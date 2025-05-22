"""
Tools for interacting with HubSpot Tickets API using the SDK.
"""

# /src/tools/hubspot/tickets/ticket_tools.py
import asyncio  # For async operations
import traceback  # For logging exceptions
from typing import Union, List, Dict, Any  # Standard typing

# HubSpot SDK imports
from hubspot.crm.tickets import (
    SimplePublicObjectInputForCreate,
    ApiException,
    PublicAssociationsForObject,
    PublicObjectId,
    AssociationSpec,
)

# Import the shared HubSpot API HUBSPOT_CLIENT instance from config
from config import HUBSPOT_CLIENT

# Import constants for associations
from src.tools.hubspot.tickets.constants import (
    AssociationCategory,
    DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,
    PipelineStage,
)

# Import DTOs for this tool
from src.tools.hubspot.tickets.dto_requests import (
    CreateTicketRequest,
    CreateSupportTicketForConversationRequest,
    CreateTicketProperties,
    AssociationToCreate,
    AssociationToObject,
    AssociationTypeSpec,
)
from src.tools.hubspot.tickets.dto_responses import (
    TicketDetailResponse,
    TicketPropertiesResponse,
    TicketAssociationDetail,
)

# Tool-specific constants
HUBSPOT_TICKET_TOOL_ERROR_PREFIX = "HUBSPOT_TICKET_TOOL_FAILED:"


def _format_error(tool_name: str, e: Exception) -> str:
    """Helper to format error messages."""
    if isinstance(e, ApiException):
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} {tool_name} - API Exception ({e.status}): {e.reason} - Body: {e.body}"
    return (
        f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} {tool_name} - Unexpected error: {str(e)}"
    )


async def create_ticket(req: CreateTicketRequest) -> Union[TicketDetailResponse, str]:
    """
    Creates a new HubSpot ticket with the given properties and associations.
    This is a general-purpose ticket creation tool.

    The `req` parameter (type `CreateTicketRequest`) should be structured as follows:
    - `properties`: An object (type `CreateTicketProperties`) containing ticket fields like:
        - `subject: str` (required)
        - `content: str` (required)
        - `hs_pipeline: Optional[str]` (defaults to '0' in DTO if not provided)
        - `hs_pipeline_stage: Optional[str]` (defaults to '2' - Waiting on Contact in DTO if not provided)
        - `hs_ticket_priority: Optional[str]`
        - ... and other custom properties allowed by `model_config = {"extra": "allow"}`.
    - `associations`: An optional list of objects (type `AssociationToCreate`) to link this ticket to other HubSpot objects.
      Each `AssociationToCreate` object should have:
        - `to`: An object (type `AssociationToObject`) with an `id: str` of the target object.
        - `types`: A list containing one or more objects (type `AssociationTypeSpec`) that define the link.
          Each `AssociationTypeSpec` requires:
            - `associationCategory: str` (e.g., "HUBSPOT_DEFINED")
            - `associationTypeId: int` (e.g., use `DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID` (which is 32) to link to a conversation/thread,
                                       or `AssociationTypeIdTicket.TICKET_TO_CONTACT.value` (which is 16) to link to a contact).

    Example for `associations` to link to a conversation with ID "12345":
    ```json
    [
        {
            "to": {"id": "12345"},
            "types": [
                {
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": 32
                }
            ]
        }
    ]
    ```

    Returns:
        A HubSpot SDK `SimplePublicObject` (the `api_response`) on successful creation,
        or an error string prefixed with `HUBSPOT_TICKET_TOOL_ERROR_PREFIX` on failure.
    """
    if not HUBSPOT_CLIENT:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_ticket - HUBSPOT_CLIENT not initialized."

    try:
        properties_payload: Dict[str, Any] = req.properties.model_dump(
            exclude_none=True
        )

        sdk_associations_payload: List[PublicAssociationsForObject] = []
        if req.associations:
            for assoc_dto in req.associations:
                sdk_to_object = PublicObjectId(id=assoc_dto.to.id)

                sdk_association_types: List[AssociationSpec] = []
                for type_spec_dto in assoc_dto.types:
                    sdk_association_types.append(
                        AssociationSpec(
                            association_category=type_spec_dto.associationCategory,
                            association_type_id=type_spec_dto.associationTypeId,
                        )
                    )

                if sdk_to_object and sdk_association_types:
                    sdk_associations_payload.append(
                        PublicAssociationsForObject(
                            to=sdk_to_object, types=sdk_association_types
                        )
                    )
                else:
                    # This case should ideally not happen if DTO validation is correct
                    print(
                        f"Warning: Skipping association due to missing 'to' or 'types' for DTO: {assoc_dto.model_dump_json()}"
                    )

        # Attempt to find and associate contact if email is provided
        # This requires the contacts API scope and might be better as a separate step or more robust logic.
        # For now, we'll keep it simple and assume if Planner wants this, it provides a contact ID directly via `associations`.
        # If contact_email is provided and no direct contact association, one could add logic here:
        # 1. Search contact by email (using HUBSPOT_CLIENT.crm.contacts.search_api.do_search)
        # 2. If found, add to associations_payload with TICKET_TO_CONTACT type_id.
        # This adds complexity and requires contacts.read scope.

        simple_public_object_input = SimplePublicObjectInputForCreate(
            properties=properties_payload,
            associations=sdk_associations_payload if sdk_associations_payload else None,
        )

        api_response = await asyncio.to_thread(
            HUBSPOT_CLIENT.crm.tickets.basic_api.create,
            simple_public_object_input_for_create=simple_public_object_input,
        )
        # Return the raw SDK response object on success
        return api_response

    except ApiException as e:
        return _format_error("create_ticket", e)
    except Exception as e:
        traceback.print_exc()  # Log the full traceback for unexpected errors
        return _format_error("create_ticket", e)


async def create_support_ticket_for_conversation(
    req: CreateSupportTicketForConversationRequest,
) -> Union[TicketDetailResponse, str]:
    """
    Creates a HubSpot support ticket specifically for an existing conversation/thread,
    with predefined pipeline settings for chatbot-initiated tickets.

    This tool simplifies ticket creation for handoff scenarios from a chatbot conversation.

    Args:
        req (CreateSupportTicketForConversationRequest): An object containing:
            - `conversation_id: str`: The ID of the HubSpot conversation/thread to associate this ticket with.
            - `subject: str`: The subject or title for the new ticket.
            - `content: str`: The main description or content for the ticket (e.g., summary of user issue).
            - `hs_ticket_priority: str`: The priority of the ticket (e.g., 'HIGH', 'MEDIUM', 'LOW').

    Returns:
        A HubSpot SDK `SimplePublicObject` on successful creation, or an error string prefixed
        with `HUBSPOT_TICKET_TOOL_ERROR_PREFIX` on failure.
    """
    if not HUBSPOT_CLIENT:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_support_ticket_for_conversation - HUBSPOT_CLIENT not initialized."

    try:
        # 1. Construct ticket properties
        ticket_properties = CreateTicketProperties(
            subject=req.subject,
            content=req.content,
            hs_pipeline=req.hs_pipeline if req.hs_pipeline is not None else "0",  # Use provided or default
            hs_pipeline_stage=req.hs_pipeline_stage if req.hs_pipeline_stage is not None else PipelineStage.WAITING_ON_CONTACT.value,  # Use provided or default
            hs_ticket_priority=req.hs_ticket_priority,
        )

        # 2. Construct association to the conversation
        association_to_conversation = AssociationToCreate(
            to=AssociationToObject(id=req.conversation_id),
            types=[
                AssociationTypeSpec(
                    associationCategory=AssociationCategory.HUBSPOT_DEFINED.value,
                    associationTypeId=DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,  # Should be 32 (Ticket to Thread)
                )
            ],
        )

        # 3. Create the full request for the generic create_ticket tool
        generic_ticket_request = CreateTicketRequest(
            properties=ticket_properties,
            associations=[association_to_conversation],
        )

        # 4. Call the generic create_ticket tool
        return await create_ticket(generic_ticket_request)

    except Exception as e:
        traceback.print_exc()  # Log the full traceback for unexpected errors
        return _format_error("create_support_ticket_for_conversation", e)
