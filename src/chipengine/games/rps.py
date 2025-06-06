"""
Rock Paper Scissors game implementation.

Fast, simple implementation perfect for testing the bot competition platform.
"""

import time
from typing import Dict, List, Optional
from enum import Enum

from ..core.base_game import BaseGame, GameState, Move, GameResult


class RPSChoice(Enum):
    """Rock Paper Scissors choices."""
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class RPSGameState(GameState):
    """Rock Paper Scissors specific game state."""
    round_number: int = 1
    moves_this_round: Dict[str, str] = {}
    scores: Dict[str, int] = {}
    total_rounds: int = 1


class RockPaperScissorsGame(BaseGame):
    """
    Rock Paper Scissors game implementation.
    
    Simple, fast game perfect for validating the bot competition platform.
    Features:
    - Best of 1 or multiple rounds
    - Clear winner determination
    - Bot-friendly interface
    """
    
    def __init__(self, game_id: str, players: List[str], total_rounds: int = 1):
        if len(players) != 2:
            raise ValueError("RPS requires exactly 2 players")
        
        self.total_rounds = total_rounds
        self.moves: List[Move] = []
        self.start_time = time.time()
        super().__init__(game_id, players)
    
    def _initialize_state(self) -> RPSGameState:
        """Initialize RPS game state."""
        return RPSGameState(
            game_id=self.game_id,
            players=self.players,
            total_rounds=self.total_rounds,
            scores={player: 0 for player in self.players},
            moves_this_round={},
            round_number=1
        )
    
    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid."""
        # Check if player is in the game
        if move.player not in self.players:
            return False
        
        # Check if player already moved this round
        if move.player in self.state.moves_this_round:
            return False
        
        # Check if game is over
        if self.is_game_over():
            return False
        
        # Check if move is valid RPS choice
        try:
            RPSChoice(move.action.lower())
            return True
        except ValueError:
            return False
    
    def apply_move(self, move: Move) -> RPSGameState:
        """Apply a move and return new game state."""
        if not self.is_valid_move(move):
            raise ValueError(f"Invalid move: {move}")
        
        # Record the move
        self.moves.append(move)
        self.state.moves_this_round[move.player] = move.action.lower()
        
        # Check if round is complete (both players moved)
        if len(self.state.moves_this_round) == 2:
            self._resolve_round()
        
        return self.state
    
    def _resolve_round(self):
        """Resolve the current round and update scores."""
        player1, player2 = self.players
        choice1 = self.state.moves_this_round[player1]
        choice2 = self.state.moves_this_round[player2]
        
        winner = self._determine_round_winner(choice1, choice2)
        
        if winner == player1:
            self.state.scores[player1] += 1
        elif winner == player2:
            self.state.scores[player2] += 1
        # Tie: no score change
        
        # Store round result in metadata
        round_result = {
            "round": self.state.round_number,
            "moves": self.state.moves_this_round.copy(),
            "winner": winner
        }
        
        if "rounds" not in self.state.metadata:
            self.state.metadata["rounds"] = []
        self.state.metadata["rounds"].append(round_result)
        
        # Prepare for next round
        self.state.moves_this_round = {}
        self.state.round_number += 1
    
    def _determine_round_winner(self, choice1: str, choice2: str) -> Optional[str]:
        """Determine winner of a single round."""
        if choice1 == choice2:
            return None  # Tie
        
        wins = {
            "rock": "scissors",
            "paper": "rock", 
            "scissors": "paper"
        }
        
        if wins[choice1] == choice2:
            return self.players[0]
        else:
            return self.players[1]
    
    def get_valid_moves(self, player: str) -> List[str]:
        """Get valid moves for a player."""
        if player not in self.players:
            return []
        
        if self.is_game_over():
            return []
        
        if player in self.state.moves_this_round:
            return []  # Already moved this round
        
        return [choice.value for choice in RPSChoice]
    
    def is_game_over(self) -> bool:
        """Check if the game is finished."""
        # Game is over when we've completed all rounds
        return self.state.round_number > self.total_rounds
    
    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over."""
        if not self.is_game_over():
            return None
        
        player1, player2 = self.players
        score1 = self.state.scores[player1]
        score2 = self.state.scores[player2]
        
        if score1 > score2:
            return player1
        elif score2 > score1:
            return player2
        else:
            return None  # Tie
    
    def get_game_result(self) -> Optional[GameResult]:
        """Get the final game result."""
        if not self.is_game_over():
            return None
        
        return GameResult(
            game_id=self.game_id,
            winner=self.get_winner(),
            players=self.players,
            moves=self.moves,
            duration_seconds=time.time() - self.start_time,
            metadata={
                **self.state.metadata,
                "final_scores": self.state.scores,
                "total_rounds": self.total_rounds
            }
        )