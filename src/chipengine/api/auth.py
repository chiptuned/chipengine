"""Authentication middleware and utilities for bot API."""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, Bot
import hashlib

security = HTTPBearer()


def get_current_bot(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> Bot:
    """Authenticate bot using API key."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    api_key = credentials.credentials
    api_key_hash = Bot.hash_api_key(api_key)
    
    bot = db.query(Bot).filter(
        Bot.api_key_hash == api_key_hash,
        Bot.is_active == True
    ).first()
    
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return bot


def get_optional_bot(
    credentials: HTTPAuthorizationCredentials = Depends(lambda: None),
    db: Session = Depends(get_db)
) -> Bot | None:
    """Get bot if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return get_current_bot(credentials, db)
    except HTTPException:
        return None