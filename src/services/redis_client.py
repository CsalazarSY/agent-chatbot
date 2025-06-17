"""Manages the connection to the Redis cache."""

import redis.asyncio as redis
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

# This will hold the connection pool.
redis_pool = None


async def initialize_redis_pool():
    """Initializes the Redis connection pool."""
    global redis_pool
    if redis_pool is None:
        print("--- Initializing Redis connection pool... ---")
        try:
            # Construct the redis URL with 'rediss://' for SSL connections
            redis_url = f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
            redis_pool = redis.ConnectionPool.from_url(
                redis_url,
                decode_responses=True,  # Decode responses to strings
                max_connections=20,
            )
            # Test the connection
            client = redis.Redis(connection_pool=redis_pool)
            await client.ping()
            print("--- Redis connection pool initialized successfully. ---")
        except Exception as e:
            print(f"!!! CRITICAL: Failed to initialize Redis connection pool: {e}")
            redis_pool = None  # Ensure it's None on failure
            raise


async def close_redis_pool():
    """Closes the Redis connection pool."""
    global redis_pool
    if redis_pool:
        print("--- Closing Redis connection pool... ---")
        await redis_pool.disconnect()
        redis_pool = None


@asynccontextmanager
async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Provides a Redis connection from the pool."""
    if redis_pool is None:
        raise ConnectionError(
            "Redis pool is not initialized. Call initialize_redis_pool() first."
        )

    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        # The connection is returned to the pool automatically by the client
        pass
