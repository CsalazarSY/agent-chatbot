''' Types for hubspot webhooks '''
# types/hubspot_types.py
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class HubSpotSubscriptionType(str, Enum):
    """ Defines the known HubSpot webhook subscription types we handle. """
    CONVERSATION_CREATION = "conversation.creation"
    CONVERSATION_NEW_MESSAGE = "conversation.newMessage"

class HubSpotNotification(BaseModel):
    """ Represents a single notification event within a HubSpot webhook payload. """
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
    model_config = {
        "extra": "allow"
    }

# The webhook payload is a list of these notifications
WebhookPayload = List[HubSpotNotification]
