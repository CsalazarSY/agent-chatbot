""" Pydantic models for HubSpot Conversations API **request** bodies. """
# /src/tools/hubspot/conversation/sdto_requests.py
from typing import Optional, List, Union
from pydantic import BaseModel, Field

# --- Base/Common Models (used in requests) ---

class DeliveryIdentifier(BaseModel):
    """Identifies how a message is delivered (e.g., EMAIL, HS_EMAIL_ADDRESS)."""
    type: Optional[str] = Field(None, description="The type of the delivery identifier (e.g., 'EMAIL').")
    value: Optional[str] = Field(None, description="The value of the delivery identifier (e.g., 'test@example.com').")

class MessageRecipientRequest(BaseModel):
    """Represents a recipient in a message request.""" 
    actorId: Optional[str] = Field(None, description="Optional HubSpot actor ID for the recipient.")
    name: Optional[str] = Field(None, description="Optional name for the recipient.")
    recipientField: Optional[str] = Field(None, description="Specifies the recipient field (e.g., 'TO', 'CC').")
    deliveryIdentifier: Optional[DeliveryIdentifier] = Field(None, description="Primary delivery identifier for the recipient.")

# --- Attachment Models ---

class QuickReplyOption(BaseModel):
    """Defines a single quick reply option."""
    valueType: str = Field(..., description="A type identifier for the value, can be used by the client.")
    label: str = Field(..., description="The text displayed on the quick reply button.")
    value: str = Field(..., description="The value sent back when the quick reply is clicked.")

class QuickReplyAttachment(BaseModel):
    """Represents a quick replies attachment."""
    type: str = Field("QUICK_REPLIES", description="The type of attachment, fixed to QUICK_REPLIES.")
    quickReplies: List[QuickReplyOption] = Field(..., description="A list of quick reply options.")

class FileUploadAttachment(BaseModel):
    """Represents a file attachment."""
    type: str = Field("FILE", description="The type of attachment, fixed to FILE.")
    fileId: str = Field(..., description="The ID of the uploaded file in HubSpot.")
    name: Optional[str] = Field(None, description="The name of the file.")
    fileUsageType: Optional[str] = Field(None, description="Usage type like IMAGE, DOCUMENT etc.") # e.g. IMAGE
    url: Optional[str] = Field(None, description="The URL to access the file.")

# --- Specific Endpoint Request Models ---

# POST /conversations/v3/conversations/actors/batch/read
class BatchReadActorsRequest(BaseModel):
    """Request body for batch reading actor details."""
    inputs: List[str] = Field(..., description="A list of actor IDs to retrieve.")

# POST /conversations/v3/conversations/threads/{threadId}/messages
class CreateMessageRequest(BaseModel):
    """Request body for sending a message or comment to a thread."""
    type: str = Field(..., description="The type of message ('MESSAGE' or 'COMMENT').")
    text: str = Field(..., description="The plain text content of the message.")
    richText: Optional[str] = Field(None, description="The rich text (HTML) content of the message.")
    subject: Optional[str] = Field(None, description="The subject line, primarily for email messages.")
    senderActorId: str = Field(..., description="The HubSpot Actor ID (e.g., 'A-xxxxx') sending the message.")
    channelId: str = Field(..., description="The ID of the channel (e.g., 'EMAIL', 'CRM_UI').")
    channelAccountId: str = Field(..., description="The specific account ID within the channel (e.g., an email integration ID or chatflow ID).")
    recipients: Optional[List[MessageRecipientRequest]] = Field(None, description="List of recipients for the message (primarily for 'MESSAGE' type).")
    attachments: Optional[List[Union[QuickReplyAttachment, FileUploadAttachment]]] = Field(None, description="List of attachments, which can be quick replies or files.")

# PATCH /conversations/v3/conversations/threads/{threadId}
class UpdateThreadRequest(BaseModel):
    """Request body for updating a thread's status or archive state."""
    status: Optional[str] = Field(None, description="New status for the thread ('OPEN' or 'CLOSED').")
    archived: Optional[bool] = Field(None, description="Set to False to restore an archived thread, True to archive (though DELETE is preferred for archiving).")
