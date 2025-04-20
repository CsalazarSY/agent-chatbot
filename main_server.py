# main_server.py
# System imports
import json
import uvicorn
from typing import Optional
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Centralized Agent Service
from agents.agents_services import agent_service
# Import config to access the refresh function
import config

# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    stop_reason: Optional[str] = None
    error: Optional[str] = None


# --- FastAPI App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("--- Running Application Startup --- ")
    success = await config.refresh_sy_token()
    if success:
        print("Initial SY API token refresh successful.")
    else:
        print("Initial SY API token refresh failed. Will attempt on first API call.")
    yield

app = FastAPI(
    title="AutoGen Agent API",
    description="API endpoint to interact with the multi-agent AutoGen system.",
    lifespan=lifespan # Add the lifespan context manager
)

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://172.20.20.204:5173/", 
    "http://172.27.160.1:5173/", 
    "http://172.17.0.1:5173/",   
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

# --- API Endpoint Definition ---
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
        show_console=False, # Ensure console output is off for API
        conversation_id=request.conversation_id
    )

    # Handle errors reported by the service or the invocation
    if error_message:
        # Consider logging the error_message server-side
        print(f"!!! Error reported: {error_message}")
        # If ID was missing, final_conversation_id will be None from the service
        status_code = 400 if "conversation_id is required" in error_message else 500
        raise HTTPException(status_code=status_code, detail={"message": error_message, "conversation_id": final_conversation_id})

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
    print(f"    << Task Result >>")
    if error_message:
        print(f"        - Task failed with error: {error_message}")
    elif task_result:
        print(f"        - Stop Reason: {stop_reason}") # Use processed stop_reason
        print(f"        - Number of Messages: {len(task_result.messages)}\n")

        # Extract the last message's content for the reply
        if task_result.messages:
            last_message = task_result.messages[-1] # Get the last message object
            # Extract content safely, handling different message types
            if hasattr(last_message, 'content'):
                 final_reply_content = last_message.content if isinstance(last_message.content, str) else json.dumps(last_message.content)
                 # Clean up internal tags if they are not meant for the user
                 if isinstance(final_reply_content, str):
                     # Remove TASK COMPLETE/FAILED prefixes
                     if final_reply_content.startswith("TASK COMPLETE:"): final_reply_content = final_reply_content[len("TASK COMPLETE:"):].strip()
                     if final_reply_content.startswith("TASK FAILED:"): final_reply_content = final_reply_content[len("TASK FAILED:"):].strip()

                     # Remove <UserProxyAgent> tag and potential leading/trailing whitespace
                     final_reply_content = final_reply_content.replace("<UserProxyAgent> :", "").strip()
                     final_reply_content = final_reply_content.replace("<UserProxyAgent>:", "").strip()
                     final_reply_content = final_reply_content.replace("<UserProxyAgent>", "").strip()

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

# --- Run the Server (for local development) ---
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)