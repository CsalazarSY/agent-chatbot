# agents/hubspot/tools/handoff.py

import asyncio # Import asyncio
import traceback
from typing import Optional

from config import hubspot_client, HUBSPOT_DEFAULT_CHANNEL, HUBSPOT_DEFAULT_CHANNEL_ACCOUNT, HUBSPOT_DEFAULT_SENDER_ACTOR_ID

# --- Tool Function Definition ---
async def send_message_to_thread(
    thread_id: str,
    message_text: str,  
    channel_id: Optional[str] = HUBSPOT_DEFAULT_CHANNEL,
    channel_account_id: Optional[str] = HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
    sender_actor_id: Optional[str] = HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
    ) -> str:
    """
    Sends a message or comment to a HubSpot conversation thread using the API.
    If the message_text contains "HANDOFF" (case-insensitive), it sends the message
    as an internal COMMENT, otherwise it sends it as a regular MESSAGE.

    Args:
        thread_id: The HubSpot conversation thread ID.
        message_text: The content of the message/comment to send.
        channel_id: Optional. The channel ID (e.g., '1000' for chat). Uses default if None.
        channel_account_id: Optional. The specific channel account ID (e.g., chatflow ID). Uses default if None.
        sender_actor_id: Optional. The HubSpot Actor ID (e.g., "A-12345") posting the message/comment. Uses default if None.

    Returns:
        A success or failure message string (e.g., "Message successfully sent..." or "HUBSPOT_TOOL_FAILED:...").
    """
    print(f"\n--- Running Tool: send_message_to_thread ---")
    print(f"    >>> Channel ID: {channel_id}")
    print(f"    >>> Account ID: {channel_account_id}")
    print(f"    >>> Thread ID: {thread_id}")
    print(f"    >>> Actor ID: {sender_actor_id}")

    # --- Validate necessary inputs ---
    if not hubspot_client:
        return "HUBSPOT_TOOL_FAILED: HubSpot client is not initialized."
    if not thread_id or not isinstance(thread_id, str) or thread_id.lower() == 'unknown':
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot thread ID was not provided."
    if not channel_id or not isinstance(channel_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel ID was not provided."
    if not channel_account_id or not isinstance(channel_account_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel account ID was not provided."
    if not sender_actor_id or not isinstance(sender_actor_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot sender actor ID was not provided."
    if not sender_actor_id.startswith("A-"):
        print("  Warning: sender_actor_id might not be a valid Agent Actor ID.")
    if not message_text or not isinstance(message_text, str):
        return "HUBSPOT_TOOL_FAILED: Valid message text was not provided."

    # --- Determine Message Type (MESSAGE or COMMENT) ---
    message_type = "MESSAGE"  # Default to visible message
    if "HANDOFF" in message_text.upper() or "COMMENT" in message_text.upper():
        message_type = "COMMENT"

    # --- Build call parameters ---
    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    payload = {
        "type": message_type,
        "text": message_text,
        "senderActorId": sender_actor_id,
        "channelId": channel_id,
        "channelAccountId": channel_account_id,
    }
    request_data = {
        "method": "POST",
        "path": api_path,
        "body": payload
    }

    try:
        # Use asyncio.to_thread to run the synchronous SDK call in the event loop
        await asyncio.to_thread(
            hubspot_client.api_request, # The function to run
            request_data # The arguments for the function
        )
        print(f"--- Tool: send_message_to_thread - finished (Success) ---\n")
        return f"HUBSPOT_TOOL_SUCCESS: Message successfully sent to thread {thread_id}."

    except Exception as e: #
        print(f"\n Error calling HubSpot API: {e}")
        traceback.print_exc()
        print(f"--- Tool: send_message_to_thread - finished (Error) ---\n")
        return f"HUBSPOT_TOOL_FAILED: Error communicating with HubSpot API: {e}"
