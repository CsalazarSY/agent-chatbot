"""Helper functions for processing HubSpot webhook events."""

# src/services/hubspot_webhook_handler.py
# pylint: disable=W0603
import asyncio
import traceback
from typing import Optional

# AutoGen imports
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import (
    BaseChatMessage,
    ToolCallExecutionEvent,
    TextMessage,
    ThoughtEvent,
)

# Models/Types
from src.tools.hubspot.conversation.dto_responses import (
    MessageDetail,
    MessageType,
    MessageDirection,
)

# HubSpot Tools used in webhook handler
from src.tools.hubspot.conversation.conversation_tools import (
    get_message_details,
    send_message_to_thread,
)

# Centralized Agent Service
from src.agents.agents_services import agent_service
from src.agents.agent_names import PLANNER_AGENT_NAME  # Import planner name

# Import HTML Formatting Service
from src.services.message_to_html import convert_message_to_html

# Import cleaner
from src.services.clean_agent_tags import clean_agent_output

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
        PROCESSING_MESSAGE_IDS.discard(
            message_id
        )  # Use discard to avoid errors if not found


async def process_agent_response(
    conversation_id: str,
    task_result: Optional[TaskResult],
    error_message: Optional[str],
):
    """
    Helper coroutine to process the agent's result, format it to HTML,
    and send the final reply (plain text and HTML) to HubSpot.
    Runs in the background after the webhook returns 200 OK.
    """
    # print(
    #     f"    -> HB Webhook Background task: Process agent response and reply for {conversation_id}"
    # )

    raw_text_reply = "Sorry, I encountered an issue and couldn't process your message."  # Default error reply
    html_reply = f"<p>{raw_text_reply}</p>"  # Default HTML error reply

    if error_message:
        print(f"!!! Agent Error for ConvID {conversation_id}: {error_message}")
        # Use default error replies
    elif task_result and task_result.messages:
        # --- Find the message BEFORE the final 'end_planner_turn' tool call --- #
        reply_message: Optional[BaseChatMessage] = None
        messages = task_result.messages
        end_turn_event_index = -1

        # Find the index of the end_planner_turn execution event
        for i in range(len(messages) - 1, -1, -1):
            current_msg = messages[i]
            if isinstance(current_msg, ToolCallExecutionEvent):
                if any(
                    exec_result.name == "end_planner_turn"
                    for exec_result in getattr(current_msg, "content", [])
                    if hasattr(exec_result, "name")
                ):
                    end_turn_event_index = i
                    break

        # Search backwards for the Planner's message
        if end_turn_event_index > 0:
            for i in range(end_turn_event_index - 1, -1, -1):
                potential_reply_msg = messages[i]
                if potential_reply_msg.source == PLANNER_AGENT_NAME and isinstance(
                    potential_reply_msg, (TextMessage, ThoughtEvent)
                ):
                    reply_message = potential_reply_msg
                    # print(
                    #     f"      - Found Planner message at index {i} (type: {type(reply_message).__name__}) before end_turn event."
                    # )
                    break

        # Fallback
        if not reply_message and messages:
            print(
                "       - WARN: Could not reliably find Planner message before end_turn event. Falling back to last message."
            )
            reply_message = messages[-1]
        # --- End of Finding Reply Message --- #

        if reply_message and hasattr(reply_message, "content"):
            raw_reply_content = reply_message.content

            # Clean up Planner's final output tags
            if isinstance(raw_reply_content, str):
                # Store the cleaned raw text first
                raw_text_reply = clean_agent_output(raw_reply_content)
                html_reply = await convert_message_to_html(raw_text_reply)
            else:
                print(
                    f"!!! Agent for ConvID {conversation_id} final message content is not a string: {type(raw_reply_content)}"
                )
                # Use default error reply
        else:
            print(
                f"!!! Agent for ConvID {conversation_id} final message has no 'content' attribute."
            )
            # Use default error reply
    else:
        print(f"!!! No task result or messages for ConvID {conversation_id}.")
        # Use default error reply

    # Send the final reply (or error message) back to the HubSpot thread
    print(
        f"      - Sending reply to HubSpot Thread {conversation_id}: Text='{raw_text_reply[:30]}...' HTML='{html_reply[:30]}...'"
    )
    try:
        # Pass text to 'message_text' and HTML to 'rich_text'
        send_result_model = await send_message_to_thread(
            thread_id=conversation_id,
            message_text=raw_text_reply,  # Send the cleaned, original text
            rich_text=html_reply,  # Send the HTML formatted version
        )

        # Check the actual type returned by the tool
        if isinstance(send_result_model, str) and send_result_model.startswith(
            "HUBSPOT_TOOL_FAILED"
        ):
            print(
                f"!!!! FAILED to send reply to HubSpot Thread {conversation_id}: {send_result_model}"
            )
        else:
            # Handle unexpected return types if necessary
            print(f"        > Reply sent to thread {conversation_id}")

    except Exception as send_exc:
        print(
            f"!!! EXCEPTION sending reply to HubSpot Thread {conversation_id}: {send_exc}"
        )
        traceback.print_exc()


async def process_incoming_hubspot_message(conversation_id: str, message_id: str):
    """
    Handles fetching message details and triggering agent processing for relevant messages.
    Runs in a background task. Ensures message_id is removed from processing set on completion.
    """
    try:
        # print(
        #     f"    -> HB Webhook Background task: Process incoming HubSpot message {message_id} for thread {conversation_id}"
        # )
        message_content = None
        is_relevant_message = False

        # 1. Fetch message details
        try:
            # print(f"        - Fetching message details ({message_id})...")
            msg_details_model = await get_message_details(
                thread_id=conversation_id, message_id=message_id
            )

            if isinstance(msg_details_model, MessageDetail):
                message_content = msg_details_model.text
                # print(
                #     f"            - Content: {message_content[:20] if message_content else ''}..."
                # )
                # print(f"            - Type: {msg_details_model.type}")
                # print(f"            - Direction: {msg_details_model.direction}")
                # print(
                #     f"            - Sender: {msg_details_model.senders[0].actorId if msg_details_model.senders else 'N/A'}"
                # )

                # 2. Check if the message is relevant for agent processing
                is_message_type = msg_details_model.type == MessageType.MESSAGE
                is_incoming = msg_details_model.direction == MessageDirection.INCOMING
                is_visitor_sender = (
                    msg_details_model.senders
                    and msg_details_model.senders[0].actorId
                    and msg_details_model.senders[0].actorId.startswith(
                        "V-"
                    )  # HubSpot visitor actor IDs start with "V-"
                )

                if is_message_type and is_incoming and is_visitor_sender:
                    is_relevant_message = True

            elif isinstance(msg_details_model, str) and msg_details_model.startswith(
                "HUBSPOT_TOOL_FAILED"
            ):
                print(f"!!! Failed to fetch message details: {msg_details_model}")
            else:
                print(
                    f"!!! Unexpected response from get_message_details: {type(msg_details_model)}"
                )

        except Exception as fetch_exc:
            print(
                f"!!! EXCEPTION fetching message details for {message_id}: {fetch_exc}"
            )
            traceback.print_exc()

        # 3. Trigger agent if relevant and content exists
        if is_relevant_message and message_content:
            # print(
            #     f"        > Triggering agent processing for thread {conversation_id}...\n\n"
            # )
            task_result, error_message, _ = await agent_service.run_chat_session(
                user_message=message_content,
                show_console=True,  # Set to False if running purely as backend service
                conversation_id=conversation_id,
            )
            await process_agent_response(conversation_id, task_result, error_message)
        else:
            print(
                f"        > Agent processing skipped for message {message_id}. (Relevant: {is_relevant_message}, Content Exists: {bool(message_content)})"
            )

    finally:
        # Ensure the message ID is removed from the processing set
        print(
            f"    <- Background task finished: ConvID={conversation_id}, MsgID={message_id}. Removing from processing set."
        )
        await remove_message_from_processing(message_id)
