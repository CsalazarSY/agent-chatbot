"""Types for hubspot webhooks"""

# /src/models/hubspot_webhooks.py
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


class HubSpotSubscriptionType(str, Enum):
    """Defines the known HubSpot webhook subscription types we handle."""

    CONVERSATION_CREATION = "conversation.creation"
    CONVERSATION_NEW_MESSAGE = "conversation.newMessage"


class HubSpotAssignmentPayload(BaseModel):
    """Represents the payload for HubSpot assignment webhook events."""
    
    was_assigned: bool
    owner_availability: Optional[str] = None
    hubspot_owner_id: Optional[int] = None  # Can be null if not assigned
    type_of_ticket: str
    contact_owner: Optional[int] = None

    hs_object_id: int
    hs_pipeline_stage: int
    hs_pipeline: int
    hs_ticket_id: int
    hs_thread_id: int
    
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
