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
)
from hubspot.crm.associations.v4.models import AssociationSpec

# Import the shared HubSpot API HUBSPOT_CLIENT instance from config
from config import HUBSPOT_CLIENT

# Import the new pipeline logic helper
from src.services.hubspot.determine_pipeline import determine_pipeline_and_stage
from src.services.hubspot.messages_filter import add_conversation_to_handed_off
from src.services import logger_config

from src.tools.hubspot.tickets.constants import (
    AssociationCategory,
    TypeOfTicketEnum,
    DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,
)

# Import DTOs for this tool
from src.tools.hubspot.tickets.dto_requests import (
    CreateTicketRequest,
    AssociationToCreate,
    AssociationToObject,
    AssociationTypeSpec,
    TicketCreationProperties,
)
from src.tools.hubspot.tickets.dto_responses import (
    TicketDetailResponse,
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
    Creates a new HubSpot ticket with the given properties and optional associations.
    This is a general-purpose ticket creation tool.

    The `req` parameter is a `CreateTicketRequest` object with two main parts:
    - `properties`: A `TicketCreationProperties` object containing ticket fields. This model allows
      any valid HubSpot ticket property (standard or custom) using its HubSpot internal name.
        - **Required:** `subject`, `content`, `hs_ticket_priority`.
        - **Custom Properties:** Any other fields like `product_group`, `total_quantity_`, etc.
        - **Contact Properties:** You can include `email` and `phone` here; the system will handle them.
    - `associations`: An optional list to link this ticket to other HubSpot objects, like a conversation.

    **Example Payload Structure:**
    ```json
    {
      "properties": {
        "subject": "Inquiry about custom stickers",
        "content": "User needs a quote for 500 custom stickers.",
        "hs_ticket_priority": "MEDIUM",
        "type_of_ticket": "Quote",
        "email": "customer@example.com",
        "product_group": "Stickers",
        "total_quantity_": 500
      },
      "associations": [
        {
          "to": { "id": "987654321" },
          "types": [{ "associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 32 }]
        }
      ]
    }
    ```

    Returns:
        A `TicketDetailResponse` object on success, or an error string on failure.
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
                    logger_config.log_message(
                        f"Skipping association due to missing 'to' or 'types' for DTO: {assoc_dto.model_dump_json()}",
                        level=3,
                        log_type="warning",
                        prefix="Warning:",
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
        logger_config.log_message(traceback.format_exc(), log_type="error")  # Log the full traceback for unexpected errors
        return _format_error("create_ticket", e)


async def create_support_ticket_for_conversation(
    conversation_id: str,
    properties: TicketCreationProperties,
) -> TicketDetailResponse | str:
    """
    Creates and associates a HubSpot support ticket with an existing conversation.

    This tool is a specialized wrapper around the generic `create_ticket` function.
    It automatically determines the correct pipeline and stage for the new ticket
    based on the provided properties, simplifying the process for the Planner.

    Args:
        conversation_id: The ID of the HubSpot conversation to link the ticket to.
        properties: A `TicketCreationProperties` object containing all ticket details
                    (e.g., subject, content, priority, and any custom fields).
    """
    if not HUBSPOT_CLIENT:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_support_ticket_for_conversation - HUBSPOT_CLIENT not initialized."

    try:
        # Make a mutable copy of the properties to potentially modify pipeline/stage
        updated_properties = properties.model_copy(deep=True)

        # Determine the pipeline and stage for the ticket
        try:
            pipeline_id, stage_id = determine_pipeline_and_stage(properties)
        except Exception as determination_exc:
            # If determination fails, return an error instead of proceeding
            return f"TOOL_LOGIC_ERROR: Failed to determine pipeline/stage. Details: {determination_exc}"

        # Assign the determined pipeline and stage to the properties object
        # This ensures they are included in the request to HubSpot
        updated_properties.hs_pipeline = pipeline_id
        updated_properties.hs_pipeline_stage = stage_id

        # Ensure critical fields are present (Pydantic model validation already does this on instantiation)
        # but an explicit check before calling the generic tool adds a layer of safety.
        if not updated_properties.subject:
            return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_support_ticket_for_conversation - 'subject' is missing."
        if not updated_properties.content:
            return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_support_ticket_for_conversation - 'content' is missing."
        if not updated_properties.hs_ticket_priority:
            return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} create_support_ticket_for_conversation - 'hs_ticket_priority' is missing."
        # type_of_ticket has a default in the DTO, so it should always be present.

        # 1. Construct association to the conversation
        association_to_conversation = AssociationToCreate(
            to=AssociationToObject(id=conversation_id),
            types=[
                AssociationTypeSpec(
                    associationCategory=AssociationCategory.HUBSPOT_DEFINED.value,
                    associationTypeId=DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,
                )
            ],
        )

        # 2. Create the full request for the generic create_ticket tool
        generic_ticket_request = CreateTicketRequest(
            properties=updated_properties,
            associations=[association_to_conversation],
        )

        # 3. Call the generic create_ticket tool
        ticket_creation_result = await create_ticket(generic_ticket_request)

        # If ticket creation was successful (i.e., not an error string) and
        # the ticket type is 'Issue', add conversation_id to handed-off set.
        # We check if it's NOT an error string because create_ticket returns SimplePublicObject on success.
        if (
            not isinstance(ticket_creation_result, str)
            and properties.type_of_ticket == TypeOfTicketEnum.ISSUE
        ):
            await add_conversation_to_handed_off(conversation_id)
            logger_config.log_message(
                f"Added conversation_id: {conversation_id} to handed-off set.",
                level=3,
                prefix=">",
            )

        return ticket_creation_result

    except Exception as e:
        logger_config.log_message(traceback.format_exc(), log_type="error")
        return _format_error("create_support_ticket_for_conversation", e)
