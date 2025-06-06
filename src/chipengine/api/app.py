"""
FastAPI application for ChipEngine.

Main application entry point with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from .routes.games import router as games_router
from .models import HealthResponse
from .. import __version__

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


if __name__ == "__main__":
    uvicorn.run(
        "chipengine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )