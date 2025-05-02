''' Helper functions for processing HubSpot webhook events. '''
# src/services/hubspot_webhook_handler.py
# pylint: disable=W0603
import asyncio
import traceback
from typing import Optional

# AutoGen imports
from autogen_agentchat.base import TaskResult

# Models/Types
from src.tools.hubspot.dto_responses import MessageDetail, MessageType, MessageDirection

# HubSpot Tools used in webhook handler
from src.tools.hubspot.conversation_tools import get_message_details, send_message_to_thread

# Centralized Agent Service
from src.agents.agents_services import agent_service

# --- Globals for Webhook Deduplication ---
PROCESSING_MESSAGE_IDS = set()
message_id_lock = asyncio.Lock()

# --- Message ID Processing Helpers ---

async def is_message_being_processed(message_id: str) -> bool:
    """Checks if a message ID is currently in the processing set."""
    async with message_id_lock:
        return message_id in PROCESSING_MESSAGE_IDS

async def add_message_to_processing(message_id: str):
    """Adds a message ID to the processing set."""
    async with message_id_lock:
        PROCESSING_MESSAGE_IDS.add(message_id)

async def remove_message_from_processing(message_id: str):
    """Removes a message ID from the processing set."""
    async with message_id_lock:
        PROCESSING_MESSAGE_IDS.discard(message_id) # Use discard to avoid errors if not found

# ----------------------------------------

def clean_agent_output(raw_reply: str) -> str:
    """Clean up Planner's final output tags from the agent's response."""
    cleaned_reply = raw_reply
    if cleaned_reply.startswith("TASK COMPLETE"):
        cleaned_reply = cleaned_reply[len("TASK COMPLETE:"):].strip()
    if cleaned_reply.startswith("TASK FAILED"):
        cleaned_reply = cleaned_reply[len("TASK FAILED:"):].strip()

    cleaned_reply = cleaned_reply.replace("<UserProxyAgent>", "").strip()
    # Remove potential leading/trailing colons
    if cleaned_reply.startswith(":"):
        cleaned_reply = cleaned_reply[1:].strip()
    return cleaned_reply

# --- Webhook Processing helpers ---
async def process_agent_response(conversation_id: str, task_result: Optional[TaskResult], error_message: Optional[str]):
    """
    Helper coroutine to process the agent's result and send the final reply to HubSpot.
    Runs in the background after the webhook returns 200 OK.
    """
    print(f"    -> HB Webhook Background task: Process agent response and reply for {conversation_id}")

    final_reply_to_send = "Sorry, I encountered an issue and couldn't process your message." # Default error reply

    if error_message:
        print(f"!! Agent Error for ConvID {conversation_id}: {error_message}")
        # Use default error reply
    elif task_result and task_result.messages:
        last_agent_message = task_result.messages[-1]
        if hasattr(last_agent_message, 'content'):
            raw_reply = last_agent_message.content

            # Clean up Planner's final output tags
            if isinstance(raw_reply, str):
                cleaned_reply = clean_agent_output(raw_reply)

                if cleaned_reply: # Ensure we have something to send
                    final_reply_to_send = cleaned_reply
                else:
                    print(f"!! Agent for ConvID {conversation_id} provided an empty reply after cleaning.")
                    # Use default error reply or a specific "empty reply" message
                    final_reply_to_send = "I received your message but something went wrong when generating the response."
            else:
                print(f"!! Agent for ConvID {conversation_id} final message content is not a string: {type(raw_reply)}")
                # Use default error reply
        else:
            print(f"!! Agent for ConvID {conversation_id} final message has no 'content' attribute.")
            # Use default error reply
    else:
        print(f"!! No task result or messages for ConvID {conversation_id}.")
        # Use default error reply

    # Send the final reply (or error message) back to the HubSpot thread
    print(f"        - Sending reply to HubSpot Thread {conversation_id}: '{final_reply_to_send[:100]}...'")
    try:
        # Pass only required args + text
        # Other parameters are better as defaults
        send_result_model = await send_message_to_thread(
            thread_id=conversation_id,
            message_text=final_reply_to_send
        )

        # Check the actual type returned by the tool
        if isinstance(send_result_model, str) and send_result_model.startswith("HUBSPOT_TOOL_FAILED"):
            print(f"!!! FAILED to send reply to HubSpot Thread {conversation_id}: {send_result_model}")
        elif isinstance(send_result_model, MessageDetail): # Use the specific model type
            print(f"        - Successfully sent reply (Message ID: {send_result_model.id}) to thread {conversation_id}")
        else:
            # Handle unexpected return types if necessary
            print(f"        - Reply sent to thread {conversation_id}, but received unexpected response type: {type(send_result_model)}")

    except Exception as send_exc:
        print(f"!!! EXCEPTION sending reply to HubSpot Thread {conversation_id}: {send_exc}")
        traceback.print_exc()

async def process_incoming_hubspot_message(conversation_id: str, message_id: str):
    """
    Handles fetching message details and triggering agent processing for relevant messages.
    Runs in a background task. Ensures message_id is removed from processing set on completion.
    """
    try:
        print(f"    -> Background task: Process incoming HubSpot message {message_id} for thread {conversation_id}")
        message_content = None
        is_relevant_message = False

        # 1. Fetch message details
        try:
            print(f"        - Fetching message details ({message_id})...")
            msg_details_model = await get_message_details(thread_id=conversation_id, message_id=message_id)

            if isinstance(msg_details_model, MessageDetail):
                message_content = msg_details_model.text
                print(f"        - Fetched message content: '{message_content[:20] if message_content else ''}...' ({msg_details_model.type}, {msg_details_model.direction}) Sender: {msg_details_model.senders[0].actorId if msg_details_model.senders else 'N/A'}")

                # 2. Check if the message is relevant for agent processing
                is_message_type = msg_details_model.type == MessageType.MESSAGE
                is_incoming = msg_details_model.direction == MessageDirection.INCOMING
                is_visitor_sender = (
                    msg_details_model.senders and
                    msg_details_model.senders[0].actorId and
                    msg_details_model.senders[0].actorId.startswith("V-") # HubSpot visitor actor IDs start with "V-"
                )

                if is_message_type and is_incoming and is_visitor_sender:
                    is_relevant_message = True
                    print(f"        - Message {message_id} is RELEVANT for agent processing.")
                else:
                    print(f"        - Message {message_id} is NOT relevant. Skipping agent trigger. (Type Match: {is_message_type}, Direction Match: {is_incoming}, Sender Match: {is_visitor_sender})")

            elif isinstance(msg_details_model, str) and msg_details_model.startswith("HUBSPOT_TOOL_FAILED"):
                print(f"    !! Failed to fetch message details: {msg_details_model}")
            else:
                print(f"    !! Unexpected response from get_message_details: {type(msg_details_model)}")

        except Exception as fetch_exc:
            print(f"    !! EXCEPTION fetching message details for {message_id}: {fetch_exc}")
            traceback.print_exc()

        # 3. Trigger agent if relevant and content exists
        if is_relevant_message and message_content:
            print(f"        -> Triggering agent processing for thread {conversation_id}...\n\n")
            task_result, error_message, _ = await agent_service.run_chat_session(
                user_message=message_content,
                show_console=True,
                conversation_id=conversation_id
            )
            await process_agent_response(conversation_id, task_result, error_message)
        else:
            print(f"    -> Agent processing skipped for message {message_id}. (Relevant: {is_relevant_message}, Content Exists: {bool(message_content)})")

    finally:
        # Ensure the message ID is removed from the processing set
        print(f"    -- Background task finished for message {message_id}. Removing from processing set.")
        await remove_message_from_processing(message_id)
