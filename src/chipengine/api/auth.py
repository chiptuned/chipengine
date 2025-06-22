"""
Authentication module for ChipEngine Bot API.

Provides API key authentication and rate limiting for bot endpoints.
"""

import secrets
import time
from typing import Dict, Optional, Set
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel


class BotInfo(BaseModel):
    """Information about a registered bot."""
    bot_id: str
    name: str
    api_key: str
    created_at: datetime
    rate_limit: int = 100  # requests per minute
    games_created: int = 0
    last_request_time: Optional[datetime] = None


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
    
    def get_requests_count(self, bot_id: str) -> int:
        """Get current requests count for a bot."""
        now = time.time()
        
        if bot_id not in self.requests:
            return 0
        
        # Count requests within window
        return len([
            req_time for req_time in self.requests[bot_id]
            if now - req_time < self.window_seconds
        ])


class BotAuthManager:
    """Manages bot authentication and authorization."""
    
    def __init__(self):
        self.bots: Dict[str, BotInfo] = {}
        self.api_key_to_bot: Dict[str, str] = {}
        self.rate_limiter = RateLimiter()
    
    def register_bot(self, name: str) -> BotInfo:
        """Register a new bot and generate API key."""
        from ..database.session import DatabaseSession
        from ..database.models import Bot as BotModel
        
        bot_id = f"bot_{secrets.token_urlsafe(8)}"
        api_key = f"chp_{secrets.token_urlsafe(32)}"
        
        bot_info = BotInfo(
            bot_id=bot_id,
            name=name,
            api_key=api_key,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        try:
            with DatabaseSession() as db:
                bot_model = BotModel(
                    id=bot_id,
                    name=name,
                    api_key=api_key,
                    created_at=bot_info.created_at
                )
                db.add(bot_model)
                db.commit()
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to save bot to database: {e}")
        
        self.bots[bot_id] = bot_info
        self.api_key_to_bot[api_key] = bot_id
        
        return bot_info
    
    def get_bot_by_api_key(self, api_key: str) -> Optional[BotInfo]:
        """Get bot info by API key."""
        bot_id = self.api_key_to_bot.get(api_key)
        if bot_id:
            return self.bots.get(bot_id)
        return None
    
    def get_bot_by_id(self, bot_id: str) -> Optional[BotInfo]:
        """Get bot info by ID."""
        return self.bots.get(bot_id)
    
    def check_rate_limit(self, bot_id: str) -> bool:
        """Check if bot is within rate limit."""
        bot = self.bots.get(bot_id)
        if not bot:
            return False
        
        return self.rate_limiter.check_rate_limit(bot_id)
    
    def update_last_request(self, bot_id: str):
        """Update bot's last request time."""
        bot = self.bots.get(bot_id)
        if bot:
            bot.last_request_time = datetime.utcnow()
    
    def increment_games_created(self, bot_id: str):
        """Increment bot's games created counter."""
        bot = self.bots.get(bot_id)
        if bot:
            bot.games_created += 1


# Global auth manager instance
bot_auth_manager = BotAuthManager()

# API Key header security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> BotInfo:
    """Verify API key and return bot info."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    bot = bot_auth_manager.get_bot_by_api_key(api_key)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check rate limit
    if not bot_auth_manager.check_rate_limit(bot.bot_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Max 100 requests per minute."
        )
    
    # Update last request time
    bot_auth_manager.update_last_request(bot.bot_id)
    
    return bot