"""
Game history recording module for ChipEngine.

Handles persisting game states, moves, and results to the database.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import engine
from ..database.models import Game, Player, Move, Bot, GameStatus
from ..core.base_game import BaseGame, Move as GameMove, GameResult


class GameHistoryRecorder:
    """
    Records game history to the database.
    
    Responsible for:
    - Creating game records when games start
    - Recording moves as they happen
    - Updating game state and results
    - Associating games with bots/players
    """
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        """Context manager entry."""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        self.session = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
            self.session.close()
    
    def create_game_record(
        self, 
        game_id: str, 
        game_type: str, 
        player_bot_ids: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Game:
        """Create a new game record in the database."""
        # Create game record
        game_record = Game(
            id=game_id,
            game_type=game_type,
            status=GameStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            config=config or {},
            state={}
        )
        self.session.add(game_record)
        
        # Create player records
        for idx, bot_id in enumerate(player_bot_ids):
            player = Player(
                bot_id=bot_id,
                game_id=game_id,
                player_number=idx,
                joined_at=datetime.utcnow()
            )
            self.session.add(player)
        
        self.session.flush()  # Ensure IDs are generated
        return game_record
    
    def record_move(
        self,
        game_id: str,
        player_bot_id: str,
        move: GameMove,
        move_number: int,
        time_taken_ms: Optional[int] = None
    ) -> Move:
        """Record a move in the database."""
        # Find the player record
        player = self.session.query(Player).filter_by(
            game_id=game_id,
            bot_id=player_bot_id
        ).first()
        
        if not player:
            raise ValueError(f"Player {player_bot_id} not found in game {game_id}")
        
        # Create move record
        move_record = Move(
            game_id=game_id,
            player_id=player.id,
            move_data={
                "action": move.action,
                "data": move.data
            },
            move_number=move_number,
            time_taken_ms=time_taken_ms,
            timestamp=datetime.utcnow()
        )
        self.session.add(move_record)
        self.session.flush()
        
        return move_record
    
    def update_game_state(self, game_id: str, state: Dict[str, Any]):
        """Update the game state in the database."""
        game = self.session.query(Game).filter_by(id=game_id).first()
        if game:
            game.state = state
            self.session.flush()
    
    def complete_game(
        self,
        game_id: str,
        result: GameResult,
        final_state: Dict[str, Any]
    ):
        """Mark a game as completed and record the result."""
        game = self.session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError(f"Game {game_id} not found")
        
        # Update game record
        game.status = GameStatus.COMPLETED
        game.completed_at = datetime.utcnow()
        game.state = final_state
        
        # Set winner if there is one
        if result.winner:
            # Find the winning bot
            winning_player = self.session.query(Player).join(Bot).filter(
                Player.game_id == game_id,
                Bot.id == result.winner
            ).first()
            
            if winning_player:
                game.winner_id = result.winner
        
        # Update player positions based on result
        if "final_scores" in result.metadata:
            scores = result.metadata["final_scores"]
            sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            for position, (bot_id, score) in enumerate(sorted_players, 1):
                player = self.session.query(Player).filter_by(
                    game_id=game_id,
                    bot_id=bot_id
                ).first()
                
                if player:
                    player.final_position = position
                    player.score = score
        
        self.session.flush()
    
    def get_game_history(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete game history."""
        game = self.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return None
        
        # Get all players
        players = self.session.query(Player).filter_by(game_id=game_id).all()
        
        # Get all moves
        moves = self.session.query(Move).filter_by(game_id=game_id).order_by(Move.timestamp).all()
        
        return {
            "game": {
                "id": game.id,
                "type": game.game_type,
                "status": game.status.value,
                "created_at": game.created_at.isoformat() if game.created_at else None,
                "completed_at": game.completed_at.isoformat() if game.completed_at else None,
                "winner_id": game.winner_id,
                "config": game.config,
                "state": game.state
            },
            "players": [
                {
                    "bot_id": p.bot_id,
                    "player_number": p.player_number,
                    "final_position": p.final_position,
                    "score": p.score
                }
                for p in players
            ],
            "moves": [
                {
                    "player_bot_id": next((p.bot_id for p in players if p.id == m.player_id), None),
                    "move_data": m.move_data,
                    "move_number": m.move_number,
                    "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                    "time_taken_ms": m.time_taken_ms
                }
                for m in moves
            ]
        }


def record_game_to_database(game: BaseGame, player_bot_ids: List[str]):
    """
    Convenience function to record an entire game to the database.
    
    This is useful for games that don't need real-time move recording.
    """
    with GameHistoryRecorder() as recorder:
        # Create game record
        game_type = game.__class__.__name__.replace("Game", "").lower()
        recorder.create_game_record(
            game_id=game.game_id,
            game_type=game_type,
            player_bot_ids=player_bot_ids,
            config=getattr(game.state, "metadata", {})
        )
        
        # Record all moves
        for idx, move in enumerate(game.moves):
            # Map player name to bot_id
            bot_id = player_bot_ids[game.players.index(move.player)]
            recorder.record_move(
                game_id=game.game_id,
                player_bot_id=bot_id,
                move=move,
                move_number=idx + 1
            )
        
        # Complete the game if it's over
        if game.is_game_over():
            result = game.get_game_result()
            if result:
                # Map winner player name to bot_id if there's a winner
                if result.winner:
                    winner_bot_id = player_bot_ids[game.players.index(result.winner)]
                    result.winner = winner_bot_id
                
                recorder.complete_game(
                    game_id=game.game_id,
                    result=result,
                    final_state=game.state.dict() if hasattr(game.state, 'dict') else vars(game.state)
                )