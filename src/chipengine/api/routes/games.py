"""
Game API routes for ChipEngine.

Provides REST endpoints for:
- Creating games
- Making moves  
- Getting game state
- Retrieving results
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models import (
    CreateGameRequest, CreateGameResponse,
    MakeMoveRequest, MakeMoveResponse,
    GameStateResponse, GameResultResponse
)
from ..game_manager import game_manager

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=CreateGameResponse)
async def create_game(request: CreateGameRequest):
    """Create a new game."""
    try:
        game_id = game_manager.create_game(
            game_type=request.game_type,
            players=request.players,
            config=request.config
        )
        
        return CreateGameResponse(
            game_id=game_id,
            game_type=request.game_type,
            players=request.players,
            status="created"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    """Get current game state."""
    try:
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
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/moves", response_model=MakeMoveResponse)
async def make_move(game_id: str, request: MakeMoveRequest):
    """Make a move in a game."""
    try:
        game = game_manager.make_move(
            game_id=game_id,
            player=request.player,
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
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{game_id}/result", response_model=GameResultResponse)
async def get_game_result(game_id: str):
    """Get game result (only available when game is finished)."""
    try:
        game = game_manager.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        result = game.get_game_result()
        if not result:
            raise HTTPException(status_code=400, detail="Game not finished yet")
        
        return GameResultResponse(
            game_id=result.game_id,
            winner=result.winner,
            players=result.players,
            duration_seconds=result.duration_seconds,
            metadata=result.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{game_id}")
async def delete_game(game_id: str):
    """Delete a game."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game_id in game_manager.active_games:
        del game_manager.active_games[game_id]
    
    return {"message": "Game deleted successfully"}


@router.get("/stats")
async def get_stats():
    """Get game manager statistics."""
    return game_manager.get_stats()


@router.post("/cleanup")
async def cleanup_finished_games():
    """Clean up finished games from memory."""
    cleaned_count = game_manager.cleanup_finished_games()
    return {"message": f"Cleaned up {cleaned_count} finished games"}