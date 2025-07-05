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
from src.services.logger_config import log_message

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
    Creates a new HubSpot ticket with the given properties and associations.
    This is a general-purpose ticket creation tool.

    The `req` parameter (type `CreateTicketRequest`) should be structured as follows:
    - `properties`: An object (type `CreateTicketProperties`) containing ticket fields.
        Key fields include:
        - `subject: str` (required)
        - `content: str` (required)
        - `hs_pipeline: Optional[str]` (defaults to '0' - e.g., the first configured pipeline - in DTO if not provided)
        - `hs_pipeline_stage: Optional[str]` (defaults to '2' - e.g., a stage like 'Waiting on Contact' - in DTO if not provided)
        - `hs_ticket_priority: Optional[str]` (e.g., "HIGH", "MEDIUM", "LOW")
        - The `CreateTicketProperties` DTO uses `model_config = {"extra": "allow"}`,
          allowing any other valid HubSpot ticket properties (including custom ones)
          to be included. These should use their HubSpot internal names.
          Boolean values for properties are often sent as strings ("true" or "false").
    - `associations`: An optional list of objects (type `AssociationToCreate`) to link this ticket to other HubSpot objects.
      Each `AssociationToCreate` object should have:
        - `to`: An object (type `AssociationToObject`) with an `id: str` of the target HubSpot object (e.g., conversation ID, contact ID).
        - `types`: A list containing one or more objects (type `AssociationTypeSpec`) that define the nature of the link.
          Each `AssociationTypeSpec` requires:
            - `associationCategory: str` (e.g., "HUBSPOT_DEFINED" for standard HubSpot associations).
            - `associationTypeId: int` (A specific ID representing the type of association.
              For example, use `DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID` (which is 32) to link to a conversation/thread,
              or `AssociationTypeIdTicket.TICKET_TO_CONTACT.value` (which is 16) to link to a contact.
              It's crucial to use the correct `associationTypeId` for your specific
              HubSpot instance and the objects you are linking).

    **Example Full Payload for Creating a HubSpot Ticket:**

    The following JSON demonstrates a comprehensive payload for creating a new ticket.
    It includes linking the new ticket to an existing HubSpot conversation and populating
    various standard and custom ticket properties.

    ```json
    {
      "associations": [
        {
          "to": {
            "id": "9214555237"  // ID of the conversation to associate this ticket with
          },
          "types": [
            {
              "associationCategory": "HUBSPOT_DEFINED",
              "associationTypeId": 32 // Corresponds to DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID
            }
          ]
        }
      ],
      "properties": {
        "subject": "New Ticket Subject - From API",
        "content": "This ticket was created via the API with various custom properties populated, and associated with a conversation.",
        "hs_pipeline": "0",        // Target pipeline ID (e.g., default service pipeline)
        "hs_pipeline_stage": "1",  // Target stage ID within the pipeline (e.g., 'New')
        "hs_ticket_priority": "HIGH",
        "type_of_ticket": "Quote", // Custom property
        "use_type": "Personal",    // Custom property
        "additional_instructions_": "Please ensure all details are double-checked.", // Custom property
        "application_use_": "For an upcoming personal event.", // Custom property
        "business_category": "Amateur Sport", // Custom property (enumeration)
        "call_requested": "false",           // Custom property (boolean as string)
        "have_you_ordered_with_us_before_": "true", // Custom property
        "height_in_inches_": 2,             // Custom property (number)
        "how_did_you_find_us_": "Google Search", // Custom property
        "location": "USA",                 // Custom property
        "number_of_colours_in_design_": "1", // Custom property
        "preferred_format": "Pages",       // Custom property
        "product_group": "Tattoo",         // Custom property, drives conditional logic elsewhere
        "promotional_product_distributor_": "true", // Custom property
        "total_quantity_": 100,            // Custom property (number)
        "type_of_tattoo_": "Glitter Tattoo", // Custom property, conditional
        "what_kind_of_content_would_you_like_to_hear_about_": "Business Products and News", // Custom property
        "width_in_inches_": 2              // Custom property (number)
      }
    }
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
                    log_message(
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
        log_message(traceback.format_exc(), log_type="error")  # Log the full traceback for unexpected errors
        return _format_error("create_ticket", e)


async def create_support_ticket_for_conversation(
    conversation_id: str,
    properties: TicketCreationProperties,
) -> TicketDetailResponse | str:
    """
    Creates a HubSpot support ticket specifically for an existing conversation/thread,
    with predefined pipeline settings for chatbot-initiated tickets.

    This tool simplifies ticket creation for handoff scenarios from a chatbot conversation.

    Args:
        conversation_id: str: The ID of the HubSpot conversation/thread to associate this ticket with.
        properties (TicketCreationProperties): An object containing all ticket properties including:
            - `subject: str` (required)
            - `content: str` (required)
            - `hs_ticket_priority: str` (required)
            - `type_of_ticket: TypeOfTicketEnum` (required, defaults to INQUIRY)
            - ... and other optional custom quote fields.

    Returns:
        A HubSpot SDK `SimplePublicObject` on successful creation, or an error string prefixed
        with `HUBSPOT_TICKET_TOOL_ERROR_PREFIX` on failure.
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
            log_message(
                f"Added conversation_id: {conversation_id} to handed-off set.",
                level=3,
                prefix=">",
            )

        return ticket_creation_result

    except Exception as e:
        log_message(traceback.format_exc(), log_type="error")
        return _format_error("create_support_ticket_for_conversation", e)
