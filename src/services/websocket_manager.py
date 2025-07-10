"""WebSocket Connection Manager"""

# src/services/websocket_manager.py
import asyncio
from typing import Dict, List, Optional
from fastapi import WebSocket

from src.services.logger_config import log_message

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
        log_message(f"WebSocket connected for conv_id: {conversation_id}", level=3)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            log_message(f"WebSocket disconnected for conv_id: {conversation_id}", level=3)

    async def send_message(self, message: str, conversation_id: str):
        if conversation_id in self.active_connections:
            log_message(f"Sending WebSocket message '{message}' to conv_id: {conversation_id}", level=3)
            tasks = [connection.send_text(message) for connection in self.active_connections[conversation_id]]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def disconnect_all(self):
        """Gracefully disconnects all active WebSocket connections."""
        log_message("Disconnecting all active WebSocket connections.", level=2, prefix="---")
        tasks = []
        for conv_id in list(self.active_connections.keys()):
            connections = self.active_connections.pop(conv_id, [])
            for ws in connections:
                tasks.append(ws.close())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        log_message("Finished disconnecting all WebSockets.", level=2, prefix="---")

# --- Global Manager Instance ---
manager: ConnectionManager | None = ConnectionManager()

async def initialize_websocket_manager():
    """Initializes the WebSocket Connection Manager."""
    global manager
    if manager is None:
        log_message("Initializing WebSocket Connection Manager...", level=3)
        manager = ConnectionManager()

async def close_websocket_manager():
    """Closes all connections and shuts down the WebSocket Manager."""
    global manager
    if manager:
        await manager.disconnect_all()
        manager = None