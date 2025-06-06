"""
FastAPI application for ChipEngine.

Main application entry point with all routes and middleware.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from .routes.games import router as games_router
from .routes.bots import router as bots_router
from .routes.bot_games import router as bot_games_router
from .models import HealthResponse
from .database import get_db, Bot, Game
from .. import __version__
from sqlalchemy.orm import Session

# Create FastAPI app
app = FastAPI(
    title="ChipEngine Bot API",
    description="""
    Fast, lean chip engine for bot competitions
    
    ## Authentication
    Most endpoints require API key authentication using Bearer tokens.
    
    ## Rate Limits
    - General API: 1000 requests/minute per bot
    - Game creation: 10 games/minute per bot
    
    ## Supported Games
    - **RPS**: Rock Paper Scissors
    """,
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
app.include_router(games_router)  # Human-playable games
app.include_router(bots_router)   # Bot registration
app.include_router(bot_games_router)  # Bot game API


@app.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with statistics."""
    bots_count = db.query(Bot).filter(Bot.is_active == True).count()
    active_games = db.query(Game).filter(Game.status == "active").count()
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow().isoformat(),
        bots_count=bots_count,
        active_games=active_games
    )


@app.get("/health", response_model=HealthResponse)
async def health(db: Session = Depends(get_db)):
    """Health check endpoint with statistics."""
    bots_count = db.query(Bot).filter(Bot.is_active == True).count()
    active_games = db.query(Game).filter(Game.status == "active").count()
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow().isoformat(),
        bots_count=bots_count,
        active_games=active_games
    )


if __name__ == "__main__":
    uvicorn.run(
        "chipengine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )