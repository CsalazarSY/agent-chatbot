# agents/hubspot/tools/api_tools.py
import asyncio
import traceback
import json
from typing import Optional, List, Dict, Any

# Import necessary configuration constants and the client
from config import (
    hubspot_client,
    HUBSPOT_DEFAULT_CHANNEL,
    HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
    HUBSPOT_DEFAULT_SENDER_ACTOR_ID
)

# --- Helper Function for API Calls ---
async def _call_hubspot_api(request_data: Dict[str, Any]) -> Dict[str, Any] | str:
    """Internal helper to make the API call and handle common errors."""
    if not hubspot_client:
        print(" Hubspot client not initialized in config.")
        return "HUBSPOT_TOOL_FAILED: HubSpot client is not initialized."
    try:
        # Use asyncio.to_thread to run the synchronous SDK call
        # The api_request method handles JSON encoding/decoding
        response_data = await asyncio.to_thread(
            hubspot_client.api_request, # The function to run
            request_data             # The arguments for the function
        )
        # api_request usually returns the parsed JSON dictionary/list
        # or raises an ApiException on failure which is caught below.
        if response_data is None:
             # Handle cases where API might return 204 No Content or similar
             # For actions like DELETE, returning success string might be appropriate
             if request_data.get("method") == "DELETE":
                 return "HUBSPOT_TOOL_SUCCESS: Operation completed successfully (No Content)."
             else:
                 # For GET/PATCH etc., None might be unexpected, treat as potential issue or success depending on endpoint
                 print(f" Warning: HubSpot API call ({request_data.get('method')} {request_data.get('path')}) returned None.")
                 # Return None for the caller to decide how to interpret
                 return {} # Return empty dict to signify success but no data? Or raise? Let's return empty dict for now.

        # Assuming successful calls that return data return a dict or list
        if isinstance(response_data, (dict, list)):
             return response_data
        else:
             # If the response isn't dict/list, return its string representation.
             print(f" Warning: HubSpot API call returned unexpected type: {type(response_data)}. Value: {response_data}")
             return f"HUBSPOT_TOOL_SUCCESS: Operation completed. Response: {str(response_data)}"

    except Exception as e: # Catches HubSpot ApiException implicitly if it inherits Exception
        error_message = f"HUBSPOT_TOOL_FAILED: Error communicating with HubSpot API: {e}"
        print(f"\n Error calling HubSpot API ({request_data.get('method')} {request_data.get('path')}): {e}")
        # Try to extract specific HubSpot error details if available
        # This depends heavily on the structure of the exception 'e' from the SDK
        if hasattr(e, 'body') and e.body:
             try:
                 error_body = json.loads(e.body)
                 error_message += f" Details: {error_body.get('message', 'N/A')}"
             except json.JSONDecodeError:
                 error_message += f" Raw Body: {e.body}"
        elif hasattr(e, 'status') and hasattr(e, 'reason'):
             error_message += f" Status: {e.status} Reason: {e.reason}"

        return error_message

# --- Tool Function Definitions ---

async def send_message_to_thread(
    thread_id: str,
    message_text: str,
    channel_id: Optional[str] = None,
    channel_account_id: Optional[str] = None,
    sender_actor_id: Optional[str] = None,
    message_type: str = "MESSAGE" # Allow explicit type override
) -> str:
    """
    (Endpoint 14) Sends a message or comment to a HubSpot conversation thread.

    Args:
        thread_id (str): The HubSpot conversation thread ID.
        message_text (str): The content of the message/comment to send.
        channel_id (Optional[str]): The channel ID (e.g., '1000' for chat). Defaults to configured HUBSPOT_DEFAULT_CHANNEL.
        channel_account_id (Optional[str]): The specific channel account ID (e.g., chatflow ID). Defaults to configured HUBSPOT_DEFAULT_CHANNEL_ACCOUNT.
        sender_actor_id (Optional[str]): The HubSpot Actor ID (e.g., "A-12345") posting the message/comment. Defaults to configured HUBSPOT_DEFAULT_SENDER_ACTOR_ID.
        message_type (str): Type of message ('MESSAGE' or 'COMMENT'). Defaults to 'MESSAGE'. Tool *used* to infer from text, now requires explicit type or defaults to MESSAGE.

    Returns:
        str: A success or failure message string (e.g., "HUBSPOT_TOOL_SUCCESS:..." or "HUBSPOT_TOOL_FAILED:...").
    """
    print(f"\n--- Running Tool: send_message_to_thread (New Impl) ---")

    # Apply defaults from config if args are None
    final_channel_id = channel_id or HUBSPOT_DEFAULT_CHANNEL
    final_channel_account_id = channel_account_id or HUBSPOT_DEFAULT_CHANNEL_ACCOUNT
    final_sender_actor_id = sender_actor_id or HUBSPOT_DEFAULT_SENDER_ACTOR_ID

    # --- Validate necessary inputs ---
    if not thread_id or not isinstance(thread_id, str) or thread_id.lower() == 'unknown':
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot thread ID was not provided."
    if not final_channel_id or not isinstance(final_channel_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel ID was not provided."
    if not final_channel_account_id or not isinstance(final_channel_account_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel account ID was not provided."
    if not final_sender_actor_id or not isinstance(final_sender_actor_id, str):
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot sender actor ID was not provided."
    if not message_text or not isinstance(message_text, str):
        return "HUBSPOT_TOOL_FAILED: Valid message text was not provided."
    if message_type not in ["MESSAGE", "COMMENT"]:
         return f"HUBSPOT_TOOL_FAILED: Invalid message_type '{message_type}'. Must be 'MESSAGE' or 'COMMENT'."

    # --- Build call parameters ---
    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    payload = {
        "type": message_type,
        "text": message_text,
        "senderActorId": final_sender_actor_id,
        "channelId": final_channel_id,
        "channelAccountId": final_channel_account_id,
        "recipients": [{"actorId": final_sender_actor_id}] # Simplistic recipient - VERIFY IF THIS IS VALID
    }
    request_data = {
        "method": "POST",
        "path": api_path,
        "body": payload
    }

    result = await _call_hubspot_api(request_data)

    if isinstance(result, str) and result.startswith("HUBSPOT_TOOL_FAILED"):
        return result
    else:
        # API call succeeded (returned dict, list, or non-failure string)
        # The send message endpoint returns the created message object on 201
        return f"HUBSPOT_TOOL_SUCCESS: Message successfully sent to thread {thread_id}." # Simplified success

async def get_thread_details(thread_id: str, association: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 6) Retrieves details for a single conversation thread.

    Args:
        thread_id (str): The unique ID of the thread.
        association (Optional[str]): Specify an association type (e.g., 'TICKET') to include associated object IDs.

    Returns:
        Dict[str, Any] | str: A dictionary containing thread details on success, or an error string.
    """
    print(f"\n--- Running Tool: get_thread_details ---")
    if not thread_id:
        return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if association:
        query_params['association'] = association
    # `archived` and `property` params omitted for simplicity, add if needed

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)

async def get_thread_messages(thread_id: str, limit: Optional[int] = None, after: Optional[str] = None, sort: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 10) Retrieves message history for a thread.

    Args:
        thread_id (str): The unique ID of the thread.
        limit (Optional[int]): Maximum number of messages per page.
        after (Optional[str]): Paging cursor for the next page.
        sort (Optional[str]): Sort direction ('createdAt' or '-createdAt'). Default is '-createdAt'.

    Returns:
        Dict[str, Any] | str: A dictionary containing message results and paging info, or an error string.
    """
    print(f"\n--- Running Tool: get_thread_messages ---")
    if not thread_id:
        return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    if sort: query_params['sort'] = sort
    # `archived` and `property` params omitted for simplicity

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)


async def list_threads(limit: Optional[int] = None, after: Optional[str] = None, thread_status: Optional[str] = None, inbox_id: Optional[str] = None, associated_contact_id: Optional[str] = None, sort: Optional[str] = None, association: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 12) Retrieves a list of conversation threads with filtering and pagination.

    Args:
        limit (Optional[int]): Max results per page.
        after (Optional[str]): Paging cursor.
        thread_status (Optional[str]): Filter by status ('OPEN' or 'CLOSED'). Required if using associated_contact_id.
        inbox_id (Optional[str]): Filter by inbox ID. Cannot be used with associated_contact_id.
        associated_contact_id (Optional[str]): Filter by contact ID. Cannot be used with inbox_id. Requires thread_status.
        sort (Optional[str]): Sort order ('id', 'latestMessageTimestamp', prefix with '-' for desc only when using associated_contact_id).
        association (Optional[str]): Include associations (e.g., 'TICKET').

    Returns:
        Dict[str, Any] | str: A dictionary containing thread results and paging info, or an error string.
    """
    print(f"\n--- Running Tool: list_threads ---")

    # Parameter validation
    if associated_contact_id and inbox_id:
         return "HUBSPOT_TOOL_FAILED: Cannot use both 'inbox_id' and 'associated_contact_id' filters simultaneously."
    if associated_contact_id and not thread_status:
         return "HUBSPOT_TOOL_FAILED: 'thread_status' is required when filtering by 'associated_contact_id'."
    if sort == 'latestMessageTimestamp': # Postman notes require latestMessageTimestampAfter - this seems complex, maybe simplify?
         # For now, let's just pass the sort param if provided, API might handle it or error out.
         pass

    api_path = "/conversations/v3/conversations/threads"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    if thread_status: query_params['threadStatus'] = thread_status
    if inbox_id: query_params['inboxId'] = inbox_id # Assuming single ID for simplicity, API allows array
    if associated_contact_id: query_params['associatedContactId'] = associated_contact_id
    if sort: query_params['sort'] = sort # Assuming single sort for simplicity, API allows array
    if association: query_params['association'] = association
    # Other params like archived, property, latestMessageTimestampAfter omitted

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)


async def update_thread(thread_id: str, status: Optional[str] = None, archived: Optional[bool] = None, is_currently_archived: bool = False) -> Dict[str, Any] | str:
    """
    (Endpoint 15) Updates a thread's status or restores it from archive.

    Args:
        thread_id (str): The ID of the thread to update.
        status (Optional[str]): New status ('OPEN' or 'CLOSED').
        archived (Optional[bool]): Set to False to restore an archived thread.
        is_currently_archived (bool): Set to True if restoring (sets required query param). Defaults to False.

    Returns:
        Dict[str, Any] | str: The updated thread details on success, or an error string.
    """
    print(f"\n--- Running Tool: update_thread ---")
    if not thread_id:
        return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if status is None and archived is None:
        return "HUBSPOT_TOOL_FAILED: Either 'status' or 'archived' must be provided to update."
    if status is not None and status not in ["OPEN", "CLOSED"]:
        return f"HUBSPOT_TOOL_FAILED: Invalid status '{status}'. Must be 'OPEN' or 'CLOSED'."
    if archived is not None and not isinstance(archived, bool):
         return f"HUBSPOT_TOOL_FAILED: 'archived' must be a boolean (true/false)."
    if archived is False and not is_currently_archived:
         return f"HUBSPOT_TOOL_FAILED: To restore a thread (set archived=false), you must also set 'is_currently_archived=true'."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if is_currently_archived:
        query_params['archived'] = 'true' # Query param indicates the *current* state when modifying archive status

    payload = {}
    if status is not None:
        payload['status'] = status
    if archived is not None:
        payload['archived'] = archived

    request_data = {
        "method": "PATCH",
        "path": api_path,
        "query_params": query_params,
        "body": payload
    }
    return await _call_hubspot_api(request_data)

async def archive_thread(thread_id: str) -> str:
    """
    (Endpoint 16) Archives a single conversation thread.

    Args:
        thread_id (str): The ID of the thread to archive.

    Returns:
        str: A success or failure message string.
    """
    print(f"\n--- Running Tool: archive_thread ---")
    if not thread_id:
        return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    request_data = {
        "method": "DELETE",
        "path": api_path
    }
    # DELETE often returns 204 No Content, helper handles this
    result = await _call_hubspot_api(request_data)
    # The helper returns a specific success string for DELETE 204
    if isinstance(result, str) and result.startswith("HUBSPOT_TOOL_"):
         return result
    else: # Should not happen if helper logic is correct
         print(f" Warning: Unexpected result type from _call_hubspot_api for DELETE: {type(result)}")
         return f"HUBSPOT_TOOL_FAILED: Unexpected result type: {type(result).__name__}"


async def get_actor_details(actor_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 1) Retrieves details for a specific actor.

    Args:
        actor_id (str): The unique ID of the actor.

    Returns:
        Dict[str, Any] | str: A dictionary containing actor details on success, or an error string.
    """
    print(f"\n--- Running Tool: get_actor_details ---")
    if not actor_id:
        return "HUBSPOT_TOOL_FAILED: actor_id is required."

    api_path = f"/conversations/v3/conversations/actors/{actor_id}"
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data)

async def get_actors_batch(actor_ids: List[str]) -> Dict[str, Any] | str:
    """
    (Endpoint 13) Retrieves details for multiple actors in a batch.

    Args:
        actor_ids (List[str]): A list of actor IDs to retrieve.

    Returns:
        Dict[str, Any] | str: A dictionary containing batch results (potentially including errors for specific IDs), or a general error string.
    """
    print(f"\n--- Running Tool: get_actors_batch ---")
    if not actor_ids or not isinstance(actor_ids, list):
        return "HUBSPOT_TOOL_FAILED: actor_ids must be a non-empty list of strings."

    api_path = "/conversations/v3/conversations/actors/batch/read"
    payload = {"inputs": actor_ids}
    request_data = {
        "method": "POST",
        "path": api_path,
        "body": payload
    }
    # This endpoint can return 200 or 207 (Multi-Status) on success
    return await _call_hubspot_api(request_data)


async def list_inboxes(limit: Optional[int] = None, after: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 9) Retrieves a list of conversation inboxes.

    Args:
        limit (Optional[int]): Maximum results per page.
        after (Optional[str]): Paging cursor.

    Returns:
        Dict[str, Any] | str: A dictionary containing inbox results and paging info, or an error string.
    """
    print(f"\n--- Running Tool: list_inboxes ---")
    api_path = "/conversations/v3/conversations/inboxes"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    # Other params omitted for simplicity

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)

async def get_inbox_details(inbox_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 4) Retrieves details for a specific inbox.

    Args:
        inbox_id (str): The unique ID of the inbox.

    Returns:
        Dict[str, Any] | str: A dictionary containing inbox details, or an error string.
    """
    print(f"\n--- Running Tool: get_inbox_details ---")
    if not inbox_id:
        return "HUBSPOT_TOOL_FAILED: inbox_id is required."

    api_path = f"/conversations/v3/conversations/inboxes/{inbox_id}"
    # `archived` param omitted for simplicity
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data)

async def list_channels(limit: Optional[int] = None, after: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 8) Retrieves a list of channels connected to inboxes.

    Args:
        limit (Optional[int]): Maximum results per page.
        after (Optional[str]): Paging cursor.

    Returns:
        Dict[str, Any] | str: A dictionary containing channel results and paging info, or an error string.
    """
    print(f"\n--- Running Tool: list_channels ---")
    api_path = "/conversations/v3/conversations/channels"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    # Other params omitted

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)

async def get_channel_details(channel_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 3) Retrieves details for a specific channel.

    Args:
        channel_id (str): The unique ID of the channel.

    Returns:
        Dict[str, Any] | str: A dictionary containing channel details, or an error string.
    """
    print(f"\n--- Running Tool: get_channel_details ---")
    if not channel_id:
        return "HUBSPOT_TOOL_FAILED: channel_id is required."

    api_path = f"/conversations/v3/conversations/channels/{channel_id}"
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data)


async def list_channel_accounts(channel_id: Optional[str] = None, inbox_id: Optional[str] = None, limit: Optional[int] = None, after: Optional[str] = None) -> Dict[str, Any] | str:
    """
    (Endpoint 7) Retrieves a list of channel accounts (instances of channels).

    Args:
        channel_id (Optional[str]): Filter by channel ID.
        inbox_id (Optional[str]): Filter by inbox ID.
        limit (Optional[int]): Maximum results per page.
        after (Optional[str]): Paging cursor.

    Returns:
        Dict[str, Any] | str: A dictionary containing channel account results and paging info, or an error string.
    """
    print(f"\n--- Running Tool: list_channel_accounts ---")
    api_path = "/conversations/v3/conversations/channel-accounts"
    query_params = {}
    if channel_id: query_params['channelId'] = channel_id # API allows array, simplifying to single
    if inbox_id: query_params['inboxId'] = inbox_id # API allows array, simplifying to single
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    # Other params omitted

    request_data = {
        "method": "GET",
        "path": api_path,
        "query_params": query_params
    }
    return await _call_hubspot_api(request_data)

async def get_channel_account_details(channel_account_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 2) Retrieves details for a specific channel account instance.

    Args:
        channel_account_id (str): The unique ID of the channel account.

    Returns:
        Dict[str, Any] | str: A dictionary containing channel account details, or an error string.
    """
    print(f"\n--- Running Tool: get_channel_account_details ---")
    if not channel_account_id:
        return "HUBSPOT_TOOL_FAILED: channel_account_id is required."

    api_path = f"/conversations/v3/conversations/channel-accounts/{channel_account_id}"
    # `archived` param omitted for simplicity
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data)


async def get_message_details(thread_id: str, message_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 5) Retrieves a specific message within a given thread.

    Args:
        thread_id (str): The unique ID of the thread.
        message_id (str): The unique ID of the message.

    Returns:
        Dict[str, Any] | str: A dictionary containing message details, or an error string.
    """
    print(f"\n--- Running Tool: get_message_details ---")
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if not message_id: return "HUBSPOT_TOOL_FAILED: message_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}"
    # `property` param omitted
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data)

async def get_original_message_content(thread_id: str, message_id: str) -> Dict[str, Any] | str:
    """
    (Endpoint 11) Retrieves the original text/richText content of a potentially truncated message.

    Args:
        thread_id (str): The unique ID of the thread.
        message_id (str): The unique ID of the message.

    Returns:
        Dict[str, Any] | str: A dictionary with 'text' and 'richText' keys, or an error string.
    """
    print(f"\n--- Running Tool: get_original_message_content ---")
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if not message_id: return "HUBSPOT_TOOL_FAILED: message_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}/original-content"
    # `property` param omitted
    request_data = {
        "method": "GET",
        "path": api_path
    }
    return await _call_hubspot_api(request_data) 