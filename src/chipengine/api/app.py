"""
FastAPI application for ChipEngine.

Main application entry point with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from .routes.games import router as games_router
from .routes.stress_tests import router as stress_tests_router
from .routes.bots import router as bots_router
from .routes.stats import router as stats_router
from .models import HealthResponse
from .. import __version__
from ..database import init_db

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


if __name__ == "__main__":
    uvicorn.run(
        "chipengine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )