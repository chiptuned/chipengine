"""
Game Manager for ChipEngine.

Handles game creation, state management, and coordination.
"""

import uuid
from typing import Dict, Optional, List
from datetime import datetime
import asyncio

from ..core.base_game import BaseGame, Move
from ..games.rps import RockPaperScissorsGame
from ..database.models import Game as GameModel, Player as PlayerModel, Move as MoveModel, GameStatus
from ..database.session import DatabaseSession


class GameManager:
    """
    Manages all active games in the system.
    
    Provides a centralized way to:
    - Create new games
    - Track active games
    - Process moves
    - Clean up finished games
    - Broadcast real-time updates via WebSocket
    """
    
    def __init__(self):
        self.active_games: Dict[str, BaseGame] = {}
        self.game_registry = {
            "rps": RockPaperScissorsGame,
            "rock_paper_scissors": RockPaperScissorsGame
        }
        self.move_counter: Dict[str, int] = {}  # Track move numbers per game
        self.websocket_manager = None  # Will be set after import
    
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
        
        # Add creation metadata
        if hasattr(game, 'state') and hasattr(game.state, 'metadata'):
            game.state.metadata['created_at'] = datetime.utcnow().isoformat()
            game.state.metadata['game_type'] = game_type
        
        self.active_games[game_id] = game
        self.move_counter[game_id] = 0
        
        # Save to database
        self._save_game_to_database(game_id, game_type, players, config)
        
        # Broadcast game creation
        asyncio.create_task(self._broadcast_game_created(game_id, game))
        
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
        
        # Record move start time
        move_start = datetime.utcnow()
        
        game.apply_move(move)
        
        # Calculate time taken
        time_taken_ms = int((datetime.utcnow() - move_start).total_seconds() * 1000)
        
        # Save move to database
        self.move_counter[game_id] += 1
        self._save_move_to_database(game_id, player, action, data, self.move_counter[game_id], time_taken_ms)
        
        # Update game state in database
        self._update_game_state(game_id, game)
        
        # Broadcast move and state update
        asyncio.create_task(self._broadcast_move(game_id, player, action, data, game))
        
        # Check if game is over
        if game.is_game_over():
            asyncio.create_task(self._broadcast_game_over(game_id, game))
        
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
        """Remove finished games from memory and mark as completed in database."""
        finished_games = [
            game_id for game_id, game in self.active_games.items()
            if game.is_game_over()
        ]
        
        for game_id in finished_games:
            game = self.active_games[game_id]
            # Mark game as completed in database
            self._mark_game_completed(game_id, game)
            del self.active_games[game_id]
            if game_id in self.move_counter:
                del self.move_counter[game_id]
        
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


    def _save_game_to_database(self, game_id: str, game_type: str, players: List[str], config: dict) -> None:
        """Save a new game to the database."""
        with DatabaseSession() as db:
            # Create game record
            game_model = GameModel(
                id=game_id,
                game_type=game_type,
                state={},
                status=GameStatus.IN_PROGRESS,
                config=config
            )
            db.add(game_model)
            
            # Create player records
            for idx, player_name in enumerate(players):
                player_model = PlayerModel(
                    bot_id=player_name,  # Using player name as bot_id for compatibility
                    game_id=game_id,
                    player_number=idx + 1
                )
                db.add(player_model)
            
            db.commit()
    
    def _save_move_to_database(self, game_id: str, player: str, action: str, 
                              data: dict, move_number: int, time_taken_ms: int) -> None:
        """Save a move to the database."""
        with DatabaseSession() as db:
            # Find the player record
            player_model = db.query(PlayerModel).filter(
                PlayerModel.game_id == game_id,
                PlayerModel.bot_id == player
            ).first()
            
            if player_model:
                move_model = MoveModel(
                    game_id=game_id,
                    player_id=player_model.id,
                    move_data={
                        "action": action,
                        "data": data
                    },
                    move_number=move_number,
                    time_taken_ms=time_taken_ms
                )
                db.add(move_model)
                db.commit()
    
    def _update_game_state(self, game_id: str, game: BaseGame) -> None:
        """Update game state in the database."""
        with DatabaseSession() as db:
            game_model = db.query(GameModel).filter(GameModel.id == game_id).first()
            if game_model:
                # Serialize game state
                state = game.get_state()
                game_model.state = {
                    "players": state.players,
                    "current_player": state.current_player,
                    "metadata": state.metadata,
                    "game_over": game.is_game_over(),
                    "winner": game.get_winner()
                }
                
                # Add scores if available (for RPS games)
                if hasattr(state, 'scores'):
                    game_model.state['scores'] = state.scores
                
                # Update status if game is over
                if game.is_game_over():
                    game_model.status = GameStatus.COMPLETED
                
                db.commit()
    
    def _mark_game_completed(self, game_id: str, game: BaseGame) -> None:
        """Mark a game as completed in the database."""
        with DatabaseSession() as db:
            game_model = db.query(GameModel).filter(GameModel.id == game_id).first()
            if game_model:
                game_model.status = GameStatus.COMPLETED
                game_model.completed_at = datetime.utcnow()
                
                # Set winner if exists
                winner = game.get_winner()
                if winner:
                    winner_player = db.query(PlayerModel).filter(
                        PlayerModel.game_id == game_id,
                        PlayerModel.bot_id == winner
                    ).first()
                    if winner_player:
                        game_model.winner_id = winner_player.bot_id
                
                # Update final game state
                self._update_game_state(game_id, game)
                
                # Update player final positions
                state = game.get_state()
                # For RPS games, scores are directly in the state
                scores = None
                if hasattr(state, 'scores'):
                    scores = state.scores
                elif hasattr(state, 'metadata') and 'scores' in state.metadata:
                    scores = state.metadata['scores']
                
                if scores:
                    sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                    
                    for position, (player_name, score) in enumerate(sorted_players, 1):
                        player_model = db.query(PlayerModel).filter(
                            PlayerModel.game_id == game_id,
                            PlayerModel.bot_id == player_name
                        ).first()
                        if player_model:
                            player_model.final_position = position
                            player_model.score = score
                
                db.commit()
    
    async def _broadcast_game_created(self, game_id: str, game: BaseGame) -> None:
        """Broadcast game creation event."""
        if self.websocket_manager:
            state = self.get_game_state(game_id)
            await self.websocket_manager.broadcast_game_update(game_id, {
                "type": "game_created",
                "state": state
            })
    
    async def _broadcast_move(self, game_id: str, player: str, action: str, data: dict, game: BaseGame) -> None:
        """Broadcast move event."""
        if self.websocket_manager:
            state = self.get_game_state(game_id)
            await self.websocket_manager.broadcast_move(
                game_id,
                player,
                {"action": action, "data": data},
                {"state": state}
            )
    
    async def _broadcast_game_over(self, game_id: str, game: BaseGame) -> None:
        """Broadcast game over event."""
        if self.websocket_manager:
            state = self.get_game_state(game_id)
            winner = game.get_winner()
            await self.websocket_manager.broadcast_game_over(game_id, winner, state)


# Global game manager instance
game_manager = GameManager()

# Import websocket manager after creating game_manager to avoid circular import
from .websockets import manager as ws_manager
game_manager.websocket_manager = ws_manager