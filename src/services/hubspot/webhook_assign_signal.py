"""Handler for HubSpot assignment webhook events."""

# src/services/hubspot/webhook_assign_signal.py
import config
from src.services.logger_config import log_message
from src.models.hubspot_webhooks import HubSpotAssignmentPayload
from src.tools.hubspot.conversation.conversation_tools import send_message_to_thread
from src.tools.hubspot.conversation.dto_requests import CreateMessageRequest
from src.services.hubspot.messages_filter import add_conversation_to_handed_off

# --- REFINED MESSAGES BASED ON SCENARIO ---

# Message for when we're outside working hours
NO_WORKING_HOURS_MESSAGE = "Our team might not be available right now. I've created a ticket so they can get back to you once they are back online. I will be disabled in this chat while you wait. For new inquiries, you can always start a new chat."

# Message for when a human agent was successfully assigned
AGENT_ASSIGNED_MESSAGE = "A team member has been assigned and will reply here shortly. I will now step back from this conversation to let them assist you directly. For any new topics, please feel free to start a new chat."

# Message for when we're in working hours but no agent is available
AGENT_NOT_AVAILABLE_MESSAGE = "Our team has been notified and will get in touch with you as soon as possible. I will be disabled in this chat while you wait. For new inquiries, you can always start a new chat."

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
        msg_scenario = payload.msg  # Get the specific scenario message
        
        # Determine message based on the msg scenario
        if msg_scenario == "no_working_hours":
            message_text = NO_WORKING_HOURS_MESSAGE
        elif msg_scenario == "agent_was_assigned":
            message_text = AGENT_ASSIGNED_MESSAGE
        elif msg_scenario == "agent_not_available":
            message_text = AGENT_NOT_AVAILABLE_MESSAGE
        else:
            # Fallback for unknown scenarios
            message_text = "Our team will get in touch with you as soon as possible. I will be disabled in this chat while you wait. For new inquiries, you can always start a new chat."

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
            # Disable the AI in this conversation REGARDLESS of assignment status.
            # This prevents the AI from re-engaging while the user is waiting for a human.
            await add_conversation_to_handed_off(conversation_id)
            
    except Exception as e:
        log_message(
            f"Exception processing assignment webhook: {e}",
            level=2,
            prefix="!!!",
            log_type="error"
        )