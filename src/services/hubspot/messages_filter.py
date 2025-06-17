"""
Manages filters for HubSpot messages using Redis, including tracking processed messages
and handed-off conversations.
"""

from src.services.redis_client import get_redis_client

# Define the keys we will use in Redis
PROCESSED_MESSAGES_KEY = "hubspot:processed_messages"
HANDED_OFF_CONVERSATIONS_KEY = "hubspot:handed_off_conversations"

# Expiry times in seconds
MESSAGE_EXPIRY_SECONDS = 2 * 60 * 60  # 2 hours
CONVERSATION_EXPIRY_SECONDS = 72 * 60 * 60  # 72 hours


# --- Message ID Processing Helpers ---
async def is_message_processed(message_id: str) -> bool:
    """Checks if a message_id is in the Redis processing set."""
    async with get_redis_client() as redis:
        return await redis.sismember(PROCESSED_MESSAGES_KEY, message_id)


async def add_message_to_processing(message_id: str):
    """Adds a message_id to the Redis processing set.
    We can set an expiry time (e.g., 1 hour) to auto-clean old message IDs.
    """
    async with get_redis_client() as redis:
        await redis.sadd(PROCESSED_MESSAGES_KEY, message_id)
        # Refresh the expiration on the set each time we add a message
        await redis.expire(PROCESSED_MESSAGES_KEY, MESSAGE_EXPIRY_SECONDS)


async def remove_message_from_processing(message_id: str):
    """Removes a message_id from the Redis processing set."""
    async with get_redis_client() as redis:
        await redis.srem(PROCESSED_MESSAGES_KEY, message_id)


# --- Handed-Off Conversation Helpers ---
async def is_conversation_handed_off(conversation_id: str) -> bool:
    """Checks if a conversation_id is in the Redis handed-off set."""
    async with get_redis_client() as redis:
        return await redis.sismember(HANDED_OFF_CONVERSATIONS_KEY, conversation_id)


async def add_conversation_to_handed_off(conversation_id: str):
    """Adds a conversation_id to the Redis handed-off set."""
    async with get_redis_client() as redis:
        await redis.sadd(HANDED_OFF_CONVERSATIONS_KEY, conversation_id)
        # Refresh the expiration on the set each time we add a conversation
        await redis.expire(HANDED_OFF_CONVERSATIONS_KEY, CONVERSATION_EXPIRY_SECONDS)


async def remove_conversation_from_handed_off(conversation_id: str):
    """Removes a conversation_id from the Redis handed-off set."""
    async with get_redis_client() as redis:
        await redis.srem(HANDED_OFF_CONVERSATIONS_KEY, conversation_id)
