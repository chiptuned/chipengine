"""Bot game management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
from datetime import datetime

from ..database import get_db, Bot, Game, Move
from ..models import (
    CreateGameRequest,
    CreateGameResponse,
    GameStateResponse,
    MakeMoveRequest,
    MakeMoveResponse,
    GameListResponse,
    GameResultResponse,
    ErrorResponse
)
from ..auth import get_current_bot
from ..rate_limiting import check_bot_rate_limit, check_game_creation_rate_limit
from ...games.rps import RockPaperScissorsGame
from ...core.base_game import Move as GameMove

router = APIRouter(prefix="/games", tags=["bot-games"])


def create_game_instance(game_type: str, players: List[str], config: dict):
    """Create appropriate game instance based on type."""
    if game_type.lower() == "rps":
        return RockPaperScissorsGame("bot_game", players)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported game type: {game_type}. Supported: ['rps']"
        )


def game_state_to_response(game: Game, game_instance) -> GameStateResponse:
    """Convert game instance to API response."""
    players = json.loads(game.players)
    
    # Get valid moves for current game state
    try:
        if game_instance.state.game_over:
            valid_moves = []
            current_player = None
        else:
            valid_moves = ["rock", "paper", "scissors"]  # RPS specific
            current_player = game_instance.state.current_player
    except:
        valid_moves = []
        current_player = None
    
    return GameStateResponse(
        game_id=game.id,
        game_type=game.game_type,
        players=players,
        status=game.status,
        current_player=current_player,
        game_over=game.status == "completed",
        winner=game.winner,
        valid_moves=valid_moves,
        moves_count=len(game.moves),
        created_at=game.created_at,
        metadata={}
    )


@router.post(
    "/",
    response_model=CreateGameResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid game type or players"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def create_game(
    request: Request,
    game_request: CreateGameRequest,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """
    Create a new game.
    
    Supported game types: ["rps"]
    
    Rate limit: 10 games per minute per bot
    """
    check_bot_rate_limit(request, current_bot.id)
    check_game_creation_rate_limit(request, current_bot.id)
    
    # Validate game type
    if game_request.game_type.lower() not in ["rps"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported game type: {game_request.game_type}. Supported: ['rps']"
        )
    
    # Generate unique game ID
    game_id = str(uuid.uuid4())
    
    # Create game instance to validate
    try:
        game_instance = create_game_instance(
            game_request.game_type,
            game_request.players,
            game_request.config
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Store in database
    game = Game(
        id=game_id,
        game_type=game_request.game_type.lower(),
        players=json.dumps(game_request.players),
        bot_id=current_bot.id,
        status="active",
        current_state=json.dumps({})
    )
    
    db.add(game)
    db.commit()
    db.refresh(game)
    
    return CreateGameResponse(
        game_id=game_id,
        game_type=game_request.game_type.lower(),
        players=game_request.players,
        status="active",
        created_at=game.created_at
    )


@router.get(
    "/{game_id}",
    response_model=GameStateResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"},
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def get_game_state(
    game_id: str,
    request: Request,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """
    Get current state of a game.
    
    Returns complete game information including valid moves.
    """
    check_bot_rate_limit(request, current_bot.id)
    
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Recreate game instance to get current state
    players = json.loads(game.players)
    try:
        game_instance = create_game_instance(game.game_type, players, {})
        
        # Replay moves to get current state
        for move in game.moves:
            game_move = GameMove(player=move.player, action=move.action)
            game_instance.apply_move(game_move)
            
    except Exception as e:
        # Fallback response if game reconstruction fails
        return GameStateResponse(
            game_id=game.id,
            game_type=game.game_type,
            players=players,
            status=game.status,
            current_player=None,
            game_over=game.status == "completed",
            winner=game.winner,
            valid_moves=[],
            moves_count=len(game.moves),
            created_at=game.created_at,
            metadata={"error": "Could not reconstruct game state"}
        )
    
    return game_state_to_response(game, game_instance)


@router.post(
    "/{game_id}/moves",
    response_model=MakeMoveResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"},
        400: {"model": ErrorResponse, "description": "Invalid move"},
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def make_move(
    game_id: str,
    move_request: MakeMoveRequest,
    request: Request,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db)
):
    """
    Make a move in a game.
    
    For RPS: action should be "rock", "paper", or "scissors"
    """
    check_bot_rate_limit(request, current_bot.id)
    
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status != "active":
        raise HTTPException(status_code=400, detail="Game is not active")
    
    # Recreate game instance
    players = json.loads(game.players)
    try:
        game_instance = create_game_instance(game.game_type, players, {})
        
        # Replay existing moves
        for move in game.moves:
            game_move = GameMove(player=move.player, action=move.action)
            game_instance.apply_move(game_move)
        
        # Apply new move
        new_move = GameMove(
            player=move_request.player,
            action=move_request.action
        )
        new_state = game_instance.apply_move(new_move)
        
    except Exception as e:
        return MakeMoveResponse(
            success=False,
            message=f"Invalid move: {str(e)}",
            game_state=game_state_to_response(game, None)
        )
    
    # Store move in database
    db_move = Move(
        game_id=game_id,
        bot_id=current_bot.id,
        player=move_request.player,
        action=move_request.action,
        data=json.dumps(move_request.data)
    )
    db.add(db_move)
    
    # Update game status if completed
    if game_instance.state.game_over:
        game.status = "completed"
        game.winner = game_instance.state.winner
        game.completed_at = datetime.utcnow()
    
    db.commit()
    
    return MakeMoveResponse(
        success=True,
        message="Move made successfully",
        game_state=game_state_to_response(game, game_instance)
    )


@router.get(
    "/",
    response_model=GameListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"}
    }
)
async def list_games(
    request: Request,
    current_bot: Bot = Depends(get_current_bot),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by game status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Games per page")
):
    """
    List games created by the authenticated bot.
    
    Optional filters:
    - status: Filter by game status (active, completed, abandoned)
    - page: Page number (1-based)
    - page_size: Number of games per page (1-100)
    """
    check_bot_rate_limit(request, current_bot.id)
    
    query = db.query(Game).filter(Game.bot_id == current_bot.id)
    
    if status:
        query = query.filter(Game.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    games = query.offset(offset).limit(page_size).all()
    
    # Convert to response format
    game_responses = []
    for game in games:
        players = json.loads(game.players)
        game_responses.append(GameStateResponse(
            game_id=game.id,
            game_type=game.game_type,
            players=players,
            status=game.status,
            current_player=None,  # Don't reconstruct full state for list
            game_over=game.status == "completed",
            winner=game.winner,
            valid_moves=[],
            moves_count=len(game.moves),
            created_at=game.created_at,
            metadata={}
        ))
    
    return GameListResponse(
        games=game_responses,
        total=total,
        page=page,
        page_size=page_size
    )