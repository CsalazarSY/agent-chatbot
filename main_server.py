"""Main server for the AutoGen Agent API"""

# main_server.py

from fastapi import WebSocket, WebSocketDisconnect

# System imports
from contextlib import asynccontextmanager
from src.tools.hubspot.conversation.conversation_tools import get_thread_details
import uvicorn
import config

# FastAPI imports
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware

# Import specific message types for reply extraction

# Types
from src.models.hubspot_webhooks import (
    WebhookPayload,
    HubSpotSubscriptionType,
    HubSpotAssignmentPayload,
)  # /hubspot/webhooks endpoint


# Centralized Agent Service


# Import the webhook processing function and its necessary globals
from src.services.hubspot.webhook_handlers import (
    process_incoming_hubspot_message,
)
from src.services.hubspot.webhook_assign_signal import (
    process_assignment_webhook,
)
from src.services.hubspot.messages_filter import (
    is_conversation_handed_off,
    is_message_processed,
    add_message_to_processing,
)

# Import the refresh token service function
from src.services.redis_client import close_redis_pool, initialize_redis_pool
from src.services.sy_refresh_token import refresh_sy_token
from src.services.chromadb.client_manager import initialize_chroma_client, close_chroma_client

# Import the HTML formatting service

# Print debug function
from src.services.logger_config import log_message

# --- WebSocket Connection Manager ---
from src.services.websocket_manager import (
    manager,
    initialize_websocket_manager,
    close_websocket_manager,
)

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
        # Initialize WebSocket Manager
        await initialize_websocket_manager()
        
        # --- Initialize ChromaDB Client ---
        initialize_chroma_client()

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
        log_message("Server shutting down... ")
        await close_websocket_manager()
        await close_redis_pool()
        close_chroma_client()


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

# WebSocket Endpoint #
@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            # This loop keeps the connection alive.
            # It will break automatically when the client disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)


#   API Endpoint Definition   #
# Health Check Endpoint #
@app.get("/")
async def health_check():  
    """
    Health check endpoint to verify server status.
    Returns a simple JSON response indicating server is running.
    """
    return {"status": "ok", "statusCode": 200,"message": "Server is running"}


@app.post("/log-payload")
async def log_payload(request: Request):
    """
    Logs the raw request body and returns a confirmation.
    This is for debugging purposes.
    """
    try:
        payload = await request.json()
        log_message(f"Received payload: {payload}", level=1, prefix="--- PAYLOAD ---")
        return {"status": "payload logged", "statusCode": 200}
    except Exception as e:
        log_message(f"Error processing payload: {e}", level=1, prefix="!!! ERROR !!!", log_type="error")
        body = await request.body()
        log_message(f"Raw body: {body.decode()}", level=2, prefix="--- RAW BODY ---")
        return {"status": "error logging payload", "statusCode": 500, "detail": str(e)}


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


#  HubSpot Assignment Webhook Endpoint  #
@app.post("/hubspot/webhooks/assignment")
async def hubspot_assignment_webhook_endpoint(payload: HubSpotAssignmentPayload, background_tasks: BackgroundTasks):
    """
    Receives webhook events from HubSpot for conversation assignment changes.
    Processes assignment status and sends appropriate messages to conversations.
    """
    
    # Schedule background task to process the assignment
    background_tasks.add_task(
        process_assignment_webhook,
        payload=payload,
    )
    
    # Return 200 OK immediately for HubSpot webhook best practice
    return {"statusCode": 200, "status": "Assignment webhook received and processing initiated"}


#   Run the Server (for local development)   #
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
