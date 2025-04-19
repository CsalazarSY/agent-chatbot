import os
import asyncio
import traceback
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from hubspot import HubSpot

# Import utilities
from utils import hubspot_config, create_hubspot_client

# Load environment variables
load_dotenv()

# --- HubSpot Client Context --- #
@dataclass
class HubSpotContext:
    """Context holding the initialized HubSpot client and config."""
    hubspot_client: Optional[HubSpot]
    config: dict

@asynccontextmanager
async def hubspot_lifespan(server: FastMCP) -> AsyncIterator[HubSpotContext]:
    """Manages the HubSpot client lifecycle."""
    client: Optional[HubSpot] = None
    cfg = hubspot_config
    if cfg.get("api_token"):
        try:
            client = create_hubspot_client(cfg["api_token"])
        except ValueError as e:
            # print(f"HubSpot Lifespan Error: {e}")
            pass # Client remains None, tools should handle this
    else:
        # print("HubSpot Lifespan Warning: HUBSPOT_API_TOKEN not found. HubSpot tools will fail.")
        pass

    try:
        yield HubSpotContext(hubspot_client=client, config=cfg)
    finally:
        # No explicit cleanup needed for the HubSpot client instance
        # print("HubSpot Lifespan: Shutdown complete.")
        pass

# --- Initialize FastMCP Server --- #
mcp = FastMCP(
    "mcp-hubspot",
    description="MCP server for interacting with HubSpot conversations.",
    lifespan=hubspot_lifespan,
    host=os.getenv("HOST", "0.0.0.0"), # For SSE
    port=int(os.getenv("PORT", "8051")) # Default port 8051 for HubSpot server
)

# --- Tool Definitions --- #

@mcp.tool(name="send_message_to_thread")
async def hubspot_send_message(
    ctx: Context,
    thread_id: str,
    message_text: str,
    channel_id: Optional[str] = None,
    channel_account_id: Optional[str] = None,
    sender_actor_id: Optional[str] = None,
) -> str | Dict[str, Any]: # Allow returning dict on success
    """(Endpoint 14) Sends a message or comment to a HubSpot conversation thread.

    If the message_text contains 'HANDOFF' or 'COMMENT' (case-insensitive), it sends the message
    as an internal COMMENT, otherwise it sends it as a regular MESSAGE.

    Args:
        ctx: The MCP server context containing the HubSpot client and config.
        thread_id: The HubSpot conversation thread ID.
        message_text: The content of the message/comment to send.
        channel_id: Optional. The channel ID (e.g., '1000' for chat). Uses default from env if None.
        channel_account_id: Optional. The specific channel account ID (e.g., chatflow ID). Uses default from env if None.
        sender_actor_id: Optional. The HubSpot Actor ID (e.g., "A-12345") posting the message/comment. Uses default from env if None.

    Returns:
        A dictionary containing the created message details on success, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    config = hubspot_context.config

    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client is not initialized."

    # Use provided args or fall back to config defaults
    final_channel_id = channel_id or config.get("default_channel")
    final_channel_account_id = channel_account_id or config.get("default_channel_account")
    final_sender_actor_id = sender_actor_id or config.get("default_sender_actor_id")

    # --- Input Validation ---
    if not thread_id or not isinstance(thread_id, str) or thread_id.lower() == 'unknown': return "HUBSPOT_TOOL_FAILED: Valid HubSpot thread ID was not provided."
    if not final_channel_id or not isinstance(final_channel_id, str): return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel ID was not provided."
    if not final_channel_account_id or not isinstance(final_channel_account_id, str): return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel account ID was not provided."
    if not final_sender_actor_id or not isinstance(final_sender_actor_id, str): return "HUBSPOT_TOOL_FAILED: Valid HubSpot sender actor ID was not provided."
    if not final_sender_actor_id.startswith("A-"): pass # Just a warning, proceed
    if not message_text or not isinstance(message_text, str): return "HUBSPOT_TOOL_FAILED: Valid message text was not provided."

    # --- Determine Message Type ---
    message_type = "MESSAGE"
    if "HANDOFF" in message_text.upper() or "COMMENT" in message_text.upper():
        message_type = "COMMENT"

    # --- API Call ---
    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    payload = {
        "type": message_type,
        "text": message_text,
        "senderActorId": final_sender_actor_id,
        "channelId": final_channel_id,
        "channelAccountId": final_channel_account_id
    }
    request_data = { "method": "POST", "path": api_path, "body": payload }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None:
            # Unexpected for a POST/create, but handle defensively
            return f"HUBSPOT_TOOL_FAILED: unexpected response from API call, we dont have enough information to proceed."

        # Handle raw Response object
        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data # Return created message details
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} sending message. Body: {body_str}"

        # Handle already parsed dict/list
        elif isinstance(response, dict): return response # Return created message details

        # Fallback for other unexpected types
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format sending message. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} sending message. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error sending message: {type(e).__name__} - {e}"

# --- Added Tools Below ---

@mcp.tool()
async def hubspot_get_thread_details(
    ctx: Context,
    thread_id: str,
    association: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 6) Retrieves details for a single conversation thread.

    Args:
        ctx: The MCP server context.
        thread_id: The unique ID of the thread.
        association: Optional. Specify an association type (e.g., 'TICKET') to include associated object IDs.

    Returns:
        A dictionary containing thread details on success, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if association: query_params['association'] = association

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting thread details. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting thread details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting thread details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting thread details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_thread_messages(
    ctx: Context,
    thread_id: str,
    limit: Optional[int] = None,
    after: Optional[str] = None,
    sort: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 10) Retrieves message history for a thread.

    Args:
        ctx: The MCP server context.
        thread_id: The unique ID of the thread.
        limit: Optional. Maximum number of messages per page.
        after: Optional. Paging cursor for the next page.
        sort: Optional. Sort direction ('createdAt' or '-createdAt'). Default is '-createdAt'.

    Returns:
        A dictionary containing message results and paging info, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    if sort: query_params['sort'] = sort

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data # API returns a dict like {"results": [], "paging": ...}
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting thread messages. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting thread messages. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting thread messages. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting thread messages: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_list_threads(
    ctx: Context,
    limit: Optional[int] = None,
    after: Optional[str] = None,
    thread_status: Optional[str] = None,
    inbox_id: Optional[str] = None,
    associated_contact_id: Optional[str] = None,
    sort: Optional[str] = None,
    association: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 12) Retrieves a list of conversation threads with filtering and pagination.

    Args:
        ctx: The MCP server context.
        limit: Optional. Max results per page.
        after: Optional. Paging cursor.
        thread_status: Optional. Filter by status ('OPEN' or 'CLOSED'). Required if using associated_contact_id.
        inbox_id: Optional. Filter by inbox ID. Cannot be used with associated_contact_id.
        associated_contact_id: Optional. Filter by contact ID. Cannot be used with inbox_id. Requires thread_status.
        sort: Optional. Sort order ('id', 'latestMessageTimestamp', etc.).
        association: Optional. Include associations (e.g., 'TICKET').

    Returns:
        A dictionary containing thread results and paging info, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."

    # Validation from original tool
    if associated_contact_id and inbox_id: return "HUBSPOT_TOOL_FAILED: Cannot use both 'inbox_id' and 'associated_contact_id'."
    if associated_contact_id and not thread_status: return "HUBSPOT_TOOL_FAILED: 'thread_status' is required when filtering by 'associated_contact_id'."

    api_path = "/conversations/v3/conversations/threads"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after
    if thread_status: query_params['threadStatus'] = thread_status
    if inbox_id: query_params['inboxId'] = inbox_id
    if associated_contact_id: query_params['associatedContactId'] = associated_contact_id
    if sort: query_params['sort'] = sort
    if association: query_params['association'] = association

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} listing threads. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format listing threads. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} listing threads. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error listing threads: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_update_thread(
    ctx: Context,
    thread_id: str,
    status: Optional[str] = None,
    archived: Optional[bool] = None,
    is_currently_archived: bool = False
) -> Dict[str, Any] | str:
    """(Endpoint 15) Updates a thread's status or restores it from archive.

    Args:
        ctx: The MCP server context.
        thread_id: The ID of the thread to update.
        status: Optional. New status ('OPEN' or 'CLOSED').
        archived: Optional. Set to False to restore an archived thread.
        is_currently_archived: Set to True if restoring (sets required query param). Defaults to False.

    Returns:
        The updated thread details on success, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."

    # Validation from original tool
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if status is None and archived is None: return "HUBSPOT_TOOL_FAILED: Either 'status' or 'archived' must be provided."
    if status is not None and status not in ["OPEN", "CLOSED"]: return f"HUBSPOT_TOOL_FAILED: Invalid status '{status}'."
    if archived is not None and not isinstance(archived, bool): return f"HUBSPOT_TOOL_FAILED: 'archived' must be a boolean."
    if archived is False and not is_currently_archived: return f"HUBSPOT_TOOL_FAILED: To restore (archived=false), set 'is_currently_archived=true'."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if is_currently_archived: query_params['archived'] = 'true'

    payload = {}
    if status is not None: payload['status'] = status
    if archived is not None: payload['archived'] = archived

    request_data = { "method": "PATCH", "path": api_path, "query_params": query_params, "body": payload }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} updating thread. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format updating thread. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} updating thread. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error updating thread: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_archive_thread(ctx: Context, thread_id: str) -> str:
    """(Endpoint 16) Archives a single conversation thread.

    Args:
        ctx: The MCP server context.
        thread_id: The ID of the thread to archive.

    Returns:
        A success or failure message string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    request_data = { "method": "DELETE", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        # Handle 204 No Content specifically for DELETE
        if response is None: return "HUBSPOT_TOOL_SUCCESS: Thread successfully archived (No Content)."

        # Handle raw Response object (though less likely for DELETE success)
        if hasattr(response, 'status_code') and hasattr(response, 'json'):
             if 200 <= response.status_code < 300:
                 # Successful status code but got a Response object? Unexpected for 204.
                 try: body_str = response.text
                 except: body_str = "[Could not retrieve response text]"
                 return f"HUBSPOT_TOOL_SUCCESS: Archive successful (Status {response.status_code}), but received unexpected response body: {body_str[:100]}..."
             else:
                 try: body_str = response.text
                 except: body_str = "[Could not retrieve response text]"
                 return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} archiving thread. Body: {body_str}"

        # Fallback for other unexpected types
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format archiving thread. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            # Check if the error status is 204, which SDK might raise for No Content
            if status_code == 204: return "HUBSPOT_TOOL_SUCCESS: Thread successfully archived (No Content)."
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} archiving thread. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error archiving thread: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_actor_details(ctx: Context, actor_id: str) -> Dict[str, Any] | str:
    """(Endpoint 1) Retrieves details for a specific actor.

    Args:
        ctx: The MCP server context.
        actor_id: The unique ID of the actor.

    Returns:
        A dictionary containing actor details on success, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not actor_id: return "HUBSPOT_TOOL_FAILED: actor_id is required."

    api_path = f"/conversations/v3/conversations/actors/{actor_id}"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        # Handle raw Response object
        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting actor details. Body: {body_str}"

        # Handle already parsed dict/list
        elif isinstance(response, dict): return response

        # Fallback for other unexpected types
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting actor details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting actor details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting actor details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_actors_batch(ctx: Context, actor_ids: List[str]) -> Dict[str, Any] | str:
    """(Endpoint 13) Retrieves details for multiple actors in a batch.

    Args:
        ctx: The MCP server context.
        actor_ids: A list of actor IDs to retrieve.

    Returns:
        A dictionary containing batch results (potentially including errors), or a general error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not actor_ids or not isinstance(actor_ids, list): return "HUBSPOT_TOOL_FAILED: actor_ids must be a non-empty list."

    api_path = "/conversations/v3/conversations/actors/batch/read"
    payload = {"inputs": actor_ids}
    request_data = { "method": "POST", "path": api_path, "body": payload }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            # Batch can return 200 or 207 on success
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data # Includes status, results, errors etc.
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting actors batch. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting actors batch. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting actors batch. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting actors batch: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_list_inboxes(
    ctx: Context,
    limit: Optional[int] = None,
    after: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 9) Retrieves a list of conversation inboxes.

    Args:
        ctx: The MCP server context.
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.

    Returns:
        A dictionary containing inbox results and paging info, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."

    api_path = "/conversations/v3/conversations/inboxes"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} listing inboxes. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format listing inboxes. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} listing inboxes. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error listing inboxes: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_inbox_details(ctx: Context, inbox_id: str) -> Dict[str, Any] | str:
    """(Endpoint 4) Retrieves details for a specific inbox.

    Args:
        ctx: The MCP server context.
        inbox_id: The unique ID of the inbox.

    Returns:
        A dictionary containing inbox details, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not inbox_id: return "HUBSPOT_TOOL_FAILED: inbox_id is required."

    api_path = f"/conversations/v3/conversations/inboxes/{inbox_id}"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting inbox details. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting inbox details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting inbox details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting inbox details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_list_channels(
    ctx: Context,
    limit: Optional[int] = None,
    after: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 8) Retrieves a list of channels connected to inboxes.

    Args:
        ctx: The MCP server context.
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.

    Returns:
        A dictionary containing channel results and paging info, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."

    api_path = "/conversations/v3/conversations/channels"
    query_params = {}
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} listing channels. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format listing channels. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} listing channels. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error listing channels: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_channel_details(ctx: Context, channel_id: str) -> Dict[str, Any] | str:
    """(Endpoint 3) Retrieves details for a specific channel.

    Args:
        ctx: The MCP server context.
        channel_id: The unique ID of the channel.

    Returns:
        A dictionary containing channel details, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not channel_id: return "HUBSPOT_TOOL_FAILED: channel_id is required."

    api_path = f"/conversations/v3/conversations/channels/{channel_id}"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting channel details. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting channel details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting channel details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting channel details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_list_channel_accounts(
    ctx: Context,
    channel_id: Optional[str] = None,
    inbox_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None
) -> Dict[str, Any] | str:
    """(Endpoint 7) Retrieves a list of channel accounts (instances of channels).

    Args:
        ctx: The MCP server context.
        channel_id: Optional. Filter by channel ID.
        inbox_id: Optional. Filter by inbox ID.
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.

    Returns:
        A dictionary containing channel account results and paging info, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."

    api_path = "/conversations/v3/conversations/channel-accounts"
    query_params = {}
    if channel_id: query_params['channelId'] = channel_id
    if inbox_id: query_params['inboxId'] = inbox_id
    if limit: query_params['limit'] = limit
    if after: query_params['after'] = after

    request_data = { "method": "GET", "path": api_path, "query_params": query_params }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} listing channel accounts. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format listing channel accounts. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} listing channel accounts. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error listing channel accounts: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_channel_account_details(
    ctx: Context,
    channel_account_id: str
) -> Dict[str, Any] | str:
    """(Endpoint 2) Retrieves details for a specific channel account instance.

    Args:
        ctx: The MCP server context.
        channel_account_id: The unique ID of the channel account.

    Returns:
        A dictionary containing channel account details, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not channel_account_id: return "HUBSPOT_TOOL_FAILED: channel_account_id is required."

    api_path = f"/conversations/v3/conversations/channel-accounts/{channel_account_id}"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting channel account details. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting channel account details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting channel account details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting channel account details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_message_details(
    ctx: Context,
    thread_id: str,
    message_id: str
) -> Dict[str, Any] | str:
    """(Endpoint 5) Retrieves a specific message within a given thread.

    Args:
        ctx: The MCP server context.
        thread_id: The unique ID of the thread.
        message_id: The unique ID of the message.

    Returns:
        A dictionary containing message details, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if not message_id: return "HUBSPOT_TOOL_FAILED: message_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting message details. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting message details. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting message details. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting message details: {type(e).__name__} - {e}"


@mcp.tool()
async def hubspot_get_original_message_content(
    ctx: Context,
    thread_id: str,
    message_id: str
) -> Dict[str, Any] | str:
    """(Endpoint 11) Retrieves the original text/richText content of a potentially truncated message.

    Args:
        ctx: The MCP server context.
        thread_id: The unique ID of the thread.
        message_id: The unique ID of the message.

    Returns:
        A dictionary with 'text' and 'richText' keys, or an error string.
    """
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    if not client: return "HUBSPOT_TOOL_FAILED: HubSpot client not initialized."
    if not thread_id: return "HUBSPOT_TOOL_FAILED: thread_id is required."
    if not message_id: return "HUBSPOT_TOOL_FAILED: message_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}/original-content"
    request_data = { "method": "GET", "path": api_path }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        if response is None: return {}

        if hasattr(response, 'status_code') and hasattr(response, 'json'):
            if 200 <= response.status_code < 300:
                try:
                    parsed_data = response.json()
                    if isinstance(parsed_data, dict): return parsed_data
                    else: return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but JSON parsing yielded unexpected type: {type(parsed_data).__name__}"
                except Exception as json_err:
                    try: response_text = response.text
                    except: response_text = "[Could not retrieve response text]"
                    return f"HUBSPOT_TOOL_WARNING: API call successful (Status {response.status_code}), but failed to parse JSON response. Error: {json_err}. Response Text: {response_text[:200]}..."
            else:
                try: body_str = response.text
                except: body_str = "[Could not retrieve response text]"
                return f"HUBSPOT_TOOL_FAILED: API Error Status {response.status_code} getting original message content. Body: {body_str}"

        elif isinstance(response, dict): return response

        else: return f"HUBSPOT_TOOL_FAILED: Unexpected success response format getting original message content. Type: {type(response).__name__}"

    except Exception as e:
        if hasattr(e, 'status'):
            status_code = e.status
            error_body = getattr(e, 'body', 'No body')
            error_reason = getattr(e, 'reason', 'No reason')
            try: body_str = error_body.decode('utf-8', errors='replace') if isinstance(error_body, bytes) else str(error_body)
            except: body_str = "[Could not decode error body]"
            return f"HUBSPOT_TOOL_FAILED: API Error Status {status_code} getting original message content. Reason: {error_reason}. Body: {body_str}"
        else: return f"HUBSPOT_TOOL_FAILED: Unexpected error getting original message content: {type(e).__name__} - {e}"

# --- End of Added Tools ---

# --- Main Execution Block --- #
async def main():
    transport = os.getenv("TRANSPORT", "stdio").lower()
    # print(f"Starting HubSpot MCP Server with {transport} transport...")
    if transport == 'sse':
        await mcp.run_sse_async()
    elif transport == 'stdio':
        await mcp.run_stdio_async()
    else:
        # print(f"Error: Invalid TRANSPORT specified: {transport}. Use 'stdio' or 'sse'.")
        pass # Or raise an error

if __name__ == "__main__":
    # Ensure event loop policy is set for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
