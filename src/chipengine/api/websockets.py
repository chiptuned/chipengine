"""
WebSocket support for ChipEngine.

Handles real-time game updates, room subscriptions, and move notifications.
"""

from typing import Dict, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

from ..core.base_game import BaseGame

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and game room subscriptions.
    
    Features:
    - Connection tracking per client
    - Game room subscriptions
    - Broadcast game updates to subscribed clients
    - Handle disconnections gracefully
    """
    
    def __init__(self):
        # Map of connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Map of game_id -> Set[connection_id]
        self.game_subscriptions: Dict[str, Set[str]] = {}
        # Map of connection_id -> Set[game_id]
        self.client_subscriptions: Dict[str, Set[str]] = {}
        # Lock for thread-safe operations
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket
            self.client_subscriptions[client_id] = set()
            logger.info(f"Client {client_id} connected")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
    
    async def disconnect(self, client_id: str) -> None:
        """Handle client disconnection."""
        async with self.lock:
            # Remove from all game subscriptions
            if client_id in self.client_subscriptions:
                for game_id in self.client_subscriptions[client_id]:
                    if game_id in self.game_subscriptions:
                        self.game_subscriptions[game_id].discard(client_id)
                        if not self.game_subscriptions[game_id]:
                            del self.game_subscriptions[game_id]
                del self.client_subscriptions[client_id]
            
            # Remove WebSocket connection
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                logger.info(f"Client {client_id} disconnected")
    
    async def subscribe_to_game(self, client_id: str, game_id: str) -> bool:
        """Subscribe a client to game updates."""
        async with self.lock:
            if client_id not in self.active_connections:
                return False
            
            # Add to game subscriptions
            if game_id not in self.game_subscriptions:
                self.game_subscriptions[game_id] = set()
            self.game_subscriptions[game_id].add(client_id)
            
            # Add to client subscriptions
            self.client_subscriptions[client_id].add(game_id)
            
            logger.info(f"Client {client_id} subscribed to game {game_id}")
        
        # Send subscription confirmation
        await self.send_personal_message({
            "type": "subscription",
            "action": "subscribed",
            "game_id": game_id,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        return True
    
    async def unsubscribe_from_game(self, client_id: str, game_id: str) -> bool:
        """Unsubscribe a client from game updates."""
        async with self.lock:
            if client_id not in self.active_connections:
                return False
            
            # Remove from game subscriptions
            if game_id in self.game_subscriptions:
                self.game_subscriptions[game_id].discard(client_id)
                if not self.game_subscriptions[game_id]:
                    del self.game_subscriptions[game_id]
            
            # Remove from client subscriptions
            if client_id in self.client_subscriptions:
                self.client_subscriptions[client_id].discard(game_id)
            
            logger.info(f"Client {client_id} unsubscribed from game {game_id}")
        
        # Send unsubscription confirmation
        await self.send_personal_message({
            "type": "subscription",
            "action": "unsubscribed",
            "game_id": game_id,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        return True
    
    async def send_personal_message(self, message: dict, client_id: str) -> None:
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast_game_update(self, game_id: str, update: dict) -> None:
        """Broadcast an update to all clients subscribed to a game."""
        # Get list of subscribers (copy to avoid modification during iteration)
        async with self.lock:
            subscribers = list(self.game_subscriptions.get(game_id, []))
        
        if not subscribers:
            return
        
        # Add metadata to update
        update["game_id"] = game_id
        update["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all subscribers
        disconnected_clients = []
        for client_id in subscribers:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_json(update)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    async def broadcast_game_state(self, game_id: str, game_state: dict) -> None:
        """Broadcast the full game state to all subscribers."""
        await self.broadcast_game_update(game_id, {
            "type": "game_state",
            "state": game_state
        })
    
    async def broadcast_move(self, game_id: str, player: str, move: dict, result: dict) -> None:
        """Broadcast a move notification to all subscribers."""
        await self.broadcast_game_update(game_id, {
            "type": "move",
            "player": player,
            "move": move,
            "result": result
        })
    
    async def broadcast_game_over(self, game_id: str, winner: Optional[str], final_state: dict) -> None:
        """Broadcast game over notification to all subscribers."""
        await self.broadcast_game_update(game_id, {
            "type": "game_over",
            "winner": winner,
            "final_state": final_state
        })
    
    async def get_connection_stats(self) -> dict:
        """Get current connection statistics."""
        async with self.lock:
            return {
                "active_connections": len(self.active_connections),
                "active_games": len(self.game_subscriptions),
                "subscriptions": {
                    game_id: len(subscribers) 
                    for game_id, subscribers in self.game_subscriptions.items()
                }
            }


# Global connection manager instance
manager = ConnectionManager()


async def handle_client_message(websocket: WebSocket, client_id: str, message: dict) -> None:
    """
    Handle incoming WebSocket messages from clients.
    
    Supported message types:
    - subscribe: Subscribe to game updates
    - unsubscribe: Unsubscribe from game updates
    - ping: Keep-alive ping
    """
    msg_type = message.get("type")
    
    if msg_type == "subscribe":
        game_id = message.get("game_id")
        if game_id:
            success = await manager.subscribe_to_game(client_id, game_id)
            if not success:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to subscribe to game",
                    "game_id": game_id
                })
    
    elif msg_type == "unsubscribe":
        game_id = message.get("game_id")
        if game_id:
            success = await manager.unsubscribe_from_game(client_id, game_id)
            if not success:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to unsubscribe from game",
                    "game_id": game_id
                })
    
    elif msg_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {msg_type}"
        })