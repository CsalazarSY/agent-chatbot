""" Pydantic models for HubSpot Conversations API responses. """
# src/tools/hubspot/dto_responses.py
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

# --- Base Models ---

class DeliveryIdentifier(BaseModel):
    """Identifies how a message was delivered (e.g., EMAIL, HS_EMAIL_ADDRESS)."""
    type: Optional[str] = Field(None, description="The type of the delivery identifier (e.g., 'EMAIL').")
    value: Optional[str] = Field(None, description="The value of the delivery identifier (e.g., 'test@example.com').")

class PagingNext(BaseModel):
    """Contains information for fetching the next page of results."""
    link: Optional[str] = Field(None, description="A link to the next page of results.")
    after: Optional[str] = Field(None, description="The cursor token to use for the next page request.")

class Paging(BaseModel):
    """Paging information included in list responses."""
    next: Optional[PagingNext] = Field(None, description="Details for accessing the next page, if available.")

class MessageStatusType(str, Enum):
    """ Defines known status types for messages. """
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    FAILED = "FAILED"

class ClientType(str, Enum):
    """ Defines known client types originating messages/events. """
    HUBSPOT = "HUBSPOT"
    SYSTEM = "SYSTEM"
    INTEGRATION = "INTEGRATION"

class MessageStatusFailureDetails(BaseModel):
    """Details about why a message failed to send."""
    errorMessageTokens: Optional[Dict[str, str]] = Field(None, description="Tokens for constructing a localized error message.")
    errorMessage: Optional[str] = Field(None, description="The specific error message.")

class MessageStatus(BaseModel):
    """Represents the status of a message (e.g., SENT, FAILED)."""
    statusType: Optional[MessageStatusType] = Field(None, description="The high-level status (SENT, RECEIVED, FAILED).")
    failureDetails: Optional[MessageStatusFailureDetails] = Field(None, description="Details if the statusType is FAILED.")

class ClientInfo(BaseModel):
    """Information about the client application that created the message."""
    clientType: Optional[ClientType] = Field(None, description="The type of client (e.g., HUBSPOT, INTEGRATION).")
    integrationAppId: Optional[int] = Field(None, description="The App ID if the clientType is INTEGRATION.")

class MessageSender(BaseModel):
    """Represents a sender of a message."""
    actorId: Optional[str] = Field(None, description="The HubSpot actor ID (e.g., 'A-xxxxx', 'U-xxxxx') of the sender.")
    name: Optional[str] = Field(None, description="The display name of the sender.")
    senderField: Optional[str] = Field(None, description="Indicates the role of the sender (e.g., 'FROM').")
    deliveryIdentifier: Optional[DeliveryIdentifier] = Field(None, description="The delivery identifier associated with the sender.")

class MessageRecipient(BaseModel):
    """Represents a recipient of a message."""
    actorId: Optional[str] = Field(None, description="The HubSpot actor ID (e.g., 'A-xxxxx', 'V-xxxxx') of the recipient.")
    name: Optional[str] = Field(None, description="The display name of the recipient.")
    deliveryIdentifier: Optional[DeliveryIdentifier] = Field(None, description="The delivery identifier for the recipient (can be null).")
    recipientField: Optional[str] = Field(None, description="The role of the recipient (e.g., 'TO', 'CC', 'BCC').")

class ThreadAssociations(BaseModel):
    """Holds IDs of objects associated with a conversation thread."""
    # Using Field alias for potential snake_case conversion if needed later
    associatedTicketId: Optional[str] = Field(None, alias="associatedTicketId", description="The ID of the associated HubSpot ticket, if any.")

class ActorType(str, Enum):
    """Type of actor involved in a conversation."""
    AGENT = "AGENT" # Represents a HubSpot User
    BOT = "BOT"     # Represents a HubSpot Bot
    # Note: Other types like VISITOR ('V-xxxxx') exist but might not be returned by /actors endpoint directly.

class Actor(BaseModel):
    """Represents an actor (user, bot) involved in conversations."""
    type: Optional[ActorType] = Field(None, description="The type of the actor (e.g., AGENT, BOT).")
    id: str = Field(..., description="The unique ID of the actor (e.g., 'A-xxxxx').")
    name: Optional[str] = Field(None, description="The name of the actor.")
    email: Optional[str] = Field(None, description="The email address associated with the actor (usually for AGENT type).")
    avatar: Optional[str] = Field(None, description="A URL to the actor's avatar image.")

class ChannelAccount(BaseModel):
    """Represents a specific instance of a channel connected to an inbox (e.g., a specific chatflow or email address)."""
    createdAt: Optional[str] = Field(None, description="Timestamp when the channel account was created.")
    archivedAt: Optional[str] = Field(None, description="Timestamp when the channel account was archived.")
    archived: Optional[bool] = Field(None, description="Indicates if the channel account is archived.")
    authorized: Optional[bool] = Field(None, description="Indicates if HubSpot is authorized to use this channel account.")
    name: Optional[str] = Field(None, description="The name of the channel account.")
    active: Optional[bool] = Field(None, description="Indicates if the channel account is currently active.")
    deliveryIdentifier: Optional[DeliveryIdentifier] = Field(None, description="The primary delivery identifier for this account (e.g., email address).")
    id: str = Field(..., description="The unique ID of the channel account.")
    inboxId: Optional[str] = Field(None, description="The ID of the inbox this channel account belongs to.")
    channelId: Optional[str] = Field(None, description="The ID of the channel type (e.g., 'EMAIL', 'FB_MESSENGER').")

class Channel(BaseModel):
    """Represents a type of communication channel (e.g., EMAIL, CHAT)."""
    name: Optional[str] = Field(None, description="The name of the channel type (e.g., 'Email', 'Chat').")
    id: str = Field(..., description="The unique ID of the channel type.")

class InboxType(str, Enum):
    """Type of HubSpot inbox."""
    HELP_DESK = "HELP_DESK"
    INBOX = "INBOX"

class Inbox(BaseModel):
    """Represents a HubSpot Conversations Inbox."""
    createdAt: Optional[str] = Field(None, description="Timestamp when the inbox was created.")
    archivedAt: Optional[str] = Field(None, description="Timestamp when the inbox was archived.")
    archived: Optional[bool] = Field(None, description="Indicates if the inbox is archived.")
    name: Optional[str] = Field(None, description="The name of the inbox.")
    id: str = Field(..., description="The unique ID of the inbox.")
    type: Optional[InboxType] = Field(None, description="The type of the inbox.")
    updatedAt: Optional[str] = Field(None, description="Timestamp when the inbox was last updated.")

class MessageType(str, Enum):
    """ Defines known message types within a conversation thread. """
    MESSAGE = "MESSAGE"                 # Standard communication message
    COMMENT = "COMMENT"                 # Internal comment/note
    WELCOME_MESSAGE = "WELCOME_MESSAGE" # Automated welcome message (e.g., chat)
    SYSTEM = "SYSTEM"                   # System-generated event message
    ASSIGNMENT = "ASSIGNMENT"           # Message indicating thread assignment change
    THREAD_STATUS_CHANGE = "THREAD_STATUS_CHANGE" # Message indicating thread status change (Open/Closed)

class MessageTruncationStatus(str, Enum):
    """Indicates if a message's content was truncated."""
    TRUNCATED = "TRUNCATED"             # Content is truncated, use get_original_message_content
    NOT_TRUNCATED = "NOT_TRUNCATED"     # Content is complete

class MessageDirection(str, Enum):
    """Direction of the message relative to HubSpot."""
    INCOMING = "INCOMING"               # Message received by HubSpot
    OUTGOING = "OUTGOING"               # Message sent from HubSpot

class MessageDetail(BaseModel):
    """Represents a single message or event within a conversation thread."""
    # --- Core Fields ---
    type: Optional[MessageType] = Field(None, description="The type of the message/event.")
    id: str = Field(..., description="The unique ID of the message.")
    conversationsThreadId: Optional[str] = Field(None, alias="conversationsThreadId", description="The ID of the thread this message belongs to.")
    createdAt: Optional[str] = Field(None, description="Timestamp when the message was created.")
    updatedAt: Optional[str] = Field(None, description="Timestamp when the message was last updated.")
    createdBy: Optional[str] = Field(None, description="Actor ID of the creator (might be system/integration).")
    client: Optional[ClientInfo] = Field(None, description="Information about the client that created the message.")
    senders: Optional[List[MessageSender]] = Field(None, description="List of senders (usually one).")
    recipients: Optional[List[MessageRecipient]] = Field(None, description="List of recipients.")
    archived: Optional[bool] = Field(None, description="Indicates if the message is archived.")

    # --- Content Fields (primarily for MESSAGE, COMMENT, WELCOME_MESSAGE) ---
    text: Optional[str] = Field(None, description="Plain text content of the message.")
    richText: Optional[str] = Field(None, description="Rich text (HTML) content of the message.")
    attachments: Optional[List[Any]] = Field(None, description="List of attachments (structure varies, using Any). Define specific model if needed.")
    subject: Optional[str] = Field(None, description="Subject line (primarily for email).")
    truncationStatus: Optional[MessageTruncationStatus] = Field(None, description="Indicates if the message content is truncated.")
    inReplyToId: Optional[str] = Field(None, description="ID of the message this is a reply to (email threading).")

    # --- Status & Direction Fields ---
    status: Optional[MessageStatus] = Field(None, description="The delivery status of the message.")
    direction: Optional[MessageDirection] = Field(None, description="Direction of the message (INCOMING or OUTGOING).")

    # --- Channel Fields ---
    channelId: Optional[str] = Field(None, description="ID of the channel type used.")
    channelAccountId: Optional[str] = Field(None, description="ID of the specific channel account used.")

    # --- Fields for specific types ---
    assignedTo: Optional[str] = Field(None, description="Actor ID assigned (for ASSIGNMENT type).")
    newStatus: Optional[str] = Field(None, description="New thread status (for THREAD_STATUS_CHANGE type).")

    # Allow other fields from API response
    model_config = {
        "extra": "allow",
        "populate_by_name": True # Allows using alias 'conversationsThreadId'
    }

class ThreadStatus(str, Enum):
    """Status of a conversation thread."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class ThreadDetail(BaseModel):
    """Represents a conversation thread."""
    associatedContactId: Optional[str] = Field(None, alias="associatedContactId", description="ID of the primary associated contact.")
    threadAssociations: Optional[ThreadAssociations] = Field(None, description="Contains IDs of associated objects like tickets.")
    assignedTo: Optional[str] = Field(None, description="Actor ID of the HubSpot user assigned to the thread.")
    createdAt: Optional[str] = Field(None, description="Timestamp when the thread was created.")
    archived: Optional[bool] = Field(None, description="Indicates if the thread is archived.")
    originalChannelId: Optional[str] = Field(None, description="ID of the channel type where the thread originated.")
    latestMessageTimestamp: Optional[str] = Field(None, description="Timestamp of the latest message (sent or received).")
    latestMessageSentTimestamp: Optional[str] = Field(None, description="Timestamp of the latest outgoing message.")
    originalChannelAccountId: Optional[str] = Field(None, description="ID of the specific channel account where the thread originated.")
    id: str = Field(..., description="The unique ID of the thread.")
    closedAt: Optional[str] = Field(None, description="Timestamp when the thread was closed.")
    spam: Optional[bool] = Field(None, description="Indicates if the thread is marked as spam.")
    inboxId: Optional[str] = Field(None, description="ID of the inbox the thread belongs to.")
    status: Optional[ThreadStatus] = Field(None, description="The current status of the thread (OPEN or CLOSED).")
    latestMessageReceivedTimestamp: Optional[str] = Field(None, description="Timestamp of the latest incoming message.")

    model_config = {
        "populate_by_name": True # Allows using alias 'associatedContactId'
    }

# --- Specific Endpoint Response Models ---

# GET /conversations/v3/conversations/actors/{actorId}
ActorDetailResponse = Actor

# GET /conversations/v3/conversations/channel-accounts/{channelAccountId}
ChannelAccountDetailResponse = ChannelAccount

# GET /conversations/v3/conversations/channels/{channelId}
ChannelDetailResponse = Channel

# GET /conversations/v3/conversations/inboxes/{inboxId}
InboxDetailResponse = Inbox

# GET /conversations/v3/conversations/threads/{threadId}/messages/{messageId}
MessageDetailResponse = MessageDetail

# GET /conversations/v3/conversations/threads/{threadId}
ThreadDetailResponse = ThreadDetail

# GET /conversations/v3/conversations/channel-accounts
class ListChannelAccountsResponse(BaseModel):
    """Response model for listing channel accounts."""
    total: Optional[int] = Field(None, description="Total number of channel accounts matching the query.")
    paging: Optional[Paging] = Field(None, description="Paging information for navigating results.")
    results: List[ChannelAccount] = Field(..., description="List of channel account details.")

# GET /conversations/v3/conversations/channels
class ListChannelsResponse(BaseModel):
    """Response model for listing channels."""
    total: Optional[int] = Field(None, description="Total number of channels.")
    paging: Optional[Paging] = Field(None, description="Paging information for navigating results.")
    results: List[Channel] = Field(..., description="List of channel details.")

# GET /conversations/v3/conversations/inboxes
class ListInboxesResponse(BaseModel):
    """Response model for listing inboxes."""
    total: Optional[int] = Field(None, description="Total number of inboxes.")
    paging: Optional[Paging] = Field(None, description="Paging information for navigating results.")
    results: List[Inbox] = Field(..., description="List of inbox details.")

# GET /conversations/v3/conversations/threads/{threadId}/messages
class ListMessagesResponse(BaseModel):
    """Response model for listing messages within a thread."""
    paging: Optional[Paging] = Field(None, description="Paging information for navigating results.")
    results: List[MessageDetail] = Field(..., description="List of message details (can be empty).")

# GET /conversations/v3/conversations/threads/{threadId}/messages/{messageId}/original-content
class OriginalMessageContentResponse(BaseModel):
    """Response model containing the full original content of a potentially truncated message."""
    text: Optional[str] = Field(None, description="The full original plain text content.")
    richText: Optional[str] = Field(None, description="The full original rich text (HTML) content.")

# GET /conversations/v3/conversations/threads
class ListThreadsResponse(BaseModel):
    """Response model for listing conversation threads."""
    paging: Optional[Paging] = Field(None, description="Paging information for navigating results.")
    results: List[ThreadDetail] = Field(..., description="List of thread details.")

# POST /conversations/v3/conversations/actors/batch/read
class BatchReadActorsResponse(BaseModel): # Renamed for clarity
    """Response model for batch reading actor details."""
    completedAt: Optional[str] = Field(None, description="Timestamp when the batch operation completed.")
    requestedAt: Optional[str] = Field(None, description="Timestamp when the batch operation was requested.")
    startedAt: Optional[str] = Field(None, description="Timestamp when the batch operation started.")
    links: Optional[Dict[str, str]] = Field(None, description="Links related to the batch operation.")
    results: List[Actor] = Field(..., description="List of successfully retrieved actor details.")
    status: Optional[str] = Field(None, description="Status of the batch operation (e.g., 'PENDING', 'COMPLETE').")

# POST /conversations/v3/conversations/threads/{threadId}/messages
# Response is the created message details
CreateMessageResponse = MessageDetail

# PATCH /conversations/v3/conversations/threads/{threadId}
# Response is the updated thread details
UpdateThreadResponse = ThreadDetail

# DELETE /conversations/v3/conversations/threads/{threadId} returns 204 No Content
# No specific response model needed, handled by checking status code in tool.
