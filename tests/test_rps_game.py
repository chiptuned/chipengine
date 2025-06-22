"""
Test Rock Paper Scissors game implementation.
"""

import pytest
from chipengine.games.rps import RockPaperScissorsGame
from chipengine.core.base_game import Move


class TestRPSGame:
    """Test RPS game functionality."""
    
    def test_game_creation(self):
        """Test creating a new RPS game."""
        game = RockPaperScissorsGame("test-1", ["Alice", "Bob"])
        
        assert game.game_id == "test-1"
        assert game.players == ["Alice", "Bob"]
        assert not game.is_game_over()
        assert game.get_winner() is None
    
    def test_valid_moves(self):
        """Test valid move checking."""
        game = RockPaperScissorsGame("test-2", ["Alice", "Bob"])
        
        # Valid moves
        assert game.is_valid_move(Move(player="Alice", action="rock"))
        assert game.is_valid_move(Move(player="Bob", action="paper"))
        assert game.is_valid_move(Move(player="Alice", action="scissors"))
        
        # Invalid moves
        assert not game.is_valid_move(Move(player="Charlie", action="rock"))  # Not a player
        assert not game.is_valid_move(Move(player="Alice", action="invalid"))  # Invalid choice
    
    def test_complete_game(self):
        """Test a complete game flow."""
        game = RockPaperScissorsGame("test-3", ["Alice", "Bob"])
        
        # Alice plays rock
        move1 = Move(player="Alice", action="rock")
        game.apply_move(move1)
        assert not game.is_game_over()
        
        # Bob plays scissors
        move2 = Move(player="Bob", action="scissors")
        game.apply_move(move2)
        
        # Game should be over now
        assert game.is_game_over()
        assert game.get_winner() == "Alice"  # Rock beats scissors
        
        # Check game result
        result = game.get_game_result()
        assert result is not None
        assert result.winner == "Alice"
        assert len(result.moves) == 2
    
    def test_tie_game(self):
        """Test a tie game."""
        game = RockPaperScissorsGame("test-4", ["Alice", "Bob"])
        
        # Both play rock
        game.apply_move(Move(player="Alice", action="rock"))
        game.apply_move(Move(player="Bob", action="rock"))
        
        assert game.is_game_over()
        assert game.get_winner() is None  # Tie
    
    def test_multiple_rounds(self):
        """Test multiple round game."""
        game = RockPaperScissorsGame("test-5", ["Alice", "Bob"], total_rounds=3)
        
        # Round 1: Alice wins
        game.apply_move(Move(player="Alice", action="rock"))
        game.apply_move(Move(player="Bob", action="scissors"))
        assert not game.is_game_over()  # Still have more rounds
        
        # Round 2: Bob wins  
        game.apply_move(Move(player="Alice", action="scissors"))
        game.apply_move(Move(player="Bob", action="rock"))
        assert not game.is_game_over()
        
        # Round 3: Alice wins
        game.apply_move(Move(player="Alice", action="paper"))
        game.apply_move(Move(player="Bob", action="rock"))
        
        assert game.is_game_over()
        assert game.get_winner() == "Alice"  # Alice won 2/3 rounds
    
    def test_get_valid_moves(self):
        """Test getting valid moves for players."""
        game = RockPaperScissorsGame("test-6", ["Alice", "Bob"])
        
        # Both players should have all choices available
        alice_moves = game.get_valid_moves("Alice")
        assert set(alice_moves) == {"rock", "paper", "scissors"}
        
        # After Alice moves, she should have no valid moves
        game.apply_move(Move(player="Alice", action="rock"))
        assert game.get_valid_moves("Alice") == []
        
        # Bob should still have moves available
        bob_moves = game.get_valid_moves("Bob")
        assert set(bob_moves) == {"rock", "paper", "scissors"}


if __name__ == "__main__":
    pytest.main([__file__])