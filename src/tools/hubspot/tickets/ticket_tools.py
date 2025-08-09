"""
Tools for interacting with HubSpot Tickets API using the SDK.
"""

# /src/tools/hubspot/tickets/ticket_tools.py
import asyncio  # For async operations
import traceback  # For logging exceptions
from typing import Optional, Union, List, Dict, Any  # Standard typing

# HubSpot SDK imports
import config
from hubspot.crm.tickets import (
    SimplePublicObjectInputForCreate,
    SimplePublicObjectInput,
    ApiException,
    PublicAssociationsForObject,
    PublicObjectId,
)
from hubspot.crm.associations.v4.models import AssociationSpec

# Import the shared HubSpot API HUBSPOT_CLIENT instance from config
from config import (
    HUBSPOT_CLIENT,
    HUBSPOT_PIPELINE_ID_AICHAT,
    HUBSPOT_PIPELINE_STAGE_ID_AICHAT_OPEN,
)

# Import the new pipeline logic helper
from src.markdown_info.custom_quote.constants import YesNoEnum
from src.services.hubspot.messages_filter import add_conversation_to_handed_off
from src.services import logger_config

from src.services.time_service import is_business_hours
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
    TicketProperties,
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
    - `properties`: A `TicketCreationProperties` object containing all ticket fields. This model allows
      any valid HubSpot ticket property (standard or custom) by using its HubSpot internal name as the
      attribute name in the object.
        - **Required:** `subject`, `content`, `hs_ticket_priority`.
        - **Custom Quote Properties:** For custom quotes, all fields from the `form_data_payload`
          (e.g., `product_category`, `total_quantity_`, `sticker_format`, etc.) are passed directly
          as attributes of this `properties` object.
        - **Contact Properties:** You can include `email`, `phone`, `firstname`, and `lastname`.
    - `associations`: An optional list to link this ticket to other HubSpot objects, like a conversation.

    Returns:
        The raw `SimplePublicObject` from the HubSpot SDK on success, or an error string on failure.
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
                        prefix="!!! ",
                    )

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
    properties: TicketProperties,
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

        # Assign the AI Chatbot pipeline and "Open" stage directly from config
        # This ensures all new tickets from the AI are routed correctly.
        updated_properties.hs_pipeline = HUBSPOT_PIPELINE_ID_AICHAT
        updated_properties.hs_pipeline_stage = HUBSPOT_PIPELINE_STAGE_ID_AICHAT_OPEN

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

# --- Update Tool ---
async def update_ticket(
    ticket_id: str, properties: TicketProperties
) -> Union[TicketDetailResponse, str]:
    """
    Performs a partial update on a HubSpot ticket using a TicketProperties DTO.

    Args:
        ticket_id: The ID of the ticket to update.
        properties: A TicketProperties object. Only the fields that are not None
                    will be included in the update.

    Returns:
        A TicketDetailResponse object on success, or an error string on failure.
    """
    if not HUBSPOT_CLIENT:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} update_ticket - HUBSPOT_CLIENT not initialized."
    if not ticket_id:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} update_ticket - ticket_id is required."

    try:
        # Convert the DTO to a dictionary, crucially excluding any unset (None) values.
        properties_payload = properties.model_dump(exclude_none=True)

        if not properties_payload:
            return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} update_ticket - properties object cannot be empty."

        simple_public_object_input = SimplePublicObjectInput(properties=properties_payload)

        api_response = await asyncio.to_thread(
            HUBSPOT_CLIENT.crm.tickets.basic_api.update,
            ticket_id=ticket_id,
            simple_public_object_input=simple_public_object_input,
        )
        return api_response

    except ApiException as e:
        return _format_error("update_ticket", e)
    except Exception as e:
        logger_config.log_message(traceback.format_exc(), log_type="error")
        return _format_error("update_ticket", e)

async def move_ticket_to_human_assistance_pipeline(
    ticket_id: str,
    conversation_id: str,
    properties: Optional[TicketProperties] = None,
) -> str:
    """
    Requests human assistance. This tool intelligently handles the handoff by:
    1. Checking if it's currently business hours.
    2. Moving the ticket to the appropriate 'On Hours' or 'Off Hours' assistance stage.
    3. Updating the 'created_on_business_hours' property for metrics.
    4. Applying any additional property updates provided by the Planner (e.g., a final summary).
    5. Disabling the AI for the conversation to allow a human to take over.

    Args:
        ticket_id: The ID of the ticket requiring assistance.
        conversation_id: The ID of the conversation to disable the AI for.
        properties: An optional TicketProperties object containing any final
                    details to update on the ticket at the time of handoff.

    Returns:
        A success or failure message string.
    """
    if not ticket_id:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} ticket_id is required."
    if not conversation_id:
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} conversation_id is required."

    # 1. Determine business hours and select the correct stage
    on_business_hours = is_business_hours()
    target_stage = (
        config.HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_ON_HOURS
        if on_business_hours
        else config.HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_OFF_HOURS
    )
    
    # 2. Prepare the final properties payload for the update
    # Start with the properties provided by the Planner, or an empty DTO if none.
    final_properties_to_update = properties if properties is not None else TicketProperties()

    # 3. Add the mandatory handoff properties. This will overwrite if the Planner
    #    somehow provided them, ensuring the correct stage is always set.
    final_properties_to_update.hs_pipeline_stage = target_stage
    final_properties_to_update.created_on_business_hours = YesNoEnum.YES if on_business_hours else YesNoEnum.NO
    
    # 4. Call the generic update_ticket tool with the combined properties
    update_result = await update_ticket(ticket_id, final_properties_to_update)

    if isinstance(update_result, str) and update_result.startswith(HUBSPOT_TICKET_TOOL_ERROR_PREFIX):
        return f"{HUBSPOT_TICKET_TOOL_ERROR_PREFIX} Failed to move ticket to assistance stage: {update_result}"

    # 5. If successful, disable the AI for the conversation
    await add_conversation_to_handed_off(conversation_id)

    return "SUCCESS: Human assistance has been requested. The ticket was moved and the AI is now disabled for this conversation."

