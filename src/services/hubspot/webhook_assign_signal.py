# /src/services/hubspot/webhook_assign_signal.py

import asyncio
import config
from src.models.hubspot_webhooks import TicketPropertyChangeWebhookPayload
from hubspot.crm.tickets.exceptions import ApiException as TicketsApiException
from hubspot.crm.owners.exceptions import ApiException as OwnersApiException
from src.tools.hubspot.conversation.dto_requests import CreateMessageRequest
from src.services.time_service import is_business_hours
from src.services.logger_config import log_message
from src.tools.hubspot.conversation.conversation_tools import send_message_to_thread
from src.services.hubspot.messages_filter import add_conversation_to_handed_off

# --- Improved, Context-Aware Messages ---
def get_handoff_messages(owner_name: str = None):
    """Returns a dictionary of messages based on whether an owner is assigned."""
    if owner_name:
        # Case 1: On-hours, agent assigned
        return {
            "assigned": f"{owner_name} has been assigned to this conversation and will reply here shortly. I will now step back to let them assist you directly. For any new topics, please feel free to start a new chat with me."
        }
    else:
        # Case 2 & 3: On-hours (no agent) or Off-hours
        return {
            "unassigned_on_hours": "Our team has been notified and will reply here as soon as someone is available. I will now step back from this conversation. For any new topics, please feel free to start a new chat with me.",
            "unassigned_off_hours": "Our team is currently offline, but I've left them a notification. They will get back to you as soon as they are available. For any new topics, please feel free to start a new chat with me."
        }

async def process_assignment_webhook(payload: TicketPropertyChangeWebhookPayload):
    """
    Processes a 'was_handed_off' property change. Sends a context-aware message
    based on business hours and owner assignment, then disables the AI.
    """
    for event in payload:
        try:
            # Check the propertyName for each event to ensure we're acting on the right one. (Rare case since this endpoint handles assignment only)
            if event.propertyName != "was_handed_off" or event.propertyValue.lower() != "yes":
                # Ignore if not a handoff activation or not the right property
                continue 

            ticket_id = str(event.objectId)

            # --- 1. Get Ticket Details (including owner and conversation) ---
            conversation_id = None
            hubspot_owner_id = None
            try:
                ticket_response = await asyncio.to_thread(
                    config.HUBSPOT_CLIENT.crm.tickets.basic_api.get_by_id,
                    ticket_id,
                    properties=["hubspot_owner_id"],
                    associations=["conversations"]
                )

                if ticket_response.associations and "conversations" in ticket_response.associations:
                    conversation_id = ticket_response.associations["conversations"].results[0].id

                if ticket_response.properties:
                    hubspot_owner_id = ticket_response.properties.get("hubspot_owner_id")

            except (TicketsApiException, IndexError, KeyError, AttributeError) as e:
                log_message(f"Could not retrieve details for ticket {ticket_id}: {e}", log_type="warning")
                continue # Move to the next event in the list

            if not conversation_id:
                log_message(f"Ticket {ticket_id} has no associated conversation.", log_type="warning")
                continue # Move to the next event

            # --- 2. Get Owner Name if an owner is assigned ---
            owner_name = None
            if hubspot_owner_id:
                try:
                    owner_response = await asyncio.to_thread(
                        config.HUBSPOT_CLIENT.crm.owners.owners_api.get_by_id,
                        owner_id=int(hubspot_owner_id)
                    )
                    owner_name = owner_response.first_name
                except OwnersApiException as e:
                    log_message(f"API error fetching owner {hubspot_owner_id}: {e}", log_type="error")
                    # Proceed without the name, the logic will handle it gracefully
                except Exception as e:
                    log_message(f"Unexpected error fetching owner {hubspot_owner_id}: {e}", log_type="error")

            # --- 3. Determine the Scenario and Message ---
            messages = get_handoff_messages(owner_name)
            message_text = ""

            if is_business_hours():
                message_text = messages.get("assigned") if owner_name else messages.get("unassigned_on_hours")
            else:
                message_text = messages.get("unassigned_off_hours")

            # --- 4. Send the Message and Disable AI ---
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
            
            if send_result:
                await add_conversation_to_handed_off(conversation_id)

        except Exception as e:
            # Log the exception but continue the loop in case other events are valid
            log_message(f"Exception processing event in assignment webhook: {e}", log_type="error")