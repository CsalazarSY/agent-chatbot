""" Main server for the AutoGen Agent API """
# main_server.py
import asyncio # Import asyncio for background tasks
import traceback # For detailed error logging

# System imports
from contextlib import asynccontextmanager
from typing import Optional
import json
import uvicorn

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# AutoGen imports
from autogen_agentchat.base import TaskResult
# Types
from models.api_types import ChatRequest, ChatResponse
from models.hubspot_types import WebhookPayload, HubSpotSubscriptionType

# Centralized Agent Service
from agents.agents_services import agent_service

# HubSpot Tools for direct use in webhook handler
from agents.hubspot.tools.conversation_tools import get_message_details, send_message_to_thread
# Import config to access the refresh function
import config

# --- FastAPI App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan to control the FastAPI app """
    # Code to run on startup
    success = await config.refresh_sy_token()
    if not success:
        print("!!! Initial SY API token refresh failed. Will attempt on first API call.")
    yield

app = FastAPI(
    title="AutoGen Agent API",
    description="API endpoint to interact with the multi-agent AutoGen system.",
    lifespan=lifespan
)

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://172.20.20.204:5173", # Removed trailing slash
    "http://172.27.160.1:5173", # Removed trailing slash
    "http://172.17.0.1:5173",   # Removed trailing slash
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
                    # Remove TASK COMPLETE/FAILED prefixes
                    if final_reply_content.startswith("TASK COMPLETE:"): final_reply_content = final_reply_content[len("TASK COMPLETE:"):].strip()
                    if final_reply_content.startswith("TASK FAILED:"): final_reply_content = final_reply_content[len("TASK FAILED:"):].strip()

                    # Remove <UserProxyAgent> tag and potential leading/trailing whitespace
                    final_reply_content = final_reply_content.replace("<UserProxyAgent>", "").strip()
                    # Remove potential leading/trailing colons if UserProxyAgent tag had them
                    if final_reply_content.startswith(":"): final_reply_content = final_reply_content[1:].strip()

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

async def process_agent_response_and_reply(conversation_id: str, task_result: Optional[TaskResult], error_message: Optional[str]):
    """
    Helper coroutine to process the agent's result and send the final reply to HubSpot.
    Runs in the background after the webhook returns 200 OK.
    """
    final_reply_to_send = "Sorry, I encountered an issue and couldn't process your message." # Default error reply

    if error_message:
        print(f"!! Agent Error for ConvID {conversation_id}: {error_message}")
        # Use default error reply
    elif task_result and task_result.messages:
        last_agent_message = task_result.messages[-1]
        if hasattr(last_agent_message, 'content'):
            raw_reply = last_agent_message.content
            if isinstance(raw_reply, str):
                # Clean up Planner's final output tags
                cleaned_reply = raw_reply
                if cleaned_reply.startswith("TASK COMPLETE:"): cleaned_reply = cleaned_reply[len("TASK COMPLETE:"):].strip()
                if cleaned_reply.startswith("TASK FAILED:"): cleaned_reply = cleaned_reply[len("TASK FAILED:"):].strip()
                cleaned_reply = cleaned_reply.replace("<UserProxyAgent>", "").strip()
                # Remove potential leading/trailing colons if UserProxyAgent tag had them
                if cleaned_reply.startswith(":"): cleaned_reply = cleaned_reply[1:].strip()

                if cleaned_reply: # Ensure we have something to send
                    final_reply_to_send = cleaned_reply
                else:
                    print(f"!! Agent for ConvID {conversation_id} provided an empty reply after cleaning.")
                    # Use default error reply or a specific "empty reply" message
                    final_reply_to_send = "I received your message but somethig went wrong when generating the response."
            else:
                print(f"!! Agent for ConvID {conversation_id} final message content is not a string: {type(raw_reply)}")
                # Use default error reply
        else:
            print(f"!! Agent for ConvID {conversation_id} final message has no 'content' attribute.")
            # Use default error reply
    else:
        print(f"!! No task result or messages for ConvID {conversation_id}.")
        # Use default error reply

    # Send the final reply (or error message) back to the HubSpot thread
    print(f"--> Sending reply to HubSpot Thread {conversation_id}: '{final_reply_to_send}'")
    try:
        # Pass only required args + text
        send_result = await send_message_to_thread(
            thread_id=conversation_id,
            message_text=final_reply_to_send
        )
        if isinstance(send_result, str) and send_result.startswith("HUBSPOT_TOOL_FAILED"):
            print(f"!!! FAILED to send reply to HubSpot Thread {conversation_id}: {send_result}")

    except Exception as send_exc:
        print(f"!!! EXCEPTION sending reply to HubSpot Thread {conversation_id}: {send_exc}")
        traceback.print_exc()


@app.post("/hubspot/webhooks")
async def hubspot_webhook_endpoint(payload: WebhookPayload):
    """
    Receives webhook notifications from HubSpot.
    Validates signature, processes relevant events (conversation.newMessage type: MESSAGE),
    triggers agent processing in the background, and returns 200 OK immediately.
    """
    # --- TODO: Implement Request Signature Verification --- #
    # 1. Get X-HubSpot-Signature header
    # 2. Get raw request body
    # 3. Concatenate client_secret + raw_body
    # 4. Calculate SHA-256 hash
    # 5. Compare hash with signature header
    # If verification fails, raise HTTPException(status_code=403, detail="Invalid signature")
    # -------------------------------------------------------- #

    print(f"\n\n--- Received HubSpot Webhook Payload ({len(payload)} event(s)) ---")

    for event in payload:
        print(f"    - Processing Event Type: {event.subscriptionType}, Object ID: {event.objectId}")

        # Filter for new messages of type MESSAGE
        if event.subscriptionType == HubSpotSubscriptionType.CONVERSATION_NEW_MESSAGE and event.messageType == "MESSAGE":
            thread_id = str(event.objectId) # Ensure string for consistency
            message_id = event.messageId

            if not message_id:
                print(f"    - Skipping newMessage event for thread {thread_id}: Missing messageId.")
                continue

            # Fetch message content (needs to happen before triggering agent)
            message_content = None
            try:
                print(f"    - Fetching message details for {message_id} in thread {thread_id}...")
                msg_details = await get_message_details(thread_id=thread_id, message_id=message_id)

                if isinstance(msg_details, dict) and 'text' in msg_details:
                    message_content = msg_details['text']
                    print(f"    -> Fetched message content: '{message_content[:50]}...'") # Log snippet
                elif isinstance(msg_details, str) and msg_details.startswith("HUBSPOT_TOOL_FAILED"):
                     print(f"    !! Failed to fetch message details: {msg_details}")
                else:
                    print(f"    !! Unexpected response from get_message_details: {type(msg_details)}")

            except Exception as fetch_exc:
                print(f"    !! EXCEPTION fetching message details for {message_id}: {fetch_exc}")
                traceback.print_exc()

            # If we successfully got content, trigger the agent processing in the background
            if message_content:
                print(f"    -> Triggering agent processing for thread {thread_id} in background...")
                # Create a background task to run the agent and send the reply
                async def run_agent_and_reply():
                    task_result, error_message, _ = await agent_service.run_chat_session(
                        user_message=message_content,
                        show_console=True,
                        conversation_id=thread_id
                    )
                    await process_agent_response_and_reply(thread_id, task_result, error_message)

                asyncio.create_task(run_agent_and_reply())
            else:
                 print(f"    -> Skipping agent trigger for thread {thread_id} due to missing message content.")

        else:
            print(f"    - Skipping event: Type '{event.subscriptionType}' / Message Type '{event.messageType}' not processed.")

    # Return 200 OK quickly to HubSpot regardless of background processing
    return {"status": "received"}


# --- --- Run the Server (for local development) --- --- #
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
