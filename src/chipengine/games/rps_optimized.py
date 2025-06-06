"""
Ultra-optimized Rock Paper Scissors for 1M+ games/second.

Removes all overhead:
- No Pydantic validation
- No deep copying
- Minimal object creation
- Cache-friendly data structures
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class RPSChoice(IntEnum):
    """Integer enum for speed - no string comparisons."""
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


@dataclass
class RPSResult:
    """Minimal result structure."""
    winner: Optional[str]
    player1_choice: int
    player2_choice: int
    duration_ns: int


class OptimizedRPSGame:
    """
    Ultra-fast RPS implementation targeting 1M+ games/second.
    
    Optimizations:
    - No validation (trust input)
    - No object creation during gameplay
    - Integer comparisons only
    - Minimal memory allocation
    """
    
    # Pre-computed winner lookup table for speed
    WINNER_TABLE = {
        (0, 0): None,  # rock vs rock = tie
        (0, 1): 1,     # rock vs paper = player2 wins  
        (0, 2): 0,     # rock vs scissors = player1 wins
        (1, 0): 0,     # paper vs rock = player1 wins
        (1, 1): None,  # paper vs paper = tie
        (1, 2): 1,     # paper vs scissors = player2 wins
        (2, 0): 1,     # scissors vs rock = player2 wins
        (2, 1): 0,     # scissors vs paper = player1 wins
        (2, 2): None,  # scissors vs scissors = tie
    }
    
    CHOICE_NAMES = ["rock", "paper", "scissors"]
    
    def __init__(self, player1: str, player2: str):
        self.player1 = player1
        self.player2 = player2
    
    def play_game(self, choice1: int, choice2: int) -> RPSResult:
        """Play a complete game with integer choices."""
        start = time.time_ns()
        
        winner_index = self.WINNER_TABLE[(choice1, choice2)]
        winner = None if winner_index is None else (
            self.player1 if winner_index == 0 else self.player2
        )
        
        duration = time.time_ns() - start
        
        return RPSResult(
            winner=winner,
            player1_choice=choice1,
            player2_choice=choice2,
            duration_ns=duration
        )
    
    def play_game_string(self, choice1: str, choice2: str) -> RPSResult:
        """Play with string choices (slower but compatible)."""
        choice_map = {"rock": 0, "paper": 1, "scissors": 2}
        return self.play_game(choice_map[choice1], choice_map[choice2])


class BatchRPSProcessor:
    """
    Process thousands of RPS games in batches for maximum throughput.
    
    Uses vectorized operations and minimal overhead.
    """
    
    def __init__(self):
        self.winner_table = OptimizedRPSGame.WINNER_TABLE
    
    def process_batch(self, choices1: List[int], choices2: List[int]) -> List[Optional[int]]:
        """Process a batch of games, return winner indices."""
        return [
            self.winner_table[(c1, c2)]
            for c1, c2 in zip(choices1, choices2)
        ]
    
    def process_batch_with_timing(self, choices1: List[int], choices2: List[int]) -> Tuple[List[Optional[int]], float]:
        """Process batch and return results + total time."""
        start = time.time()
        results = self.process_batch(choices1, choices2)
        duration = time.time() - start
        return results, duration


def benchmark_optimized():
    """Benchmark the optimized implementation."""
    print("🚀 Optimized RPS Benchmarks")
    print("-" * 40)
    
    # Test single game speed
    game = OptimizedRPSGame("Alice", "Bob")
    
    iterations = 1000000
    start = time.time()
    
    for i in range(iterations):
        choice1 = i % 3
        choice2 = (i + 1) % 3
        result = game.play_game(choice1, choice2)
    
    duration = time.time() - start
    rate = iterations / duration
    
    print(f"Single game rate: {rate:.0f} games/second")
    print(f"Time per game: {duration/iterations*1000000:.1f}μs")
    
    # Test batch processing
    batch_processor = BatchRPSProcessor()
    batch_size = 100000
    
    choices1 = [i % 3 for i in range(batch_size)]
    choices2 = [(i + 1) % 3 for i in range(batch_size)]
    
    # Warm up
    batch_processor.process_batch(choices1[:1000], choices2[:1000])
    
    start = time.time()
    results, _ = batch_processor.process_batch_with_timing(choices1, choices2)
    duration = time.time() - start
    
    batch_rate = batch_size / duration
    print(f"Batch processing rate: {batch_rate:.0f} games/second")
    print(f"Time per game: {duration/batch_size*1000000:.1f}μs")
    
    return rate, batch_rate


if __name__ == "__main__":
    single_rate, batch_rate = benchmark_optimized()
    
    print(f"\n🎯 Results:")
    print(f"Single game: {single_rate:.0f} games/sec")
    print(f"Batch mode: {batch_rate:.0f} games/sec")
    print(f"Target: 1,000,000 games/sec")
    
    if batch_rate >= 1000000:
        print("✅ TARGET ACHIEVED!")
    else:
        print(f"❌ Need {1000000/batch_rate:.1f}x improvement")