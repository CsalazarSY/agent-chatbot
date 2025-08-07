"""Types for hubspot webhooks"""

# /src/models/hubspot_webhooks.py
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, field_validator


class HubSpotSubscriptionType(str, Enum):
    """Defines the known HubSpot webhook subscription types we handle."""

    CONVERSATION_CREATION = "conversation.creation"
    CONVERSATION_NEW_MESSAGE = "conversation.newMessage"
    OBJECT_PROPERTY_CHANGE = "object.propertyChange"

class TicketPropertyChangePayload(BaseModel):
    """Represents the payload for HubSpot ticket property change webhook events."""
    
    eventId: int
    subscriptionId: int
    portalId: int
    appId: int
    occurredAt: int
    subscriptionType: str  # Will be "object.propertyChange"
    attemptNumber: int
    objectId: int # The ticket ID
    objectTypeId: str  # e.g., "0-5" for tickets
    propertyName: str
    propertyValue: str
    changeSource: str
    sourceId: Optional[str] = None
    isSensitive: bool
    
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
ChatWebhookPayload = List[HubSpotNotification]

# The ticket property change webhook payload is a list of ticket property change events
TicketPropertyChangeWebhookPayload = List[TicketPropertyChangePayload]
