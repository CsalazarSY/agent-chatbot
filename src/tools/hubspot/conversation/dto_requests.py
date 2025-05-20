""" Pydantic models for HubSpot Conversations API **request** bodies. """
# /src/tools/hubspot/conversation/sdto_requests.py
from typing import Optional, List
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

class MessageAttachmentRequest(BaseModel):
    """Represents an attachment to be sent with a message."""
    # Structure based on common attachment patterns, adjust if HubSpot spec differs.
    # The Postman collection shows attachments: [] - doesn't define structure.
    # Assuming basic structure for now. Needs verification if attachments are used.
    id: Optional[str] = Field(None, description="ID of the attachment (if already uploaded).")
    name: Optional[str] = Field(None, description="Filename of the attachment.")
    # content: Optional[bytes] = Field(None, description="File content (if uploading directly).") # Usually handled differently

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
    attachments: Optional[List[MessageAttachmentRequest]] = Field(None, description="List of attachments for the message.") # Assuming empty list if none

# PATCH /conversations/v3/conversations/threads/{threadId}
class UpdateThreadRequest(BaseModel):
    """Request body for updating a thread's status or archive state."""
    status: Optional[str] = Field(None, description="New status for the thread ('OPEN' or 'CLOSED').")
    archived: Optional[bool] = Field(None, description="Set to False to restore an archived thread, True to archive (though DELETE is preferred for archiving).")
