""" Main server for the AutoGen Agent API """
# main_server.py

# System imports
from contextlib import asynccontextmanager
import json
import uvicorn

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Types
from src.models.chat_api import ChatRequest, ChatResponse # /chat endpoint
from src.models.hubspot_webhooks import WebhookPayload, HubSpotSubscriptionType # /hubspot/webhooks endpoint

# Centralized Agent Service
from src.agents.agents_services import agent_service

# Import config module and the trigger function
import config

# Import the webhook processing function and its necessary globals
from src.services.hubspot_webhook_handler import (
    clean_agent_output,
    process_incoming_hubspot_message,
    PROCESSING_MESSAGE_IDS,
    message_id_lock
)

# --- FastAPI App Setup ---
@asynccontextmanager
async def lifespan(_: FastAPI):
    """ Lifespan to control the FastAPI app """
    # Code to run on startup
    print("--- Server starting up: Triggering initial SY token refresh via config... ---")
    # Call the trigger function in config
    refresh_success = await config.trigger_sy_token_refresh()
    if refresh_success:
        print("--- Initial SY API token refresh successful (triggered via config). ---")
    else:
        # Token is None in config.SY_API_AUTH_TOKEN_DYNAMIC
        print("!!! WARNING: Initial SY API token refresh failed (triggered via config). API calls requiring token will fail until refreshed. !!!")
    yield
    # Code to run on shutdown (if needed)
    print("--- Server shutting down... ---")

app = FastAPI(
    title="AutoGen Agent API",
    description="API endpoint to interact with the multi-agent AutoGen system.",
    lifespan=lifespan
)

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://172.20.20.204:5173",
    "http://172.27.160.1:5173",
    "http://172.17.0.1:5173",  
    "https://hubsbot.loca.lt", # Subdomain exposed with localtunnel
    "http://hubsbot.loca.lt"   # Also allow http for localtunnel if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*", "GET", "POST", "OPTIONS"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*", "Content-Type"], # Allow all headers
)

# --- --- API Endpoint Definition --- --- #

# --- Chat Endpoint --- #
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user message and optional conversation_id, processes it via the
    centralized AgentService, handles state, and returns the reply with the
    conversation_id.
    """
    # Pass message and conversation_id to the service
    task_result, error_message, final_conversation_id = await agent_service.run_chat_session(
        request.message,
        show_console=True,
        conversation_id=request.conversation_id
    )

    # Handle errors reported by the service or the invocation
    if error_message:
        # Consider logging the error_message server-side
        print(f"!!! Error reported: {error_message}")
        # If ID was missing, final_conversation_id will be None from the service
        status_code = 400 if "conversation_id is required" in error_message else 500
        raise HTTPException(
            status_code=status_code,
            detail={"message": error_message, "conversation_id": final_conversation_id}
        )

    # Handle cases where the task didn't complete successfully but didn't raise an error
    if not task_result:
        err_detail = "Task finished without a result, but no specific error was reported."
        print(f"!!! {err_detail}")
        # Return error but still include the conversation ID if available
        raise HTTPException(status_code=500, detail={"message": err_detail, "conversation_id": final_conversation_id})

    # Process successful result
    final_reply_content = "No final message found in result." # Default fallback
    stop_reason = str(task_result.stop_reason) if task_result.stop_reason else "Paused/Awaiting Input" # Adjust default

    ####### --- Process Task Result --- #######
    print("\n\n\n<< Task Result >>")
    if error_message:
        print(f"          - Task failed with error: {error_message}")
    elif task_result:
        print(f"          - Stop Reason: {stop_reason}")
        print(f"          - Number of Messages: {len(task_result.messages)}")

        # Extract the last message's content for the reply
        if task_result.messages:
            last_message = task_result.messages[-1] # Get the last message object
            # Extract content safely, handling different message types
            if hasattr(last_message, 'content'):
                final_reply_content = (
                    last_message.content
                    if isinstance(last_message.content, str)
                    else json.dumps(last_message.content)
                 )
                 # Clean up internal tags if they are not meant for the user
                if isinstance(final_reply_content, str):
                    final_reply_content = clean_agent_output(final_reply_content)
            else:
                final_reply_content = f"[{type(last_message).__name__} type message received]" # More informative default
        else:
            print(">>> No messages found in TaskResult. <<<")
            final_reply_content = "The conversation generated no messages."
    else:
        print(">>> TaskResult was not obtained (task might have failed before completion or service error) <<<")
        final_reply_content = "An issue occurred, and no result was generated."
        # Ensure final_conversation_id is handled even in this case
        if not final_conversation_id: final_conversation_id = request.conversation_id or "unknown"

    ####### --- End of Task Result Analysis --- #######

    # Return the reply, the conversation ID (crucial for continuing), and stop reason
    return ChatResponse(
        reply=final_reply_content,
        conversation_id=final_conversation_id, # Return the ID used/generated
        stop_reason=stop_reason
    )

# --- HubSpot Webhook Endpoint --- #
@app.post("/hubspot/webhooks")
async def hubspot_webhook_endpoint(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Receives webhook events from HubSpot.
    Specifically handles 'newMessage' events for INCOMING visitor messages.
    Validates, deduplicates, and triggers background processing.
    """
    print("\n--- HubSpot Webhook Received ---")
    print(f"    - Payload: {payload}")

    # Process individual events (assuming HubSpot might send multiple)
    for event in payload.events:
        print(f" -> Processing Event: Type={event.subscriptionType}, Attempt={event.attemptNumber}, ID={event.eventId}")

        # Only process new message events
        if event.subscriptionType == HubSpotSubscriptionType.CONVERSATION_NEW_MESSAGE:
            conversation_id = event.objectId
            message_id = event.messageId

            # Input validation
            if not conversation_id or not message_id:
                print("    !! Skipping event: Missing conversationId or messageId.")
                continue

            print(f"    - New message event: ConvID={conversation_id}, MsgID={message_id}")

            # Deduplication check
            async with message_id_lock:
                if message_id in PROCESSING_MESSAGE_IDS:
                    print(f"    -- Skipping duplicate message ID: {message_id}")
                    continue
                else:
                    print(f"    -- Adding message ID {message_id} to processing set.")
                    PROCESSING_MESSAGE_IDS.add(message_id)

            # Schedule background task to fetch details and process
            print(f"    -> Scheduling background task for message {message_id} in thread {conversation_id}")
            background_tasks.add_task(
                process_incoming_hubspot_message,
                conversation_id=conversation_id,
                message_id=message_id
            )

        else:
            print(f"    - Skipping event type: {event.subscriptionType}")

    # Return 200 OK immediately for HubSpot webhook best practice
    return {"status": "Webhook received and processing initiated"}

# --- --- Run the Server (for local development) --- --- #
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
