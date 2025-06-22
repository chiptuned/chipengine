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


# Statistics API Models
class GameSummary(BaseModel):
    """Summary information for a game."""
    game_id: str
    game_type: str
    status: str
    created_at: str
    completed_at: Optional[str]
    players: List[Dict[str, Any]]
    winner_id: Optional[str]
    duration_seconds: Optional[float]


class GameDetail(BaseModel):
    """Detailed game information including moves."""
    game_id: str
    game_type: str
    status: str
    created_at: str
    completed_at: Optional[str]
    config: Dict[str, Any]
    state: Dict[str, Any]
    players: List[Dict[str, Any]]
    moves: List[Dict[str, Any]]
    winner_id: Optional[str]
    duration_seconds: Optional[float]


class BotStatistics(BaseModel):
    """Bot performance statistics."""
    bot_id: str
    bot_name: str
    total_games: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    avg_game_duration: float
    games_by_type: Dict[str, int]
    recent_games: List[GameSummary]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry for a bot."""
    rank: int
    bot_id: str
    bot_name: str
    games_played: int
    wins: int
    win_rate: float
    points: int


class PlatformStatistics(BaseModel):
    """Platform-wide statistics."""
    total_games: int
    active_games: int
    completed_games: int
    total_bots: int
    active_bots: int
    games_last_24h: int
    games_last_7d: int
    popular_game_types: Dict[str, int]
    peak_concurrent_games: int
    avg_game_duration: float


# Tournament API Models
class CreateTournamentRequest(BaseModel):
    """Request to create a new tournament."""
    name: str
    game_type: str
    format: str = "single_elimination"
    max_participants: Optional[int] = None
    config: Dict[str, Any] = {}


class CreateTournamentResponse(BaseModel):
    """Response when creating a tournament."""
    tournament_id: str
    name: str
    game_type: str
    format: str
    status: str
    max_participants: Optional[int]
    created_at: str


class JoinTournamentRequest(BaseModel):
    """Request to join a tournament."""
    bot_id: str


class JoinTournamentResponse(BaseModel):
    """Response when joining a tournament."""
    tournament_id: str
    bot_id: str
    seed: Optional[int]
    registered_at: str


class TournamentInfo(BaseModel):
    """Tournament information."""
    tournament_id: str
    name: str
    game_type: str
    format: str
    status: str
    created_at: str
    start_time: Optional[str]
    end_time: Optional[str]
    max_participants: Optional[int]
    current_participants: int
    config: Dict[str, Any]


class TournamentListResponse(BaseModel):
    """Response listing tournaments."""
    tournaments: List[TournamentInfo]
    total: int


class BracketResponse(BaseModel):
    """Tournament bracket/standings response."""
    tournament_id: str
    format: str
    status: str
    data: Dict[str, Any]