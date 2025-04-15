# main_server.py
# System imports
import json
import uvicorn
from typing import Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Centralized Agent Service
from agents.agents_services import agent_service

# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    stop_reason: Optional[str] = None
    error: Optional[str] = None
    conversation_id: Optional[str] = None
    
# --- FastAPI App Setup ---
app = FastAPI(
    title="AutoGen Agent API",
    description="API endpoint to interact with the multi-agent AutoGen system.",
)

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://172.20.20.204:5173/",
    "http://172.27.160.1:5173/",
    "http://172.17.0.1:5173/",
    "https://hubsbot.loca.lt", # Subdomain exposed with localtunnel
    "http://hubsbot.loca.lt"
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
    Receives a user message, processes it via the centralized AgentService,
    and returns the final reply or error.
    """
    print(f"\n<-- Received request: {request.message}")
    print("\n>>>>>>>>>>>>>> Chat Start <<<<<<<<<<<<<<")
    task_result, error_message = await agent_service.run_chat_session(request.message)
    print("\n>>>>>>>>>>>>>> Chat End <<<<<<<<<<<<<<")

    # Handle errors reported by the service or the invocation
    if error_message:
        # Consider logging the error_message server-side
        print(f"!!! Error reported: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

    # Handle cases where the task didn't complete successfully but didn't raise an error
    if not task_result:
        err_detail = "Task finished without a result, but no specific error was reported."
        print(f"!!! {err_detail}")
        raise HTTPException(status_code=500, detail=err_detail)

    # Process successful result
    final_reply = "No final message found in result." # Default fallback
    stop_reason = str(task_result.stop_reason) if task_result.stop_reason else "Unknown"

    ####### --- Process Task Result --- #######
    print(f"\n\n\n\n\n <<<----------->>> Task Result Analysis <<<----------->>>")
    if error_message:
        print(f"        - Task failed with error: {error_message}")
    elif task_result:
        print(f"        - Stop Reason: {task_result.stop_reason}")
        print(f"        - Number of Messages: {len(task_result.messages)}")

        # Check the final message
        if task_result.messages:
            final_reply = task_result.messages[-1]
            # Extract content safely
            if hasattr(final_reply, 'content'):
                 final_content = final_reply.content if isinstance(final_reply.content, str) else json.dumps(final_reply.content)
            else:
                 final_content = f"[{type(final_reply).__name__} with no 'content']"

            if task_result.stop_reason is None or "completed" in str(task_result.stop_reason).lower() or "finished" in str(task_result.stop_reason).lower():
                    print(">>> Task completed successfully. <<<")
            
            print(f"        - Final Message: {final_content}")
        else:
            print(">>> No messages found in TaskResult. <<<")
    else:
         print(">>> TaskResult was not obtained (task might have failed before completion or service error) <<<")
    ####### --- End of Task Result Analysis --- #######

    # Use the extracted string content for the response
    return ChatResponse(reply=final_content, stop_reason=stop_reason)

# --- Run the Server (for local development) ---
if __name__ == "__main__":
    # Use reload=True for development so the server restarts on code changes
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)