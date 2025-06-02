"""
Manages filters for HubSpot messages, including tracking messages currently being processed
and conversations that have been handed off and should be skipped.
"""

# /src/services/hubspot_webhooks/messages_filter.py

import asyncio
from typing import Set

# --- Global In-Memory Stores ---
# Stores message_ids currently being processed to prevent duplicate processing.
PROCESSED_MESSAGES: Set[str] = set()
MESSAGE_ID_LOCK = asyncio.Lock()

# Stores conversation_ids that have been marked as handed off (e.g., an "Issue" ticket was created).
# Messages from these conversations should typically be skipped.
HANDED_OFF_CONVERSATIONS: Set[str] = set()
HANDED_OFF_CONVERSATIONS_LOCK = asyncio.Lock()


# --- Message ID Processing Helpers ---
async def is_message_processed(message_id: str) -> bool:
    """Checks if a message_id is currently in the processing set."""
    async with MESSAGE_ID_LOCK:
        return message_id in PROCESSED_MESSAGES


async def add_message_to_processing(message_id: str):
    """Adds a message_id to the processing set."""
    async with MESSAGE_ID_LOCK:
        PROCESSED_MESSAGES.add(message_id)


async def remove_message_from_processing(message_id: str):
    """Removes a message_id from the processing set."""
    async with MESSAGE_ID_LOCK:
        PROCESSED_MESSAGES.discard(message_id)


# --- Handed-Off Conversation Helpers ---
async def is_conversation_handed_off(conversation_id: str):
    """Checks if a conversation_id is in the handed-off set."""
    async with HANDED_OFF_CONVERSATIONS_LOCK:
        return conversation_id in HANDED_OFF_CONVERSATIONS


async def add_conversation_to_handed_off(conversation_id: str):
    """Adds a conversation_id to the handed-off set."""
    async with HANDED_OFF_CONVERSATIONS_LOCK:
        HANDED_OFF_CONVERSATIONS.add(conversation_id)


async def remove_conversation_from_handed_off(conversation_id: str):
    """Removes a conversation_id from the handed-off set (e.g., if it needs to be re-activated)."""
    async with HANDED_OFF_CONVERSATIONS_LOCK:
        HANDED_OFF_CONVERSATIONS.discard(conversation_id)
