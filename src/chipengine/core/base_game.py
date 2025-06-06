"""
BaseGame interface for all games in ChipEngine.

This defines the common interface that all games must implement,
enabling the multi-game architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel


class GameState(BaseModel):
    """Base game state that all games inherit from."""
    game_id: str
    players: List[str]
    current_player: Optional[str] = None
    game_over: bool = False
    winner: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Move(BaseModel):
    """Base move class that all games inherit from."""
    player: str
    action: str
    data: Dict[str, Any] = {}


class GameResult(BaseModel):
    """Game result with winner and statistics."""
    game_id: str
    winner: Optional[str]
    players: List[str]
    moves: List[Move]
    duration_seconds: float
    metadata: Dict[str, Any] = {}


class BaseGame(ABC):
    """
    Abstract base class for all games in ChipEngine.
    
    This interface ensures that all games can be:
    - Created with consistent parameters
    - Played through a standard API
    - Integrated into tournaments
    - Extended with new features
    """
    
    def __init__(self, game_id: str, players: List[str]):
        self.game_id = game_id
        self.players = players
        self.state = self._initialize_state()
    
    @abstractmethod
    def _initialize_state(self) -> GameState:
        """Initialize the game state for this specific game."""
        pass
    
    @abstractmethod
    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid in the current game state."""
        pass
    
    @abstractmethod
    def apply_move(self, move: Move) -> GameState:
        """Apply a move and return the new game state."""
        pass
    
    @abstractmethod
    def get_valid_moves(self, player: str) -> List[str]:
        """Get list of valid moves for a player."""
        pass
    
    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if the game is finished."""
        pass
    
    @abstractmethod
    def get_winner(self) -> Optional[str]:
        """Get the winner if the game is over."""
        pass
    
    def get_state(self) -> GameState:
        """Get the current game state."""
        return self.state
    
    def get_game_result(self) -> Optional[GameResult]:
        """Get the final game result if the game is over."""
        if not self.is_game_over():
            return None
        
        return GameResult(
            game_id=self.game_id,
            winner=self.get_winner(),
            players=self.players,
            moves=getattr(self, 'moves', []),
            duration_seconds=getattr(self, 'duration', 0.0),
            metadata=self.state.metadata
        )