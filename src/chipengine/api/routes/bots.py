"""
Bot API routes for ChipEngine.

Provides REST endpoints for bot registration and game management.
"""

from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status

from ..models import (
    RegisterBotRequest, RegisterBotResponse,
    BotInfoResponse, BotCreateGameRequest, BotCreateGameResponse,
    BotMakeMoveRequest, MakeMoveResponse, GameStateResponse,
    BotGameListResponse
)
from ..auth import bot_auth_manager, verify_api_key, BotInfo
from ..game_manager import game_manager

router = APIRouter(prefix="/api/bots", tags=["bots"])


# Bot-specific game tracking
bot_games: Dict[str, List[str]] = {}  # bot_id -> list of game_ids


@router.post("/register", response_model=RegisterBotResponse)
async def register_bot(request: RegisterBotRequest):
    """
    Register a new bot and receive an API key.
    
    The API key must be included in all subsequent requests as the X-API-Key header.
    """
    try:
        bot_info = bot_auth_manager.register_bot(request.name)
        
        # Initialize bot's game list
        bot_games[bot_info.bot_id] = []
        
        return RegisterBotResponse(
            bot_id=bot_info.bot_id,
            name=bot_info.name,
            api_key=bot_info.api_key,
            created_at=bot_info.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register bot: {str(e)}"
        )


@router.get("/{bot_id}", response_model=BotInfoResponse)
async def get_bot_info(
    bot_id: str,
    bot: BotInfo = Depends(verify_api_key)
):
    """
    Get information about a bot.
    
    Bots can only retrieve their own information.
    """
    # Verify bot is requesting its own info
    if bot.bot_id != bot_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other bot's information"
        )
    
    return BotInfoResponse(
        bot_id=bot.bot_id,
        name=bot.name,
        created_at=bot.created_at.isoformat(),
        games_created=bot.games_created,
        last_request_time=bot.last_request_time.isoformat() if bot.last_request_time else None,
        rate_limit=bot.rate_limit
    )


@router.post("/games", response_model=BotCreateGameResponse)
async def create_bot_game(
    request: BotCreateGameRequest,
    bot: BotInfo = Depends(verify_api_key)
):
    """
    Create a new game as a bot.
    
    If opponent_bot_id is provided, the game will be created with that bot as the opponent.
    Otherwise, the game will be created with a placeholder for a human or another bot to join.
    """
    try:
        # Determine players
        players = [bot.bot_id]
        
        if request.opponent_bot_id:
            # Verify opponent bot exists
            opponent = bot_auth_manager.get_bot_by_id(request.opponent_bot_id)
            if not opponent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Opponent bot not found"
                )
            players.append(request.opponent_bot_id)
        else:
            # Add placeholder for second player
            players.append("waiting_for_opponent")
        
        # Create the game
        game_id = game_manager.create_game(
            game_type=request.game_type,
            players=players,
            config=request.config
        )
        
        # Track game for bot
        if bot.bot_id not in bot_games:
            bot_games[bot.bot_id] = []
        bot_games[bot.bot_id].append(game_id)
        
        # Track game for opponent bot if specified
        if request.opponent_bot_id and request.opponent_bot_id in bot_games:
            bot_games[request.opponent_bot_id].append(game_id)
        
        # Update bot's games created counter
        bot_auth_manager.increment_games_created(bot.bot_id)
        
        return BotCreateGameResponse(
            game_id=game_id,
            game_type=request.game_type,
            players=players,
            status="created",
            your_player_id=bot.bot_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/games/{game_id}", response_model=GameStateResponse)
async def get_bot_game_state(
    game_id: str,
    bot: BotInfo = Depends(verify_api_key)
):
    """
    Get the current state of a game.
    
    Bots can only access games they are participating in.
    """
    try:
        # Verify bot is in the game
        game = game_manager.get_game(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        if bot.bot_id not in game.players:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this game"
            )
        
        state_data = game_manager.get_game_state(game_id)
        
        return GameStateResponse(
            game_id=state_data["game_id"],
            players=state_data["players"],
            current_player=state_data["current_player"],
            game_over=state_data["game_over"],
            winner=state_data["winner"],
            valid_moves=state_data["valid_moves_per_player"],
            metadata=state_data["metadata"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/games/{game_id}/move", response_model=MakeMoveResponse)
async def make_bot_move(
    game_id: str,
    request: BotMakeMoveRequest,
    bot: BotInfo = Depends(verify_api_key)
):
    """
    Make a move in a game.
    
    Bots can only make moves for themselves in games they are participating in.
    """
    try:
        # Verify bot is in the game
        game = game_manager.get_game(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        if bot.bot_id not in game.players:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this game"
            )
        
        # Make the move
        game = game_manager.make_move(
            game_id=game_id,
            player=bot.bot_id,
            action=request.action,
            data=request.data
        )
        
        # Get updated game state
        state_data = game_manager.get_game_state(game_id)
        game_state = GameStateResponse(
            game_id=state_data["game_id"],
            players=state_data["players"],
            current_player=state_data["current_player"],
            game_over=state_data["game_over"],
            winner=state_data["winner"],
            valid_moves=state_data["valid_moves_per_player"],
            metadata=state_data["metadata"]
        )
        
        return MakeMoveResponse(
            success=True,
            message="Move applied successfully",
            game_state=game_state
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/games", response_model=BotGameListResponse)
async def list_bot_games(
    bot: BotInfo = Depends(verify_api_key),
    status_filter: Optional[str] = None  # "active", "completed", or None for all
):
    """
    List all games for the authenticated bot.
    
    Optionally filter by game status (active or completed).
    """
    bot_game_ids = bot_games.get(bot.bot_id, [])
    
    games_list = []
    active_count = 0
    completed_count = 0
    
    for game_id in bot_game_ids:
        game = game_manager.get_game(game_id)
        if game:
            is_completed = game.is_game_over()
            
            # Apply status filter if provided
            if status_filter == "active" and is_completed:
                continue
            elif status_filter == "completed" and not is_completed:
                continue
            
            # Count games by status
            if is_completed:
                completed_count += 1
            else:
                active_count += 1
            
            # Get game info
            state = game.get_state()
            game_info = {
                "game_id": game_id,
                "game_type": type(game).__name__.replace("Game", "").lower(),
                "players": state.players,
                "current_player": state.current_player,
                "game_over": is_completed,
                "winner": game.get_winner() if is_completed else None,
                "created_at": state.metadata.get("created_at", "unknown")
            }
            games_list.append(game_info)
    
    # Sort by creation time (most recent first)
    games_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return BotGameListResponse(
        games=games_list,
        total_games=len(games_list),
        active_games=active_count,
        completed_games=completed_count
    )


@router.get("/stats")
async def get_bot_stats(bot: BotInfo = Depends(verify_api_key)):
    """
    Get statistics for the authenticated bot.
    
    Returns various metrics about the bot's activity and performance.
    """
    bot_game_ids = bot_games.get(bot.bot_id, [])
    
    # Calculate statistics
    total_games = len(bot_game_ids)
    wins = 0
    losses = 0
    active_games = 0
    
    game_types = {}
    
    for game_id in bot_game_ids:
        game = game_manager.get_game(game_id)
        if game:
            game_type = type(game).__name__.replace("Game", "").lower()
            game_types[game_type] = game_types.get(game_type, 0) + 1
            
            if game.is_game_over():
                winner = game.get_winner()
                if winner == bot.bot_id:
                    wins += 1
                elif winner is not None:  # Not a draw
                    losses += 1
            else:
                active_games += 1
    
    # Calculate rate limit usage
    requests_in_window = bot_auth_manager.rate_limiter.get_requests_count(bot.bot_id)
    
    return {
        "bot_id": bot.bot_id,
        "name": bot.name,
        "created_at": bot.created_at.isoformat(),
        "total_games": total_games,
        "active_games": active_games,
        "completed_games": total_games - active_games,
        "wins": wins,
        "losses": losses,
        "draws": total_games - active_games - wins - losses,
        "win_rate": wins / (wins + losses) if (wins + losses) > 0 else 0,
        "game_types_played": game_types,
        "rate_limit_usage": {
            "current_requests": requests_in_window,
            "max_requests": bot.rate_limit,
            "window_seconds": 60
        },
        "last_request_time": bot.last_request_time.isoformat() if bot.last_request_time else None
    }