''' Pydantic models for HubSpot Conversations API responses. '''
# agents/hubspot/types/hubspot_api_types.py

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# --- Base/Common Models ---

class DeliveryIdentifier(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None

class PagingNext(BaseModel):
    link: Optional[str] = None
    after: Optional[str] = None

class Paging(BaseModel):
    next: Optional[PagingNext] = None

class MessageStatusFailureDetails(BaseModel):
    errorMessageTokens: Optional[Dict[str, str]] = None
    errorMessage: Optional[str] = None

class MessageStatus(BaseModel):
    statusType: Optional[str] = None # e.g., SENT, FAILED
    failureDetails: Optional[MessageStatusFailureDetails] = None

class ClientInfo(BaseModel):
    clientType: Optional[str] = None # e.g., HUBSPOT
    integrationAppId: Optional[int] = None

class MessageSender(BaseModel):
    actorId: Optional[str] = None
    name: Optional[str] = None
    senderField: Optional[str] = None
    deliveryIdentifier: Optional[DeliveryIdentifier] = None

class MessageRecipient(BaseModel):
    actorId: Optional[str] = None
    name: Optional[str] = None
    deliveryIdentifier: Optional[DeliveryIdentifier] = None # Note: Can be null
    recipientField: Optional[str] = None

class ThreadAssociations(BaseModel):
    # Using Field alias for potential snake_case conversion if needed later
    associatedTicketId: Optional[str] = Field(None, alias="associatedTicketId")
    # Add other potential associations if known

class ActorType(str, Enum):
    AGENT = "AGENT"
    BOT = "BOT"
    # Add others if necessary

class Actor(BaseModel):
    type: Optional[ActorType] = None
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None

class ChannelAccount(BaseModel):
    createdAt: Optional[datetime] = None
    archivedAt: Optional[datetime] = None
    archived: Optional[bool] = None
    authorized: Optional[bool] = None
    name: Optional[str] = None
    active: Optional[bool] = None
    deliveryIdentifier: Optional[DeliveryIdentifier] = None
    id: str
    inboxId: Optional[str] = None
    channelId: Optional[str] = None

class Channel(BaseModel):
    name: Optional[str] = None
    id: str

class InboxType(str, Enum):
    HELP_DESK = "HELP_DESK"
    INBOX = "INBOX"

class Inbox(BaseModel):
    createdAt: Optional[datetime] = None
    archivedAt: Optional[datetime] = None
    archived: Optional[bool] = None
    name: Optional[str] = None
    id: str
    type: Optional[InboxType] = None
    updatedAt: Optional[datetime] = None

class MessageType(str, Enum):
    MESSAGE = "MESSAGE"
    COMMENT = "COMMENT"
    WELCOME_MESSAGE = "WELCOME_MESSAGE"
    SYSTEM = "SYSTEM"

class MessageTruncationStatus(str, Enum):
    TRUNCATED = "TRUNCATED"
    NOT_TRUNCATED = "NOT_TRUNCATED"

class MessageDirection(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"

class MessageDetail(BaseModel):
    type: Optional[MessageType] = None
    id: str
    conversationsThreadId: Optional[str] = Field(None, alias="conversationsThreadId")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    client: Optional[ClientInfo] = None
    senders: Optional[List[MessageSender]] = None
    recipients: Optional[List[MessageRecipient]] = None
    archived: Optional[bool] = None
    text: Optional[str] = None
    richText: Optional[str] = None
    attachments: Optional[List[Any]] = None # Define specific attachment model if structure known
    subject: Optional[str] = None
    truncationStatus: Optional[MessageTruncationStatus] = None
    inReplyToId: Optional[str] = None
    status: Optional[MessageStatus] = None
    direction: Optional[MessageDirection] = None
    channelId: Optional[str] = None
    channelAccountId: Optional[str] = None

class ThreadStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    # Add others if necessary

class ThreadDetail(BaseModel):
    associatedContactId: Optional[str] = Field(None, alias="associatedContactId")
    threadAssociations: Optional[ThreadAssociations] = None
    assignedTo: Optional[str] = None # Actor ID
    createdAt: Optional[datetime] = None
    archived: Optional[bool] = None
    originalChannelId: Optional[str] = None
    latestMessageTimestamp: Optional[datetime] = None
    latestMessageSentTimestamp: Optional[datetime] = None
    originalChannelAccountId: Optional[str] = None
    id: str
    closedAt: Optional[datetime] = None
    spam: Optional[bool] = None
    inboxId: Optional[str] = None
    status: Optional[ThreadStatus] = None
    latestMessageReceivedTimestamp: Optional[datetime] = None

# --- Specific Endpoint Response Models ---

# GET /conversations/v3/conversations/actors/{actorId}
ActorDetailResponse = Actor # Reuse base model

# GET /conversations/v3/conversations/channel-accounts/{channelAccountId}
ChannelAccountDetailResponse = ChannelAccount # Reuse base model

# GET /conversations/v3/conversations/channels/{channelId}
ChannelDetailResponse = Channel # Reuse base model

# GET /conversations/v3/conversations/inboxes/{inboxId}
InboxDetailResponse = Inbox # Reuse base model

# GET /conversations/v3/conversations/threads/{threadId}/messages/{messageId}
MessageDetailResponse = MessageDetail # Reuse base model

# GET /conversations/v3/conversations/threads/{threadId}
ThreadDetailResponse = ThreadDetail # Reuse base model

# GET /conversations/v3/conversations/channel-accounts
class ListChannelAccountsResponse(BaseModel):
    total: Optional[int] = None
    paging: Optional[Paging] = None
    results: List[ChannelAccount]

# GET /conversations/v3/conversations/channels
class ListChannelsResponse(BaseModel):
    total: Optional[int] = None
    paging: Optional[Paging] = None
    results: List[Channel]

# GET /conversations/v3/conversations/inboxes
class ListInboxesResponse(BaseModel):
    total: Optional[int] = None
    paging: Optional[Paging] = None
    results: List[Inbox]

# GET /conversations/v3/conversations/threads/{threadId}/messages
class ListMessagesResponse(BaseModel):
    paging: Optional[Paging] = None
    results: List[MessageDetail] # Messages might be empty, so allow empty list

# GET /conversations/v3/conversations/threads/{threadId}/messages/{messageId}/original-content
class OriginalMessageContentResponse(BaseModel):
    text: Optional[str] = None
    richText: Optional[str] = None

# GET /conversations/v3/conversations/threads
class ListThreadsResponse(BaseModel):
    paging: Optional[Paging] = None
    results: List[ThreadDetail]

# POST /conversations/v3/conversations/actors/batch/read
class BatchReadResponse(BaseModel): # Simplified representation
    completedAt: Optional[datetime] = None
    requestedAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    links: Optional[Dict[str, str]] = None
    results: List[Actor]
    status: Optional[str] = None # e.g., PENDING, COMPLETE

# POST /conversations/v3/conversations/threads/{threadId}/messages
# Response is the created message details
CreateMessageResponse = MessageDetail # Reuse base model

# PATCH /conversations/v3/conversations/threads/{threadId}
# Response is the updated thread details
UpdateThreadResponse = ThreadDetail # Reuse base model

# DELETE /conversations/v3/conversations/threads/{threadId} returns 204 No Content
# No specific response model needed, handled by checking status code in tool. 