"""
Bot API routes for ChipEngine.

Provides REST endpoints for bot registration and game management.
"""

from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

from ..models import (
    RegisterBotRequest, RegisterBotResponse,
    BotInfoResponse, BotCreateGameRequest, BotCreateGameResponse,
    BotMakeMoveRequest, MakeMoveResponse, GameStateResponse,
    BotGameListResponse, BotStatistics
)
from ..auth import get_current_bot, generate_api_key
from ..database import get_db, Bot, Game, Player, Move
from ..game_manager import game_manager
from ...core.history import GameHistoryRecorder

router = APIRouter(prefix="/api/bots", tags=["bots"])


@router.post("/register", response_model=RegisterBotResponse)
async def register_bot(
    request: RegisterBotRequest,
    db: Session = Depends(get_db)
):
    """Register a new bot and receive an API key."""
    # Check if bot name already exists
    existing_bot = db.query(Bot).filter(Bot.name == request.name).first()
    if existing_bot:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bot name already exists"
        )
    
    # Create new bot
    bot_id = str(uuid.uuid4())
    api_key = generate_api_key()
    
    bot = Bot(
        id=bot_id,
        name=request.name,
        api_key=api_key,
        is_active=True,
        metadata={}
    )
    
    try:
        db.add(bot)
        db.commit()
        db.refresh(bot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bot registration failed"
        )
    
    return RegisterBotResponse(
        bot_id=bot.id,
        name=bot.name,
        api_key=bot.api_key,
        created_at=bot.created_at.isoformat()
    )


@router.get("/{bot_id}", response_model=BotInfoResponse)
async def get_bot_info(
    bot_id: str,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """Get information about a bot (can only access your own info)."""
    if current_bot.id != bot_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own bot information"
        )
    
    # Count games created by this bot
    games_created = db.query(Game).join(Player).filter(
        Player.bot_id == bot_id
    ).count()
    
    last_request_time = None
    if current_bot.metadata and "last_request_time" in current_bot.metadata:
        last_request_time = current_bot.metadata["last_request_time"]
    
    return BotInfoResponse(
        bot_id=current_bot.id,
        name=current_bot.name,
        created_at=current_bot.created_at.isoformat(),
        games_created=games_created,
        last_request_time=last_request_time,
        rate_limit=100  # requests per minute
    )


@router.post("/games", response_model=BotCreateGameResponse)
async def create_game(
    request: BotCreateGameRequest,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """Create a new game as a bot."""
    # Generate bot IDs as players
    players = [current_bot.id]
    
    if request.opponent_bot_id:
        # Verify opponent bot exists
        opponent = db.query(Bot).filter(Bot.id == request.opponent_bot_id).first()
        if not opponent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opponent bot not found"
            )
        players.append(request.opponent_bot_id)
    else:
        # Add a random bot opponent
        players.append("bot_random")
    
    # Create game through game manager
    try:
        game_state = game_manager.create_game(
            game_type=request.game_type,
            players=players,
            config=request.config
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return BotCreateGameResponse(
        game_id=game_state.game_id,
        game_type=game_state.game_type,
        players=game_state.players,
        status=game_state.status,
        your_player_id=current_bot.id
    )


@router.get("/games/{game_id}", response_model=GameStateResponse)
async def get_game_state(
    game_id: str,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """Get current state of a game."""
    # Verify bot has access to this game
    from ..auth import require_bot_ownership
    require_bot_ownership(game_id, current_bot, db)
    
    # Get game state
    game_state = game_manager.get_game_state(game_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    return game_state


@router.post("/games/{game_id}/move", response_model=MakeMoveResponse)
async def make_move(
    game_id: str,
    request: BotMakeMoveRequest,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """Make a move in a game."""
    # Verify bot has access to this game
    from ..auth import require_bot_ownership
    require_bot_ownership(game_id, current_bot, db)
    
    # Make the move
    try:
        move = {"action": request.action, **request.data}
        result = game_manager.make_move(
            game_id=game_id,
            player_id=current_bot.id,
            move=move
        )
        
        return MakeMoveResponse(
            success=result["success"],
            message=result.get("message", ""),
            game_state=result["game_state"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/games", response_model=BotGameListResponse)
async def list_games(
    status: Optional[str] = None,
    limit: int = 20,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """List games for the authenticated bot."""
    # Query games where bot is a player
    query = db.query(Game).join(Player).filter(Player.bot_id == current_bot.id)
    
    if status:
        query = query.filter(Game.status == status)
    
    games = query.order_by(Game.created_at.desc()).limit(limit).all()
    
    # Convert to response format
    game_list = []
    for game in games:
        game_list.append({
            "game_id": game.id,
            "game_type": game.game_type,
            "status": game.status,
            "created_at": game.created_at.isoformat(),
            "completed_at": game.completed_at.isoformat() if game.completed_at else None,
            "winner_id": game.winner_id
        })
    
    # Count games by status
    total_games = db.query(Game).join(Player).filter(Player.bot_id == current_bot.id).count()
    active_games = db.query(Game).join(Player).filter(
        Player.bot_id == current_bot.id,
        Game.status == "active"
    ).count()
    completed_games = total_games - active_games
    
    return BotGameListResponse(
        games=game_list,
        total_games=total_games,
        active_games=active_games,
        completed_games=completed_games
    )


@router.get("/stats", response_model=BotStatistics)
async def get_bot_stats(
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for the authenticated bot."""
    # Get all games where bot participated
    games = db.query(Game).join(Player).filter(Player.bot_id == current_bot.id).all()
    
    total_games = len(games)
    wins = sum(1 for g in games if g.winner_id == current_bot.id)
    losses = sum(1 for g in games if g.status == "completed" and g.winner_id != current_bot.id)
    draws = sum(1 for g in games if g.status == "completed" and g.winner_id is None)
    
    # Calculate win rate
    completed_games = wins + losses + draws
    win_rate = (wins / completed_games * 100) if completed_games > 0 else 0.0
    
    # Count by game type
    games_by_type = {}
    for game in games:
        games_by_type[game.game_type] = games_by_type.get(game.game_type, 0) + 1
    
    # Get recent games
    recent_games = []
    for game in sorted(games, key=lambda g: g.created_at, reverse=True)[:5]:
        recent_games.append({
            "game_id": game.id,
            "game_type": game.game_type,
            "status": game.status,
            "result": "win" if game.winner_id == current_bot.id else "loss" if game.winner_id else "draw",
            "completed_at": game.completed_at.isoformat() if game.completed_at else None
        })
    
    return BotStatistics(
        bot_id=current_bot.id,
        total_games=total_games,
        wins=wins,
        losses=losses,
        draws=draws,
        win_rate=win_rate,
        games_by_type=games_by_type,
        recent_games=recent_games
    )