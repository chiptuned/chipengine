"""API models for ChipEngine."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Bot Registration Models
class BotRegistrationRequest(BaseModel):
    """Request to register a new bot."""
    name: str = Field(..., min_length=1, max_length=100, description="Bot name")


class BotRegistrationResponse(BaseModel):
    """Response after bot registration."""
    bot_id: int
    name: str
    api_key: str
    message: str


class BotInfoResponse(BaseModel):
    """Bot information response."""
    bot_id: int
    name: str
    created_at: datetime
    is_active: bool


# Game Management Models
class CreateGameRequest(BaseModel):
    """Request to create a new game."""
    game_type: str = Field(..., description="Type of game (e.g., 'rps')")
    players: List[str] = Field(..., min_items=2, max_items=10, description="List of player names")
    config: Dict[str, Any] = Field(default_factory=dict, description="Game configuration")


class CreateGameResponse(BaseModel):
    """Response when creating a game."""
    game_id: str
    game_type: str
    players: List[str]
    status: str
    created_at: datetime


class MakeMoveRequest(BaseModel):
    """Request to make a move in a game."""
    player: str = Field(..., description="Player making the move")
    action: str = Field(..., description="Action/move to make")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional move data")


class GameStateResponse(BaseModel):
    """Response containing current game state."""
    game_id: str
    game_type: str
    players: List[str]
    status: str
    current_player: Optional[str]
    game_over: bool
    winner: Optional[str]
    valid_moves: List[str]
    moves_count: int
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MakeMoveResponse(BaseModel):
    """Response after making a move."""
    success: bool
    message: str
    game_state: GameStateResponse


class GameResultResponse(BaseModel):
    """Response containing final game result."""
    game_id: str
    game_type: str
    winner: Optional[str]
    players: List[str]
    duration_seconds: float
    moves_count: int
    completed_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GameListResponse(BaseModel):
    """Response for listing games."""
    games: List[GameStateResponse]
    total: int
    page: int
    page_size: int


# Health and Status Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    bots_count: int
    active_games: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str
    code: int