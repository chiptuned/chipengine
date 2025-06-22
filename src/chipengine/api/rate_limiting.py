"""Rate limiting for bot API endpoints."""

from fastapi import HTTPException, Request
from collections import defaultdict, deque
import time
from typing import Dict, Deque

class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier."""
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] <= now - self.window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) >= self.max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        return True


# Global rate limiters
bot_rate_limiter = InMemoryRateLimiter(max_requests=1000, window_seconds=60)  # 1000 req/min
game_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)   # 10 games/min


def check_bot_rate_limit(request: Request, bot_id: int):
    """Check general bot API rate limit."""
    identifier = f"bot_{bot_id}"
    if not bot_rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 1000 requests per minute."
        )


def check_game_creation_rate_limit(request: Request, bot_id: int):
    """Check game creation rate limit."""
    identifier = f"bot_game_{bot_id}"
    if not game_rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=429,
            detail="Game creation rate limit exceeded. Maximum 10 games per minute."
        )