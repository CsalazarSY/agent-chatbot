"""Tools for interacting with HubSpot Conversations API"""

# /src/tools/hubspot/conversation/conversation_tools.py
import asyncio
from typing import Optional, List, Union, Dict, Any

# Import config for client and defaults
import config
from src.services.clean_agent_tags import clean_agent_output

# Import Pydantic models for request/response validation
from .dto_responses import (
    ThreadDetail,
    ListMessagesResponse,
    ListThreadsResponse,
    ThreadStatus,
    UpdateThreadResponse,
    ActorDetailResponse,
    BatchReadActorsResponse,
    ListInboxesResponse,
    InboxDetailResponse,
    ListChannelsResponse,
    ChannelDetailResponse,
    ListChannelAccountsResponse,
    ChannelAccountDetailResponse,
    MessageDetailResponse,
    OriginalMessageContentResponse,
    CreateMessageResponse,
)
from .dto_requests import (
    BatchReadActorsRequest,
    CreateMessageRequest,
    UpdateThreadRequest,
)

# Standardized Error Prefix
ERROR_PREFIX = "HUBSPOT_TOOL_FAILED:"

# --- Internal Helper Function --- #


async def _make_hubspot_api_request(
    method: str,
    api_path: str,
    query_params: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
) -> Union[Dict, List, str, None]:  # Can return None on 204 No Content
    """Internal helper to make HubSpot API requests via the API client.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE).
        api_path: The API endpoint path (e.g., '/conversations/v3/...').
        query_params: Optional dictionary of query parameters.
        json_payload: Optional dictionary for the request body (for POST/PATCH).

    Returns:
        - Parsed JSON response (Dict or List) on success.
        - None on success with 204 No Content status.
        - An error string prefixed with ERROR_PREFIX on failure.
    """
    client = config.HUBSPOT_CLIENT
    if not client:
        return f"{ERROR_PREFIX} HubSpot client not initialized in config."

    request_data = {
        "method": method.upper(),
        "path": api_path,
        "query_params": query_params or {},
        "body": json_payload,
    }

    try:
        response = await asyncio.to_thread(client.api_request, request_data)

        # Handle successful 204 No Content (e.g., DELETE archive_thread)
        # The HubSpot API might return None directly for 204
        if response is None and method.upper() == "DELETE":
            return None  # Indicate successful deletion/no content

        # Handle cases where API returns the raw response object
        if hasattr(response, "status_code"):
            status_code = response.status_code
            if 200 <= status_code < 300:
                if status_code == 204:
                    return None  # Explicitly return None for 204
                try:
                    # Try parsing JSON for other 2xx codes
                    return response.json()
                except Exception as json_err:
                    # Success status but no valid JSON?
                    try:
                        body_str = response.text
                    except Exception:
                        body_str = "[Could not read response text]"
                    return f"{ERROR_PREFIX} API call successful (Status {status_code}) but failed to parse JSON response. Error: {json_err}. Body: {body_str[:200]}..."
            else:
                # Handle error status codes from raw response object
                try:
                    body_str = response.text
                except Exception:
                    body_str = "[Could not read response text]"
                return (
                    f"{ERROR_PREFIX} API Error Status {status_code}. Body: {body_str}"
                )

        # Handle cases where API returns pre-parsed dict/list (more common)
        elif isinstance(response, (dict, list)):
            # Assume successful if dict or list returned directly
            return response

        # Fallback for unexpected successful response types
        else:
            return f"{ERROR_PREFIX} Unexpected success response format from API call. Type: {type(response).__name__}. Path: {api_path}"

    except Exception as e:
        # Handle exceptions raised by the API client
        if hasattr(e, "status"):
            status_code = e.status
            error_body = getattr(e, "body", "No body")
            error_reason = getattr(e, "reason", "No reason")
            try:
                body_str = (
                    error_body.decode("utf-8", errors="replace")
                    if isinstance(error_body, bytes)
                    else str(error_body)
                )
            except Exception:
                body_str = "[Could not decode error body]"
            # Check for 204 raised as exception (possible API behavior)
            if status_code == 204 and method.upper() == "DELETE":
                return None  # Treat as successful deletion
            return f"{ERROR_PREFIX} API Error Status {status_code}. Reason: {error_reason}. Body: {body_str}"

        return f"{ERROR_PREFIX} Unexpected error during API request to {api_path}: {type(e).__name__} - {e}"


# --- Actor Tools --- #


async def get_actor_details(actor_id: str) -> Union[ActorDetailResponse, str]:
    """Retrieves details for a specific actor.
    Allowed Scopes: [Dev, Internal]
    Args: actor_id: The unique ID of the actor.
    Returns: An ActorDetailResponse model instance on success, or an error string.
    """
    if not actor_id:
        return f"{ERROR_PREFIX} actor_id is required."

    api_path = f"/conversations/v3/conversations/actors/{actor_id}"
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):  # Error string from helper
        return result
    elif isinstance(result, dict):
        try:
            return ActorDetailResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_actor_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_actor_details: {type(result).__name__}"


async def get_actors_batch(actor_ids: List[str]) -> Union[BatchReadActorsResponse, str]:
    """Retrieves details for multiple actors in a batch.
    Allowed Scopes: [Dev, Internal]
    Args: actor_ids: A list of actor IDs to retrieve.
    Returns: A BatchReadActorsResponse model instance (potentially including errors), or a general error string.
    """
    if not actor_ids or not isinstance(actor_ids, list):
        return f"{ERROR_PREFIX} actor_ids must be a non-empty list."

    api_path = "/conversations/v3/conversations/actors/batch/read"
    try:
        request_body = BatchReadActorsRequest(inputs=actor_ids).model_dump()
    except Exception as pydantic_err:
        return f"{ERROR_PREFIX} Failed to create request body for batch actors: {pydantic_err}"

    result = await _make_hubspot_api_request(
        "POST", api_path, json_payload=request_body
    )

    if isinstance(result, str):  # Error string from helper
        return result
    elif isinstance(result, dict):
        try:
            # Batch API can return 200 or 207, response DTO handles the structure
            return BatchReadActorsResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_actors_batch: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_actors_batch: {type(result).__name__}"


# --- Channel Tools --- #


async def get_channel_account_details(
    channel_account_id: str,
) -> Union[ChannelAccountDetailResponse, str]:
    """Retrieves details for a specific channel account instance.
    Allowed Scopes: [Dev, Internal]
    Args: channel_account_id: The unique ID of the channel account.
    Returns: A ChannelAccountDetailResponse model instance, or an error string.
    """
    if not channel_account_id:
        return f"{ERROR_PREFIX} channel_account_id is required."

    api_path = f"/conversations/v3/conversations/channel-accounts/{channel_account_id}"
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return ChannelAccountDetailResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_channel_account_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_channel_account_details: {type(result).__name__}"


async def get_channel_details(channel_id: str) -> Union[ChannelDetailResponse, str]:
    """Retrieves details for a specific channel.
    Allowed Scopes: [Dev, Internal]
    Args: channel_id: The unique ID of the channel.
    Returns: A ChannelDetailResponse model instance, or an error string.
    """
    if not channel_id:
        return f"{ERROR_PREFIX} channel_id is required."

    api_path = f"/conversations/v3/conversations/channels/{channel_id}"
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return ChannelDetailResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_channel_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_channel_details: {type(result).__name__}"


async def list_channel_accounts(
    channel_id: Optional[str] = None,
    inbox_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> Union[ListChannelAccountsResponse, str]:
    """Retrieves a list of channel accounts (instances of channels).
    Allowed Scopes: [Dev, Internal]
    Args:
        channel_id: Optional. Filter by channel ID.
        inbox_id: Optional. Filter by inbox ID.
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.
    Returns: A ListChannelAccountsResponse model instance containing channel account results/paging info, or an error string.
    """
    api_path = "/conversations/v3/conversations/channel-accounts"
    query_params = {}
    if channel_id:
        query_params["channelId"] = channel_id
    if inbox_id:
        query_params["inboxId"] = inbox_id
    if limit:
        query_params["limit"] = limit
    if after:
        query_params["after"] = after

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):  # Response is a dict containing 'results'
        try:
            return ListChannelAccountsResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for list_channel_accounts: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for list_channel_accounts: {type(result).__name__}"


async def list_channels(
    limit: Optional[int] = None, after: Optional[str] = None
) -> Union[ListChannelsResponse, str]:
    """Retrieves a list of channels connected to inboxes.
    Allowed Scopes: [Dev, Internal]
    Args:
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.
    Returns: A ListChannelsResponse model instance containing channel results and paging info, or an error string.
    """
    api_path = "/conversations/v3/conversations/channels"
    query_params = {}
    if limit:
        query_params["limit"] = limit
    if after:
        query_params["after"] = after

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):  # Response is a dict containing 'results'
        try:
            return ListChannelsResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for list_channels: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for list_channels: {type(result).__name__}"


# --- Inbox Tools --- #


async def get_inbox_details(inbox_id: str) -> Union[InboxDetailResponse, str]:
    """Retrieves details for a specific inbox.
    Allowed Scopes: [Dev, Internal]
    Args: inbox_id: The unique ID of the inbox.
    Returns: An InboxDetailResponse model instance, or an error string.
    """
    if not inbox_id:
        return f"{ERROR_PREFIX} inbox_id is required."

    api_path = f"/conversations/v3/conversations/inboxes/{inbox_id}"
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return InboxDetailResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_inbox_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_inbox_details: {type(result).__name__}"


async def list_inboxes(
    limit: Optional[int] = None, after: Optional[str] = None
) -> Union[ListInboxesResponse, str]:
    """Retrieves a list of conversation inboxes.
    Allowed Scopes: [Dev, Internal]
    Args:
        limit: Optional. Maximum results per page.
        after: Optional. Paging cursor.
    Returns: A ListInboxesResponse model instance containing inbox results and paging info, or an error string.
    """
    api_path = "/conversations/v3/conversations/inboxes"
    query_params = {}
    if limit:
        query_params["limit"] = limit
    if after:
        query_params["after"] = after

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):  # Response is dict with 'results'
        try:
            return ListInboxesResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for list_inboxes: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for list_inboxes: {type(result).__name__}"


# --- Message Tools --- #


async def get_message_details(
    thread_id: str, message_id: str
) -> Union[MessageDetailResponse, str]:
    """Retrieves a specific message within a given thread.
    Allowed Scopes: [Dev, Internal]
    Args:
        thread_id: The unique ID of the thread.
        message_id: The unique ID of the message.
    Returns: A MessageDetailResponse model instance, or an error string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."
    if not message_id:
        return f"{ERROR_PREFIX} message_id is required."

    api_path = (
        f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}"
    )
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return MessageDetailResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_message_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_message_details: {type(result).__name__}"


async def get_original_message_content(
    thread_id: str, message_id: str
) -> Union[OriginalMessageContentResponse, str]:
    """Retrieves the original text/richText content of a potentially truncated message.
    Allowed Scopes: [Dev, Internal]
    Args:
        thread_id: The unique ID of the thread.
        message_id: The unique ID of the message.
    Returns: An OriginalMessageContentResponse model instance with 'text'/'richText', or an error string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."
    if not message_id:
        return f"{ERROR_PREFIX} message_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages/{message_id}/original-content"
    result = await _make_hubspot_api_request("GET", api_path)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return OriginalMessageContentResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_original_message_content: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_original_message_content: {type(result).__name__}"


# --- Thread Tools --- #


async def archive_thread(thread_id: str) -> str:
    """Archives a single conversation thread.
    Allowed Scopes: [Dev Only]
    Args: thread_id: The ID of the thread to archive.
    Returns: A success or failure message string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    result = await _make_hubspot_api_request("DELETE", api_path)

    if result is None:
        return "HUBSPOT_TOOL_SUCCESS: Thread successfully archived (No Content)."
    elif isinstance(result, str):  # Error string from helper
        return result
    else:
        # Unexpected if DELETE didn't return None or error string
        return f"{ERROR_PREFIX} Unexpected response type from helper for archive_thread: {type(result).__name__}. Expected None or error string."


async def get_thread_details(
    thread_id: str, association: Optional[str] = None
) -> Union[ThreadDetail, str]:
    """Retrieves details for a single conversation thread.
    Allowed Scopes: [Dev, Internal]
    Args:
        thread_id: The unique ID of the thread.
        association: Optional. Specify an association type (e.g., 'TICKET') to include associated object IDs.
    Returns: A ThreadDetail model instance on success, or an error string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if association:
        query_params["association"] = association

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            return ThreadDetail.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_thread_details: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_thread_details: {type(result).__name__}"


async def get_thread_messages(
    thread_id: str,
    limit: Optional[int] = None,
    after: Optional[str] = None,
    sort: Optional[str] = None,
) -> Union[ListMessagesResponse, str]:
    """Retrieves message history for a thread.
    Allowed Scopes: [Dev, Internal]
    Args:
        thread_id: The unique ID of the thread.
        limit: Optional. Maximum number of messages per page.
        after: Optional. Paging cursor for the next page.
        sort: Optional. Sort direction ('createdAt' or '-createdAt'). Default is '-createdAt'.
    Returns: A ListMessagesResponse model instance containing message results and paging info, or an error string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    query_params = {}
    if limit:
        query_params["limit"] = limit
    if after:
        query_params["after"] = after
    if sort:
        query_params["sort"] = sort

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):  # Response is dict with 'results'
        try:
            return ListMessagesResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for get_thread_messages: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for get_thread_messages: {type(result).__name__}"


async def list_threads(
    limit: Optional[int] = None,
    after: Optional[str] = None,
    thread_status: Optional[ThreadStatus] = None,
    inbox_id: Optional[str] = None,
    associated_contact_id: Optional[str] = None,
    sort: Optional[str] = None,
    association: Optional[str] = None,
) -> Union[ListThreadsResponse, str]:
    """Retrieves a list of conversation threads with filtering and pagination.
    Allowed Scopes: [Dev, Internal]
    Args:
        limit: Optional. Max results per page.
        after: Optional. Paging cursor.
        thread_status: Optional. Filter by status ('OPEN' or 'CLOSED'). Required if using associated_contact_id.
        inbox_id: Optional. Filter by inbox ID. Cannot be used with associated_contact_id.
        associated_contact_id: Optional. Filter by contact ID. Cannot be used with inbox_id. Requires thread_status.
        sort: Optional. Sort order ('id', 'latestMessageTimestamp', etc.).
        association: Optional. Include associations (e.g., 'TICKET').
    Returns: A ListThreadsResponse model instance containing thread results and paging info, or an error string.
    """
    if associated_contact_id and inbox_id:
        return f"{ERROR_PREFIX} Cannot use both 'inbox_id' and 'associated_contact_id'."
    if associated_contact_id and not thread_status:
        return f"{ERROR_PREFIX} 'thread_status' is required when filtering by 'associated_contact_id'."

    api_path = "/conversations/v3/conversations/threads"
    query_params = {}
    if limit:
        query_params["limit"] = limit
    if after:
        query_params["after"] = after
    if thread_status:
        query_params["threadStatus"] = thread_status
    if inbox_id:
        query_params["inboxId"] = inbox_id
    if associated_contact_id:
        query_params["associatedContactId"] = associated_contact_id
    if sort:
        query_params["sort"] = sort
    if association:
        query_params["association"] = association

    result = await _make_hubspot_api_request("GET", api_path, query_params=query_params)

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):  # Response is dict with 'results'
        try:
            return ListThreadsResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for list_threads: {parse_err}. Data: {str(result)[:200]}..."
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for list_threads: {type(result).__name__}"


async def send_message_to_thread(
    thread_id: str,
    message_text: str,
    channel_id: Optional[str] = None,
    channel_account_id: Optional[str] = None,
    sender_actor_id: Optional[str] = None,
    rich_text: Optional[str] = None,
    subject: Optional[str] = None,
    recipients: Optional[List[dict]] = None,
    attachments: Optional[List[dict]] = None,
) -> Union[CreateMessageResponse, str]:
    """Sends a message or comment to a HubSpot conversation thread.
    If the message_text contains 'HANDOFF' or 'COMMENT' (case-insensitive), it sends the message
    as an internal COMMENT, otherwise it sends it as a regular MESSAGE.
    Allowed Scopes: [Dev, Internal]
    Args:
        thread_id: The HubSpot conversation thread ID.
        message_text: The content of the message/comment to send.
        channel_id: Optional. The channel ID (e.g., '1000' for chat). Uses default from config if None.
        channel_account_id: Optional. The specific channel account ID (e.g., chatflow ID). Uses default from config if None.
        sender_actor_id: Optional. The HubSpot Actor ID (e.g., "A-12345") posting the message/comment. Uses default from config if None.
        rich_text: Optional. Rich text (HTML) content of the message.
        subject: Optional. Subject line, primarily for email messages.
        recipients: Optional. List of recipient dictionaries (matching MessageRecipientRequest structure).
        attachments: Optional. List of attachment dictionaries (matching MessageAttachmentRequest structure).
    Returns: A CreateMessageResponse (MessageDetail) model instance on success, or an error string.
    """
    # Use config values for defaults
    final_channel_id = channel_id or config.HUBSPOT_DEFAULT_CHANNEL
    final_channel_account_id = (
        channel_account_id or config.HUBSPOT_DEFAULT_CHANNEL_ACCOUNT
    )
    final_sender_actor_id = sender_actor_id or config.HUBSPOT_DEFAULT_SENDER_ACTOR_ID

    # --- Input Validation ---
    if not thread_id or not isinstance(thread_id, str):
        return f"{ERROR_PREFIX} Valid HubSpot thread ID was not provided."
    if not final_channel_id or not isinstance(final_channel_id, str):
        return f"{ERROR_PREFIX} Valid HubSpot channel ID was not provided."
    if not final_channel_account_id or not isinstance(final_channel_account_id, str):
        return f"{ERROR_PREFIX} Valid HubSpot channel account ID was not provided."
    if not final_sender_actor_id or not isinstance(final_sender_actor_id, str):
        return f"{ERROR_PREFIX} Valid HubSpot sender actor ID was not provided."
    if not message_text or not isinstance(message_text, str):
        return f"{ERROR_PREFIX} Valid message text was not provided."

    # --- Determine Message Type ---
    message_type = "MESSAGE"
    if "HANDOFF" in message_text.upper() or "COMMENT" in message_text.upper():
        message_type = "COMMENT"

    cleaned_message_text = clean_agent_output(message_text)
    # --- Prepare Payload ---
    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    payload_dict = {
        "type": message_type,
        "text": cleaned_message_text,
        "senderActorId": final_sender_actor_id,
        "channelId": final_channel_id,
        "channelAccountId": final_channel_account_id,
    }
    if rich_text:
        payload_dict["richText"] = rich_text
    if subject:
        payload_dict["subject"] = subject
    if recipients:
        payload_dict["recipients"] = recipients
    if attachments:
        payload_dict["attachments"] = attachments

    try:
        request_body = CreateMessageRequest(**payload_dict).model_dump(
            exclude_none=True
        )
    except Exception as pydantic_err:
        return f"{ERROR_PREFIX} Failed to create request body for sending message: {pydantic_err}. Payload attempted: {payload_dict}"

    # --- Make API Call --- #
    result = await _make_hubspot_api_request(
        "POST", api_path, json_payload=request_body
    )

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        try:
            # Response should be the created message detail (201 Created usually)
            return CreateMessageResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for send_message_to_thread: {parse_err}. Data: {str(result)[:200]}..."

    # POST should return a dict on success
    return f"{ERROR_PREFIX} Unexpected successful response type from helper for send_message_to_thread: {type(result).__name__}"


async def update_thread(
    thread_id: str,
    status: Optional[str] = None,
    archived: Optional[bool] = None,
    is_currently_archived: bool = False,
) -> Union[UpdateThreadResponse, str]:
    """Updates a thread's status or restores it from archive.
    Allowed Scopes: [Dev Only]
    Args:
        thread_id: The ID of the thread to update.
        status: Optional. New status ('OPEN' or 'CLOSED').
        archived: Optional. Set to False to restore an archived thread.
        is_currently_archived: Set to True if restoring (sets required query param). Defaults to False.
    Returns: An UpdateThreadResponse model instance (updated thread details) on success, or an error string.
    """
    if not thread_id:
        return f"{ERROR_PREFIX} thread_id is required."
    if status is None and archived is None:
        return f"{ERROR_PREFIX} Either 'status' or 'archived' must be provided."

    # --- Prepare Payload ---
    payload_dict = {}
    if status is not None:
        if status not in ["OPEN", "CLOSED"]:
            return f"{ERROR_PREFIX} Invalid status '{status}'."
        payload_dict["status"] = status
    if archived is not None:
        payload_dict["archived"] = archived
    if archived is False and not is_currently_archived:
        return f"{ERROR_PREFIX} To restore (archived=false), set 'is_currently_archived=true'."

    api_path = f"/conversations/v3/conversations/threads/{thread_id}"
    query_params = {}
    if is_currently_archived:
        query_params["archived"] = "true"

    try:
        request_body = UpdateThreadRequest(**payload_dict).model_dump(exclude_none=True)
    except Exception as pydantic_err:
        return f"{ERROR_PREFIX} Failed to create request body for updating thread: {pydantic_err}. Payload attempted: {payload_dict}"

    # --- Make API Call --- #
    result = await _make_hubspot_api_request(
        "PATCH", api_path, query_params=query_params, json_payload=request_body
    )

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        try:
            # Response is the updated thread detail
            return UpdateThreadResponse.model_validate(result)
        except Exception as parse_err:
            return f"{ERROR_PREFIX} Failed to validate successful response for update_thread: {parse_err}. Data: {str(result)[:200]}..."
    else:
        # PATCH should return a dict on success
        return f"{ERROR_PREFIX} Unexpected successful response type from helper for update_thread: {type(result).__name__}"
