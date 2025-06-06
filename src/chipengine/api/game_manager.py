"""
Game Manager for ChipEngine.

Handles game creation, state management, and coordination.
"""

import uuid
from typing import Dict, Optional
from datetime import datetime

from ..core.base_game import BaseGame, Move
from ..games.rps import RockPaperScissorsGame


class GameManager:
    """
    Manages all active games in the system.
    
    Provides a centralized way to:
    - Create new games
    - Track active games
    - Process moves
    - Clean up finished games
    """
    
    def __init__(self):
        self.active_games: Dict[str, BaseGame] = {}
        self.game_registry = {
            "rps": RockPaperScissorsGame,
            "rock_paper_scissors": RockPaperScissorsGame
        }
    
    def create_game(self, game_type: str, players: list, config: dict = None) -> str:
        """Create a new game and return game ID."""
        if game_type not in self.game_registry:
            raise ValueError(f"Unknown game type: {game_type}")
        
        game_id = str(uuid.uuid4())
        game_class = self.game_registry[game_type]
        
        # Handle game-specific configuration
        if config is None:
            config = {}
        
        if game_type in ["rps", "rock_paper_scissors"]:
            total_rounds = config.get("total_rounds", 1)
            game = game_class(game_id, players, total_rounds)
        else:
            game = game_class(game_id, players)
        
        self.active_games[game_id] = game
        return game_id
    
    def get_game(self, game_id: str) -> Optional[BaseGame]:
        """Get a game by ID."""
        return self.active_games.get(game_id)
    
    def make_move(self, game_id: str, player: str, action: str, data: dict = None) -> BaseGame:
        """Make a move in a game."""
        game = self.get_game(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")
        
        move = Move(
            player=player,
            action=action,
            data=data or {}
        )
        
        game.apply_move(move)
        return game
    
    def get_game_state(self, game_id: str) -> dict:
        """Get current game state."""
        game = self.get_game(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")
        
        state = game.get_state()
        
        # Get valid moves for all players
        valid_moves_per_player = {}
        for player in game.players:
            valid_moves_per_player[player] = game.get_valid_moves(player)
        
        return {
            "game_id": game_id,
            "players": state.players,
            "current_player": state.current_player,
            "game_over": game.is_game_over(),
            "winner": game.get_winner(),
            "valid_moves_per_player": valid_moves_per_player,
            "metadata": state.metadata
        }
    
    def cleanup_finished_games(self):
        """Remove finished games from memory."""
        finished_games = [
            game_id for game_id, game in self.active_games.items()
            if game.is_game_over()
        ]
        
        for game_id in finished_games:
            del self.active_games[game_id]
        
        return len(finished_games)
    
    def get_stats(self) -> dict:
        """Get manager statistics."""
        active_count = len(self.active_games)
        finished_count = sum(1 for game in self.active_games.values() if game.is_game_over())
        
        return {
            "active_games": active_count,
            "finished_games": finished_count,
            "supported_games": list(self.game_registry.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global game manager instance
game_manager = GameManager()