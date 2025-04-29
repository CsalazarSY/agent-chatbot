''' Custom API types for the agent chatbot (/chat)'''
# types/api_types.py
from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """ Request model for the chat endpoint """
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """ Response model for the chat endpoint """
    reply: str
    conversation_id: str
    stop_reason: Optional[str] = None
    error: Optional[str] = None 
    