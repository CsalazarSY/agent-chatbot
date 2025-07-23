"""Types for hubspot webhooks"""

# /src/models/hubspot_webhooks.py
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, field_validator


class HubSpotSubscriptionType(str, Enum):
    """Defines the known HubSpot webhook subscription types we handle."""

    CONVERSATION_CREATION = "conversation.creation"
    CONVERSATION_NEW_MESSAGE = "conversation.newMessage"


class HubSpotAssignmentPayload(BaseModel):
    """Represents the payload for HubSpot assignment webhook events."""
    
    was_assigned: bool
    owner_availability: str
    hubspot_owner_id: Union[int, str, None] = None  # Can be null, empty string, or int
    type_of_ticket: str
    contact_owner: Optional[int] = None
    msg: str  # Message indicating the assignment scenario

    hs_object_id: int
    hs_pipeline_stage: int
    hs_pipeline: int
    hs_ticket_id: int
    hs_thread_id: int
    
    @field_validator('hubspot_owner_id', mode='before')
    @classmethod
    def validate_hubspot_owner_id(cls, v):
        """Convert empty string to None, keep int values as is"""
        if v == "" or v is None:
            return None
        return v
    
    # Allow extra fields not explicitly defined
    model_config = {"extra": "allow"}


class HubSpotNotification(BaseModel):
    """Represents a single notification event within a HubSpot webhook payload."""

    objectId: int
    propertyName: Optional[str] = None
    propertyValue: Optional[str] = None
    changeSource: Optional[str] = None
    eventId: int
    subscriptionId: int
    portalId: int
    appId: int
    occurredAt: int
    subscriptionType: HubSpotSubscriptionType
    attemptNumber: int

    # Field for conversation.creation
    changeFlag: Optional[str] = None

    # Fields for conversation.newMessage
    messageId: Optional[str] = None
    messageType: Optional[str] = None

    # Allow extra fields not explicitly defined
    model_config = {"extra": "allow"}


# The webhook payload is a list of these notifications
WebhookPayload = List[HubSpotNotification]
