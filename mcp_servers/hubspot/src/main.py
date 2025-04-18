import os
import asyncio
import traceback
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from hubspot import HubSpot

# Import utilities
from utils import hubspot_config, create_hubspot_client

# Load environment variables
load_dotenv()

# --- HubSpot Client Context --- #
@dataclass
class HubSpotContext:
    """Context holding the initialized HubSpot client and config."""
    hubspot_client: Optional[HubSpot]
    config: dict

@asynccontextmanager
async def hubspot_lifespan(server: FastMCP) -> AsyncIterator[HubSpotContext]:
    """Manages the HubSpot client lifecycle."""
    client: Optional[HubSpot] = None
    cfg = hubspot_config
    if cfg.get("api_token"):
        try:
            client = create_hubspot_client(cfg["api_token"])
        except ValueError as e:
            # print(f"HubSpot Lifespan Error: {e}") 
            pass # Client remains None, tools should handle this
    else:
        # print("HubSpot Lifespan Warning: HUBSPOT_API_TOKEN not found. HubSpot tools will fail.") 
        pass

    try:
        yield HubSpotContext(hubspot_client=client, config=cfg)
    finally:
        # No explicit cleanup needed for the HubSpot client instance
        # print("HubSpot Lifespan: Shutdown complete.") 
        pass

# --- Initialize FastMCP Server --- #
mcp = FastMCP(
    "mcp-hubspot",
    description="MCP server for interacting with HubSpot conversations.",
    lifespan=hubspot_lifespan,
    host=os.getenv("HOST", "0.0.0.0"), # For SSE
    port=int(os.getenv("PORT", "8051")) # Default port 8051 for HubSpot server
)

# --- Tool Definition --- #
@mcp.tool(name="send_message_to_thread")
async def hubspot_send_message(
    ctx: Context,
    thread_id: str,
    message_text: str,
    channel_id: Optional[str] = None,
    channel_account_id: Optional[str] = None,
    sender_actor_id: Optional[str] = None,
) -> str:
    """Sends a message or comment to a HubSpot conversation thread.

    If the message_text contains 'HANDOFF' or 'COMMENT' (case-insensitive), it sends the message
    as an internal COMMENT, otherwise it sends it as a regular MESSAGE.

    Args:
        ctx: The MCP server context containing the HubSpot client and config.
        thread_id: The HubSpot conversation thread ID.
        message_text: The content of the message/comment to send.
        channel_id: Optional. The channel ID (e.g., '1000' for chat). Uses default from env if None.
        channel_account_id: Optional. The specific channel account ID (e.g., chatflow ID). Uses default from env if None.
        sender_actor_id: Optional. The HubSpot Actor ID (e.g., "A-12345") posting the message/comment. Uses default from env if None.

    Returns:
        A success or failure message string (e.g., "HUBSPOT_TOOL_SUCCESS:..." or "HUBSPOT_TOOL_FAILED:...").
    """
    # print(f"\n--- MCP Tool: send_message_to_thread --- Called")
    # Retrieve client and config from context
    hubspot_context: HubSpotContext = ctx.request_context.lifespan_context
    client = hubspot_context.hubspot_client
    config = hubspot_context.config

    # Use provided args or fall back to config defaults
    final_channel_id = channel_id or config.get("default_channel")
    final_channel_account_id = channel_account_id or config.get("default_channel_account")
    final_sender_actor_id = sender_actor_id or config.get("default_sender_actor_id")

    # print(f"    Thread ID: {thread_id}")
    # print(f"    Channel ID: {final_channel_id}")
    # print(f"    Account ID: {final_channel_account_id}")
    # print(f"    Actor ID: {final_sender_actor_id}")
    # --- Input Validation (copied from original tool) --- #
    if not client:
        # print("    ERROR: HubSpot client not initialized in context.")
        return "HUBSPOT_TOOL_FAILED: HubSpot client is not initialized."
    if not thread_id or not isinstance(thread_id, str) or thread_id.lower() == 'unknown':
        # print("    ERROR: Invalid thread_id.") 
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot thread ID was not provided."
    if not final_channel_id or not isinstance(final_channel_id, str):
        # print("    ERROR: Invalid channel_id.") 
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel ID was not provided."
    if not final_channel_account_id or not isinstance(final_channel_account_id, str):
        # print("    ERROR: Invalid channel_account_id.") 
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot channel account ID was not provided."
    if not final_sender_actor_id or not isinstance(final_sender_actor_id, str):
        # print("    ERROR: Invalid sender_actor_id.") 
        return "HUBSPOT_TOOL_FAILED: Valid HubSpot sender actor ID was not provided."
    if not final_sender_actor_id.startswith("A-"):
        # print(f"    Warning: sender_actor_id '{final_sender_actor_id}' might not be a valid Agent Actor ID.") 
        pass # Just a warning, proceed
    if not message_text or not isinstance(message_text, str):
        # print("    ERROR: Invalid message_text.") 
        return "HUBSPOT_TOOL_FAILED: Valid message text was not provided."

    # --- Determine Message Type --- #
    message_type = "MESSAGE"
    if "HANDOFF" in message_text.upper() or "COMMENT" in message_text.upper():
        message_type = "COMMENT"
    # print(f"    Determined Message Type: {message_type}") 

    # --- API Call --- #
    api_path = f"/conversations/v3/conversations/threads/{thread_id}/messages"
    payload = {
        "type": message_type,
        "text": message_text,
        "senderActorId": final_sender_actor_id,
        "channelId": final_channel_id,
        "channelAccountId": final_channel_account_id,
    }
    request_data = {
        "method": "POST",
        "path": api_path,
        "body": payload
    }

    try:
        # print(f"    Attempting API call to {api_path}...") 
        # Use asyncio.to_thread for the synchronous SDK call
        await asyncio.to_thread(
            client.api_request,
            request_data 
        )
        # print(f"--- MCP Tool: send_message_to_thread - finished (Success) ---\n") 
        return f"HUBSPOT_TOOL_SUCCESS: Message successfully sent to thread {thread_id}."

    except Exception as e:
        # print(f"\n    ERROR calling HubSpot API: {e}") 
        # traceback.print_exc() # Avoid printing traceback to stdio
        # print(f"--- MCP Tool: send_message_to_thread - finished (Error) ---\n") 
        # Attempt to extract a more specific error from HubSpot exception if possible
        error_details = str(e)
        # Consider checking for specific HubSpot error types if the library provides them
        return f"HUBSPOT_TOOL_FAILED: Error communicating with HubSpot API: {error_details}"

# --- Main Execution Block --- #
async def main():
    transport = os.getenv("TRANSPORT", "stdio").lower()
    # print(f"Starting HubSpot MCP Server with {transport} transport...") 
    if transport == 'sse':
        await mcp.run_sse_async()
    elif transport == 'stdio':
        await mcp.run_stdio_async()
    else:
        # print(f"Error: Invalid TRANSPORT specified: {transport}. Use 'stdio' or 'sse'.") 
        pass # Or raise an error

if __name__ == "__main__":
    # Ensure event loop policy is set for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
