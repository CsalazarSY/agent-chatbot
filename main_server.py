"""Main server for the AutoGen Agent API"""

# main_server.py

# System imports
import json
from typing import Optional
from contextlib import asynccontextmanager
import uvicorn
import config

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Import specific message types for reply extraction
from autogen_agentchat.messages import (
    BaseChatMessage,
    ToolCallExecutionEvent,
    TextMessage,
    ThoughtEvent,
)

# Types
from src.models.chat_api import ChatRequest, ChatResponse  # /chat endpoint
from src.models.hubspot_webhooks import (
    WebhookPayload,
    HubSpotSubscriptionType,
)  # /hubspot/webhooks endpoint


# Centralized Agent Service
from src.agents.agents_services import agent_service
from src.agents.agent_names import PLANNER_AGENT_NAME


# Import the webhook processing function and its necessary globals
from src.services.clean_agent_tags import clean_agent_output
from src.services.hubspot.webhook_handlers import (
    process_incoming_hubspot_message,
)
from src.services.hubspot.messages_filter import (
    is_conversation_handed_off,
    is_message_processed,
    add_message_to_processing,
)

# Import the refresh token service function
from src.services.redis_client import close_redis_pool, initialize_redis_pool
from src.services.sy_refresh_token import refresh_sy_token

# Import the HTML formatting service
from src.services.message_to_html import convert_message_to_html

# Print debug function
from src.services.logger_config import log_message


#  FastAPI App Setup 
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan to control the FastAPI app"""
    #  Startup
    log_message("Application Startup", level=1, prefix="--- --- ---")

    # Log critical config values now that logger is ready
    log_message(f"ChromaDB path: {config.CHROMA_DB_PATH_CONFIG}", prefix="!!!")

    try:
        # Initialize Redis Pool
        await initialize_redis_pool()

        # Trigger initial SY token refresh
        log_message("Server starting up: Triggering initial SY token refresh", level=2)
        refresh_success = await refresh_sy_token()
        if refresh_success:
            log_message("Initial SY API token refresh successful", level=2)
        else:
            log_message(
                "WARNING: Initial SY API token refresh failed. API calls will fail. !!!",
                level=1,
                log_type="warning",
            )

        yield

    finally:
        #  Shutdown 
        log_message(" Server shutting down... ")
        await close_redis_pool()


app = FastAPI(
    title="AutoGen Agent API",
    description="API endpoint to interact with the multi-agent AutoGen system.",
    lifespan=lifespan,
)

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://172.20.20.204:5173",
    "http://172.27.160.1:5173",
    "http://172.17.0.1:5173",
    "https://hubsbot.loca.lt",  # Subdomain exposed with localtunnel
    "http://hubsbot.loca.lt",  # Also allow http for localtunnel if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "*",
        "GET",
        "POST",
        "OPTIONS",
    ],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*", "Content-Type"],  # Allow all headers
)

#   API Endpoint Definition   #


#  Chat Endpoint  #
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user message and optional conversation_id, processes it via the
    centralized AgentService, handles state, and returns the reply with the
    conversation_id.
    """
    # Pass message and conversation_id to the service
    task_result, error_message, final_conversation_id = (
        await agent_service.run_chat_session(
            request.message, show_console=True, conversation_id=request.conversation_id
        )
    )

    # Handle errors reported by the service or the invocation
    if error_message:
        # Consider logging the error_message server-side
        log_message(f"Error reported: {error_message}", log_type="error", prefix="!!!")
        # If ID was missing, final_conversation_id will be None from the service
        status_code = 400 if "conversation_id is required" in error_message else 500
        raise HTTPException(
            status_code=status_code,
            detail={"message": error_message, "conversation_id": final_conversation_id},
        )

    # Handle cases where the task didn't complete successfully but didn't raise an error
    if not task_result:
        err_detail = (
            "Task finished without a result, but no specific error was reported."
        )
        log_message(err_detail, log_type="error", prefix="!!!")
        # Return error but still include the conversation ID if available
        raise HTTPException(
            status_code=500,
            detail={"message": err_detail, "conversation_id": final_conversation_id},
        )

    # Process successful result
    final_reply_content = "No final message found in result."  # Default fallback
    stop_reason = (
        str(task_result.stop_reason)
        if task_result.stop_reason
        else "Paused/Awaiting Input"
    )  # Adjust default

    #######  Process Task Result  #######
    log_message("<< Task Result >>")
    if error_message:
        log_message(
            f"Task failed with error: {error_message}",
            level=2,
            prefix="-",
            log_type="error",
        )
    elif task_result:
        log_message(f"Stop Reason: {stop_reason}", level=2, prefix="-")
        log_message(
            f"Number of Messages: {len(task_result.messages)}", level=2, prefix="-"
        )

        #  Find the message BEFORE the final 'end_planner_turn' tool call  #
        reply_message: Optional[BaseChatMessage] = None
        messages = task_result.messages
        end_turn_event_index = -1

        # First, find the index of the end_planner_turn execution event
        for i in range(len(messages) - 1, -1, -1):
            current_msg = messages[i]
            if isinstance(current_msg, ToolCallExecutionEvent):
                if any(
                    exec_result.name == "end_planner_turn"
                    for exec_result in getattr(current_msg, "content", [])
                    if hasattr(exec_result, "name")
                ):
                    end_turn_event_index = i
                    break

        # If found, search backwards from the event index for the Planner's message
        if end_turn_event_index > 0:
            for i in range(end_turn_event_index - 1, -1, -1):
                potential_reply_msg = messages[i]
                # Look for the last TextMessage or ThoughtEvent from the Planner
                if potential_reply_msg.source == PLANNER_AGENT_NAME and isinstance(
                    potential_reply_msg, (TextMessage, ThoughtEvent)
                ):
                    reply_message = potential_reply_msg
                    break  # Found the most recent relevant message

        # Fallback if the specific sequence wasn't found (should be rare)
        if not reply_message and messages:
            log_message(
                "Could not reliably find Planner message before end_turn event. Falling back to last message.",
                level=3,
                prefix="-",
                log_type="warning",
            )
            reply_message = messages[-1]
        #  End of Finding Reply Message  #

        # Extract the reply content from the identified message
        if reply_message and hasattr(reply_message, "content"):
            final_reply_content = (
                reply_message.content
                if isinstance(reply_message.content, str)
                else json.dumps(reply_message.content)
            )
            # Clean up internal tags if they are not meant for the user
            if isinstance(final_reply_content, str):
                cleaned_reply = clean_agent_output(final_reply_content)
                html_reply = await convert_message_to_html(cleaned_reply)

                final_reply_content = html_reply
        else:
            final_reply_content = (
                f"[{type(reply_message).__name__} type message found, but no content]"
                if reply_message
                else "No suitable reply message found in TaskResult."
            )

    else:
        log_message(
            "TaskResult was not obtained (task might have failed before completion or service error)",
            prefix=">>>",
            log_type="error",
        )
        final_reply_content = "An issue occurred, and no result was generated."
        # Ensure final_conversation_id is handled even in this case
        if not final_conversation_id:
            final_conversation_id = request.conversation_id or "unknown"

    #######  End of Task Result Analysis  #######

    # Return the reply, the conversation ID (crucial for continuing), and stop reason
    return ChatResponse(
        reply=final_reply_content,
        conversation_id=final_conversation_id,  # Return the ID used/generated
        stop_reason=stop_reason,
    )


#  HubSpot Webhook Endpoint  #
@app.post("/hubspot/webhooks")
async def hubspot_webhook_endpoint(
    payload: WebhookPayload, background_tasks: BackgroundTasks
):
    """
    Receives webhook events from HubSpot.
    Specifically handles 'newMessage' events for INCOMING visitor messages.
    Validates, deduplicates, and triggers background processing.
    """

    # Process individual events (assuming HubSpot might send multiple)
    # The payload *is* the list of events
    for event in payload:
        log_message(
            f"Processing Event: Type={event.subscriptionType}, Attempt={event.attemptNumber}, Event ID={event.eventId}",
            level=1,
            prefix="--- --- ---"
        )

        # Only process new message events
        if event.subscriptionType == HubSpotSubscriptionType.CONVERSATION_NEW_MESSAGE:
            conversation_id = str(event.objectId)
            message_id = str(event.messageId)

            # Input validation
            if not conversation_id or not message_id:
                log_message(
                    "Skipping event: Missing conversationId or messageId.",
                    level=2,
                    prefix="!!",
                    log_type="warning",
                )
                continue

            # Deduplication check for individual message_id
            is_processed_message = await is_message_processed(message_id)
            if is_processed_message:  # Check if True
                log_message(
                    f"Skipping processed message ID: {message_id}",
                    level=2,
                    prefix="!!",
                    log_type="warning",
                )
                continue

            # Check if the entire conversation has been handed off
            is_conversation_disabled = await is_conversation_handed_off(
                conversation_id
            )
            if is_conversation_disabled:
                log_message(
                    f"Skipping event for handed-off conversation ID: {conversation_id} (message_id: {message_id})",
                    level=2,
                    prefix="!!",
                    log_type="warning",
                )
                continue  # Skip to the next event

            # If not a duplicate message and conversation not handed off, add to processing set
            await add_message_to_processing(message_id)

            # Schedule background task to fetch details and process for the agent
            background_tasks.add_task(
                process_incoming_hubspot_message,
                conversation_id=conversation_id,
                message_id=message_id,
            )

    # Return 200 OK immediately for HubSpot webhook best practice
    return {"statusCode": 200, "status": "Webhook received and processing initiated"}


#   Run the Server (for local development)   #
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
