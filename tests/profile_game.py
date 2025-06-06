"""
Profile the RPS game to find bottlenecks for 1M games/second optimization.
"""

import cProfile
import pstats
import time
import sys
sys.path.insert(0, 'src')

from chipengine.games.rps import RockPaperScissorsGame
from chipengine.core.base_game import Move


def profile_single_game():
    """Profile a single game to see where time is spent."""
    def run_game():
        game = RockPaperScissorsGame("test", ["Alice", "Bob"])
        game.apply_move(Move(player="Alice", action="rock"))
        game.apply_move(Move(player="Bob", action="scissors"))
        return game.get_winner()
    
    # Profile it
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run 10000 games to get meaningful data
    for i in range(10000):
        run_game()
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    print("🔍 Profiling 10,000 games:")
    stats.print_stats(20)  # Top 20 functions
    
    return stats


def benchmark_game_creation():
    """Benchmark just game creation speed."""
    iterations = 100000
    
    start = time.time()
    for i in range(iterations):
        game = RockPaperScissorsGame(f"test-{i}", ["Alice", "Bob"])
    end = time.time()
    
    rate = iterations / (end - start)
    print(f"🚀 Game creation rate: {rate:.0f} games/second")
    print(f"   Time per game: {(end-start)/iterations*1000:.3f}ms")


def benchmark_move_processing():
    """Benchmark move processing speed."""
    game = RockPaperScissorsGame("test", ["Alice", "Bob"])
    
    iterations = 100000
    moves = [
        Move(player="Alice", action="rock"),
        Move(player="Bob", action="scissors")
    ]
    
    start = time.time()
    for i in range(iterations):
        # Reset game state manually for speed
        game.state.moves_this_round = {}
        game.state.game_over = False
        game.state.winner = None
        game.state.round_number = 1
        
        for move in moves:
            game.apply_move(move)
    end = time.time()
    
    rate = iterations / (end - start)
    print(f"⚡ Move processing rate: {rate:.0f} complete games/second")
    print(f"   Time per game: {(end-start)/iterations*1000:.3f}ms")


def benchmark_minimal_rps():
    """Benchmark the absolute minimal RPS logic."""
    
    def minimal_rps_game(choice1: str, choice2: str) -> str:
        """Ultra-minimal RPS logic."""
        if choice1 == choice2:
            return "tie"
        
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        return "player1" if wins[choice1] == choice2 else "player2"
    
    iterations = 1000000
    choices = ["rock", "paper", "scissors"]
    
    start = time.time()
    for i in range(iterations):
        choice1 = choices[i % 3]
        choice2 = choices[(i + 1) % 3]
        result = minimal_rps_game(choice1, choice2)
    end = time.time()
    
    rate = iterations / (end - start)
    print(f"🔥 Minimal RPS logic rate: {rate:.0f} games/second")
    print(f"   Time per game: {(end-start)/iterations*1000000:.1f}μs")


if __name__ == "__main__":
    print("ChipEngine Performance Analysis")
    print("=" * 50)
    
    print("\n1. Minimal RPS Logic Speed:")
    benchmark_minimal_rps()
    
    print("\n2. Game Creation Speed:")
    benchmark_game_creation()
    
    print("\n3. Move Processing Speed:")
    benchmark_move_processing()
    
    print("\n4. Detailed Profiling:")
    profile_single_game()
    
    print("\n🎯 Target: 1,000,000 games/second")
    print("💡 Each game must complete in <1 microsecond!")