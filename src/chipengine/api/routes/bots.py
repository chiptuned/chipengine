"""Bot registration and management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db, Bot, create_tables
from ..models import (
    BotRegistrationRequest,
    BotRegistrationResponse, 
    BotInfoResponse,
    ErrorResponse
)
from ..auth import get_current_bot
from ..rate_limiting import check_bot_rate_limit

router = APIRouter(prefix="/bots", tags=["bots"])

# Ensure tables exist
create_tables()


@router.post(
    "/register",
    response_model=BotRegistrationResponse,
    responses={
        409: {"model": ErrorResponse, "description": "Bot name already exists"},
        400: {"model": ErrorResponse, "description": "Invalid request"}
    }
)
async def register_bot(
    request: BotRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new bot and get API key.
    
    **This endpoint is public** - no authentication required for registration.
    
    Returns:
    - bot_id: Unique bot identifier
    - name: Bot name
    - api_key: Secret API key for authentication (store securely!)
    - message: Success message
    
    **Important**: Store the API key securely - it cannot be retrieved later!
    """
    try:
        # Generate secure API key
        api_key = Bot.generate_api_key()
        api_key_hash = Bot.hash_api_key(api_key)
        
        # Create bot record
        bot = Bot(
            name=request.name,
            api_key=api_key,  # Store plaintext temporarily for response
            api_key_hash=api_key_hash
        )
        
        db.add(bot)
        db.commit()
        db.refresh(bot)
        
        # Return API key (only time it's shown!)
        return BotRegistrationResponse(
            bot_id=bot.id,
            name=bot.name,
            api_key=api_key,
            message=f"Bot '{request.name}' registered successfully! Store your API key securely."
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Bot name '{request.name}' already exists"
        )


@router.get(
    "/me",
    response_model=BotInfoResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def get_my_info(
    request: Request,
    current_bot: Bot = Depends(get_current_bot)
):
    """
    Get information about the authenticated bot.
    
    Requires: Bearer token with valid API key
    """
    check_bot_rate_limit(request, current_bot.id)
    
    return BotInfoResponse(
        bot_id=current_bot.id,
        name=current_bot.name,
        created_at=current_bot.created_at,
        is_active=current_bot.is_active
    )


@router.get(
    "/",
    response_model=List[BotInfoResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def list_bots(
    request: Request,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """
    List all registered bots (public information).
    
    Requires: Bearer token with valid API key
    """
    check_bot_rate_limit(request, current_bot.id)
    
    bots = db.query(Bot).filter(Bot.is_active == True).all()
    
    return [
        BotInfoResponse(
            bot_id=bot.id,
            name=bot.name,
            created_at=bot.created_at,
            is_active=bot.is_active
        )
        for bot in bots
    ]


@router.delete(
    "/me",
    responses={
        200: {"description": "Bot deactivated successfully"},
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def deactivate_bot(
    request: Request,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """
    Deactivate the authenticated bot.
    
    This will disable the bot and invalidate its API key.
    """
    check_bot_rate_limit(request, current_bot.id)
    
    current_bot.is_active = False
    db.commit()
    
    return {"message": f"Bot '{current_bot.name}' has been deactivated"}