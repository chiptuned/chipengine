"""API models for ChipEngine."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CreateGameRequest(BaseModel):
    """Request to create a new game."""
    game_type: str
    players: List[str]
    config: Dict[str, Any] = {}


class CreateGameResponse(BaseModel):
    """Response when creating a game."""
    game_id: str
    game_type: str
    players: List[str]
    status: str


class MakeMoveRequest(BaseModel):
    """Request to make a move in a game."""
    player: str
    action: str
    data: Dict[str, Any] = {}


class GameStateResponse(BaseModel):
    """Response containing current game state."""
    game_id: str
    players: List[str]
    current_player: Optional[str]
    game_over: bool
    winner: Optional[str]
    valid_moves: List[str]
    metadata: Dict[str, Any] = {}


class MakeMoveResponse(BaseModel):
    """Response after making a move."""
    success: bool
    message: str
    game_state: GameStateResponse


class GameResultResponse(BaseModel):
    """Response containing final game result."""
    game_id: str
    winner: Optional[str]
    players: List[str]
    duration_seconds: float
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str