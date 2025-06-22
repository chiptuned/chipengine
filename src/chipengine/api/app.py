"""
FastAPI application for ChipEngine.

Main application entry point with all routes and middleware.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import uuid

from .routes.games import router as games_router
from .routes.stress_tests import router as stress_tests_router
from .routes.bots import router as bots_router
from .routes.stats import router as stats_router
from .routes.tournaments import router as tournaments_router
from .models import HealthResponse
from .. import __version__
from ..database import init_db
from .websockets import manager, handle_client_message

# Create FastAPI app
app = FastAPI(
    title="ChipEngine API",
    description="Fast, lean chip engine for bot competitions",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games_router)
app.include_router(stress_tests_router)
app.include_router(bots_router)
app.include_router(stats_router)
app.include_router(tournaments_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"ChipEngine API v{__version__} started")
    print("Database initialized")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow().isoformat()
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time game updates.
    
    Clients can:
    - Connect to receive real-time updates
    - Subscribe to specific games
    - Receive move notifications
    - Receive game state changes
    """
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            await handle_client_message(websocket, client_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        await manager.disconnect(client_id)


@app.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics."""
    return await manager.get_connection_stats()


if __name__ == "__main__":
    uvicorn.run(
        "chipengine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )