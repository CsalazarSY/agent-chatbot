# Models package - exports all data models for the agent chatbot
from .chat_api import ChatRequest, ChatResponse
from .hubspot_webhooks import (
    HubSpotSubscriptionType,
    TicketPropertyChangePayload,
    HubSpotNotification,
    ChatWebhookPayload,
    TicketPropertyChangeWebhookPayload
)

# Also export the modules themselves for backward compatibility
from . import chat_api
from . import hubspot_webhooks

__all__ = [
    # Chat API models
    "ChatRequest",
    "ChatResponse",
    
    # HubSpot webhook models
    "HubSpotSubscriptionType",
    "TicketPropertyChangePayload", 
    "HubSpotNotification",
    "ChatWebhookPayload",
    "TicketPropertyChangeWebhookPayload",
    
    # Module exports for backward compatibility
    "chat_api",
    "hubspot_webhooks"
]