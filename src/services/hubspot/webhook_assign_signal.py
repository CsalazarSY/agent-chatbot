# /src/services/hubspot/webhook_assign_signal.py

import config
import asyncio # Added for the asyncio.to_thread call
from src.services.logger_config import log_message
from src.models.hubspot_webhooks import TicketPropertyChangePayload
from src.tools.hubspot.conversation.conversation_tools import send_message_to_thread
from src.tools.hubspot.conversation.dto_requests import CreateMessageRequest
from src.services.hubspot.messages_filter import add_conversation_to_handed_off
from hubspot.crm.tickets import ApiException

HANDOFF_CONFIRMATION_MESSAGE = "A team member has been notified and will reply here shortly. I will now step back from this conversation to let them assist you directly. For any new topics, please feel free to start a new chat."
HANDOFF_FAILURE_MESSAGE = "Our team will be in touch as soon as possible"

async def process_assignment_webhook(payload: TicketPropertyChangePayload):
    """
    Processes a 'was_handed_off' property change webhook. Finds the associated
    conversation, sends a confirmation or failure message based on the property value,
    and disables the AI only when handed off successfully.
    """

    try:
        ticket_id = str(payload.objectId)
        property_value = payload.propertyValue.lower()
        conversation_id = None

        # Determine which message to send based on property value
        if property_value == "yes":
            message_text = HANDOFF_CONFIRMATION_MESSAGE
        else:
            message_text = HANDOFF_FAILURE_MESSAGE

        try:
            api_response = await asyncio.to_thread(
                config.HUBSPOT_CLIENT.crm.tickets.basic_api.get_by_id,
                ticket_id,
                associations=["conversations"]
            )

            if api_response.associations and "conversations" in api_response.associations:
                conversation_id = api_response.associations["conversations"].results[0].id

        except ApiException as e:
            log_message(f"HubSpot API error finding conversation for ticket {ticket_id}: {e}", log_type="error")
            return
        
        except (IndexError, KeyError, AttributeError):
            log_message(f"Ticket {ticket_id} has no associated conversation. Cannot send handoff message.", log_type="warning")
            return

        if not conversation_id:
            log_message(f"Could not determine conversation ID for ticket {ticket_id}.", log_type="error")
            return

        message_payload = CreateMessageRequest(
            type="MESSAGE",
            text=message_text,
            richText=f"<p>{message_text}</p>",
            senderActorId=config.HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
            channelId=config.HUBSPOT_DEFAULT_CHANNEL,
            channelAccountId=config.HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
        )
        
        send_result = await send_message_to_thread(
            thread_id=conversation_id,
            message_request_payload=message_payload
        )
        
        if isinstance(send_result, str) and send_result.startswith("HUBSPOT_TOOL_FAILED"):
            log_message(f"Failed to send handoff message to conversation {conversation_id}: {send_result}", log_type="error")

        # TODO: Is it better to handoff after moving the ticket or when we receive the webhook?
        # else:
        #     # Only add to handed off list when property value is "yes"
        #     if property_value == "yes":
        #         await add_conversation_to_handed_off(conversation_id)
            
    except Exception as e:
        log_message(f"Exception processing property change webhook: {e}", log_type="error")