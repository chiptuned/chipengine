"""
Load testing for ChipEngine RPS implementation.

Tests game creation and completion at increasing rates:
- 10 games/second
- 100 games/second  
- 1000 games/second
- Until it breaks
"""

import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys
sys.path.insert(0, 'src')

from chipengine.api.game_manager import game_manager
from chipengine.core.base_game import Move


class LoadTester:
    def __init__(self):
        self.results = []
        self.errors = []
    
    def create_and_play_game(self, game_id_suffix: int) -> dict:
        """Create a game, play it to completion, return timing data."""
        start_time = time.time()
        
        try:
            # Create game
            game_id = game_manager.create_game(
                'rps', 
                [f'Player{game_id_suffix}', f'Bot{game_id_suffix}']
            )
            
            creation_time = time.time()
            
            # Play game (both players make moves)
            game_manager.make_move(game_id, f'Player{game_id_suffix}', 'rock')
            move1_time = time.time()
            
            game_manager.make_move(game_id, f'Bot{game_id_suffix}', 'scissors')
            move2_time = time.time()
            
            # Get final state
            final_state = game_manager.get_game_state(game_id)
            end_time = time.time()
            
            return {
                'success': True,
                'game_id': game_id,
                'total_time': end_time - start_time,
                'creation_time': creation_time - start_time,
                'move1_time': move1_time - creation_time,
                'move2_time': move2_time - move1_time,
                'final_check_time': end_time - move2_time,
                'game_over': final_state['game_over'],
                'winner': final_state['winner']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_time': time.time() - start_time
            }
    
    def run_concurrent_games(self, games_per_second: int, duration_seconds: int = 10):
        """Run games at specified rate for given duration."""
        print(f"\n🎯 Testing {games_per_second} games/second for {duration_seconds} seconds...")
        
        target_games = games_per_second * duration_seconds
        interval = 1.0 / games_per_second
        
        with ThreadPoolExecutor(max_workers=min(200, games_per_second * 2)) as executor:
            futures = []
            start_time = time.time()
            
            for i in range(target_games):
                # Submit game creation
                future = executor.submit(self.create_and_play_game, i)
                futures.append(future)
                
                # Control rate
                expected_time = start_time + (i * interval)
                sleep_time = expected_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Collect results
            test_results = []
            for future in futures:
                try:
                    result = future.result(timeout=5.0)
                    test_results.append(result)
                except Exception as e:
                    test_results.append({
                        'success': False,
                        'error': f'Future error: {str(e)}',
                        'total_time': 0
                    })
            
            actual_duration = time.time() - start_time
            
        return self.analyze_results(test_results, games_per_second, actual_duration)
    
    def analyze_results(self, results: list, target_rate: int, actual_duration: float):
        """Analyze test results and return summary."""
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        if successful:
            times = [r['total_time'] for r in successful]
            avg_time = statistics.mean(times)
            p95_time = statistics.quantiles(times, n=20)[18] if len(times) > 5 else max(times)
            p99_time = statistics.quantiles(times, n=100)[98] if len(times) > 10 else max(times)
        else:
            avg_time = p95_time = p99_time = 0
        
        actual_rate = len(results) / actual_duration if actual_duration > 0 else 0
        success_rate = len(successful) / len(results) if results else 0
        
        summary = {
            'target_rate': target_rate,
            'actual_rate': actual_rate,
            'duration': actual_duration,
            'total_games': len(results),
            'successful_games': len(successful),
            'failed_games': len(failed),
            'success_rate': success_rate,
            'avg_game_time': avg_time,
            'p95_game_time': p95_time,
            'p99_game_time': p99_time,
            'errors': [r.get('error', 'Unknown') for r in failed[:5]]  # First 5 errors
        }
        
        # Print results
        print(f"📊 Results for {target_rate} games/second:")
        print(f"   Actual rate: {actual_rate:.1f} games/second")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   Total games: {len(results)} ({len(successful)} success, {len(failed)} failed)")
        print(f"   Avg game time: {avg_time*1000:.1f}ms")
        print(f"   P95 game time: {p95_time*1000:.1f}ms")
        print(f"   P99 game time: {p99_time*1000:.1f}ms")
        
        if failed:
            print(f"   First few errors: {summary['errors'][:3]}")
        
        return summary
    
    def ramp_test(self):
        """Run ramping load test until failure."""
        print("🚀 Starting ramping load test...")
        print("Testing RPS game creation and completion rates")
        
        rates = [10, 100, 1000, 10000]  # games per second
        all_results = []
        
        for rate in rates:
            try:
                # Clean up games before each test
                game_manager.cleanup_finished_games()
                
                result = self.run_concurrent_games(rate, duration_seconds=5)
                all_results.append(result)
                
                # Stop if success rate drops below 90%
                if result['success_rate'] < 0.9:
                    print(f"❌ Breaking at {rate} games/second due to {result['success_rate']:.1%} success rate")
                    break
                    
                # Stop if actual rate is significantly lower than target
                if result['actual_rate'] < rate * 0.8:
                    print(f"❌ Breaking at {rate} games/second due to rate limiting")
                    break
                    
                print(f"✅ {rate} games/second: SUCCESS")
                
            except KeyboardInterrupt:
                print("❌ Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ Test failed at {rate} games/second: {e}")
                break
        
        print("\n📈 LOAD TEST SUMMARY:")
        print("-" * 50)
        for result in all_results:
            status = "✅" if result['success_rate'] > 0.9 else "❌"
            print(f"{status} {result['target_rate']:5d} games/sec: "
                  f"{result['actual_rate']:6.1f} actual, "
                  f"{result['success_rate']:5.1%} success, "
                  f"{result['avg_game_time']*1000:5.1f}ms avg")
        
        if all_results:
            max_successful_rate = max(
                r['actual_rate'] for r in all_results 
                if r['success_rate'] > 0.9
            )
            print(f"\n🏆 Maximum sustainable rate: {max_successful_rate:.0f} games/second")
        
        return all_results


if __name__ == "__main__":
    print("ChipEngine Load Testing")
    print("=" * 50)
    
    tester = LoadTester()
    results = tester.ramp_test()
    
    print(f"\n📊 Active games in memory: {len(game_manager.active_games)}")
    cleanup_count = game_manager.cleanup_finished_games()
    print(f"🗑️  Cleaned up {cleanup_count} finished games")
    print(f"📊 Active games after cleanup: {len(game_manager.active_games)}")