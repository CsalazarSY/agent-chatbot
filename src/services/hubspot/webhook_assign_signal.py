"""Handler for HubSpot assignment webhook events."""

# src/services/hubspot/webhook_assign_signal.py
import config
from src.services.logger_config import log_message
from src.models.hubspot_webhooks import HubSpotAssignmentPayload
from src.tools.hubspot.conversation.conversation_tools import send_message_to_thread
from src.tools.hubspot.conversation.dto_requests import CreateMessageRequest
from src.services.hubspot.messages_filter import add_conversation_to_handed_off

# --- REFINED MESSAGES ---

# Message for when a human agent was successfully assigned.
ASSIGN_SUCCESSFUL_MESSAGE = "A team member has been assigned and will reply here shortly. I will now be disabled in this conversation. For any new topics, please feel free to start a new chat."

# Message for when no agent was available, but the user is in the queue.
ASSIGN_UNSUCCESSFUL_MESSAGE = "Our team will get in touch with you as soon as possible. I will be disabled in this chat while you wait. For new inquiries, you can always start a new chat."

async def process_assignment_webhook(payload: HubSpotAssignmentPayload):
    """
    Processes HubSpot assignment webhook payload.
    Sends appropriate messages to the conversation based on assignment status
    and disables the AI for the conversation in all handoff scenarios.
    
    Args:
        payload: HubSpotAssignmentPayload containing assignment information
    """
    try:
        conversation_id = str(payload.hs_thread_id)  # Use hs_thread_id as conversation ID
        was_assigned = payload.was_assigned
        
        log_message(
            f"Processing assignment webhook for conversation {conversation_id}, was_assigned: {was_assigned}",
            level=1,
            prefix="ASSIGNMENT"
        )
        
        # Determine message based on assignment status
        if was_assigned:
            # Human agent was assigned
            message_text = ASSIGN_SUCCESSFUL_MESSAGE
        else:
            # No human agent available, user is queued
            message_text = ASSIGN_UNSUCCESSFUL_MESSAGE

        # Create message request
        message_payload = CreateMessageRequest(
            type="MESSAGE",
            text=message_text,
            richText=f"<p>{message_text}</p>",
            senderActorId=config.HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
            channelId=config.HUBSPOT_DEFAULT_CHANNEL,
            channelAccountId=config.HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
        )
        
        # Send message to HubSpot conversation
        send_result = await send_message_to_thread(
            thread_id=conversation_id,
            message_request_payload=message_payload
        )
        
        # Check if message was sent successfully
        if isinstance(send_result, str) and send_result.startswith("HUBSPOT_TOOL_FAILED"):
            log_message(
                f"Failed to send assignment message to conversation {conversation_id}: {send_result}",
                level=3,
                prefix="!!!",
                log_type="error"
            )
        else:
            log_message(
                f"Successfully sent assignment message to conversation {conversation_id}",
                level=3,
                prefix="SUCCESS"
            )
            
            # --- LOGIC CHANGE ---
            # Disable the AI in this conversation REGARDLESS of assignment status.
            # This prevents the AI from re-engaging while the user is waiting for a human.
            await add_conversation_to_handed_off(conversation_id)
            log_message(
                f"AI disabled for conversation {conversation_id} after handoff notification.",
                level=3,
                prefix="HANDOFF"
            )
            
    except Exception as e:
        log_message(
            f"Exception processing assignment webhook: {e}",
            level=2,
            prefix="!!!",
            log_type="error"
        )