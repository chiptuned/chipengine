"""Authentication middleware and utilities for bot API."""

import secrets
import time
from typing import Dict, Optional
from datetime import datetime
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, Bot

security = HTTPBearer()


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def check_rate_limit(self, bot_id: str) -> bool:
        """Check if bot is within rate limit."""
        now = time.time()
        
        if bot_id not in self.requests:
            self.requests[bot_id] = []
        
        # Remove old requests outside the window
        self.requests[bot_id] = [
            req_time for req_time in self.requests[bot_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if within limit
        if len(self.requests[bot_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[bot_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def generate_api_key() -> str:
    """Generate a secure API key for bot authentication."""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Add a prefix to identify ChipEngine keys
    return f"chp_{token}"


def get_current_bot(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> Bot:
    """
    Validate bot authentication and return current bot.
    
    This dependency can be used in any endpoint that requires bot authentication.
    """
    api_key = credentials.credentials
    
    # Query bot by API key
    bot = db.query(Bot).filter(Bot.api_key == api_key).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not bot.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bot account is deactivated"
        )
    
    # Check rate limit
    if not rate_limiter.check_rate_limit(bot.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Update last seen timestamp
    bot.metadata = bot.metadata or {}
    bot.metadata["last_request_time"] = datetime.utcnow().isoformat()
    db.commit()
    
    return bot


def require_bot_ownership(game_id: str, bot: Bot, db: Session) -> None:
    """
    Verify that a bot owns or is participating in a game.
    
    Raises HTTPException if bot doesn't have access to the game.
    """
    from .database import Game, Player
    
    # Check if bot is a player in this game
    player = db.query(Player).join(Game).filter(
        Game.id == game_id,
        Player.bot_id == bot.id
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this game"
        )