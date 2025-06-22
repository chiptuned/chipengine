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
    valid_moves: Dict[str, List[str]]
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


class StressTestRequest(BaseModel):
    """Request to start a stress test."""
    game_type: str = "rps"
    concurrent_games: int = 100
    games_per_second: int = 50
    duration_seconds: int = 60
    total_games: Optional[int] = None


class StressTestResponse(BaseModel):
    """Response when starting a stress test."""
    test_id: str
    status: str
    config: StressTestRequest
    started_at: str


class StressTestStatus(BaseModel):
    """Current status of a stress test."""
    test_id: str
    status: str
    started_at: str
    elapsed_seconds: float
    games_created: int
    games_completed: int
    games_failed: int
    current_rps: float
    peak_rps: float
    avg_game_duration: float
    errors: List[str]
    config: StressTestRequest


class StressTestMetrics(BaseModel):
    """Detailed metrics for a stress test."""
    test_id: str
    performance: Dict[str, float]
    counters: Dict[str, int]
    timing: Dict[str, float]
    errors: List[str]


# Bot API Models
class RegisterBotRequest(BaseModel):
    """Request to register a new bot."""
    name: str


class RegisterBotResponse(BaseModel):
    """Response when registering a bot."""
    bot_id: str
    name: str
    api_key: str
    created_at: str


class BotInfoResponse(BaseModel):
    """Bot information response."""
    bot_id: str
    name: str
    created_at: str
    games_created: int
    last_request_time: Optional[str]
    rate_limit: int


class BotCreateGameRequest(BaseModel):
    """Request for bot to create a game."""
    game_type: str
    opponent_bot_id: Optional[str] = None  # If playing against another bot
    config: Dict[str, Any] = {}


class BotCreateGameResponse(BaseModel):
    """Response when bot creates a game."""
    game_id: str
    game_type: str
    players: List[str]
    status: str
    your_player_id: str


class BotMakeMoveRequest(BaseModel):
    """Request for bot to make a move."""
    action: str
    data: Dict[str, Any] = {}


class BotGameListResponse(BaseModel):
    """Response listing bot's games."""
    games: List[Dict[str, Any]]
    total_games: int
    active_games: int
    completed_games: int