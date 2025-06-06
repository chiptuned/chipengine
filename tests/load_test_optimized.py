"""
Load testing for optimized ChipEngine targeting 1M+ games/second.

Includes detailed logging and multiple optimization strategies.
"""

import asyncio
import time
import statistics
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import asdict
import sys
sys.path.insert(0, 'src')

from chipengine.games.rps_optimized import OptimizedRPSGame, BatchRPSProcessor


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HighPerformanceLoadTester:
    """Load tester optimized for 1M+ games/second."""
    
    def __init__(self):
        self.results = []
        
    def single_threaded_test(self, games_per_second: int, duration_seconds: int = 5):
        """Single-threaded test using optimized game."""
        logger.info(f"🔥 Single-threaded test: {games_per_second} games/sec for {duration_seconds}s")
        
        game = OptimizedRPSGame("Player", "Bot")
        target_games = games_per_second * duration_seconds
        
        results = []
        start_time = time.time()
        
        for i in range(target_games):
            choice1 = i % 3
            choice2 = (i + 1) % 3
            result = game.play_game(choice1, choice2)
            results.append(result)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        actual_rate = len(results) / actual_duration
        
        avg_game_time = sum(r.duration_ns for r in results) / len(results) / 1000  # μs
        
        test_result = {
            'method': 'single_threaded',
            'target_rate': games_per_second,
            'actual_rate': actual_rate,
            'duration': actual_duration,
            'total_games': len(results),
            'success_rate': 1.0,
            'avg_game_time_us': avg_game_time,
            'games_completed': target_games
        }
        
        logger.info(f"   Actual rate: {actual_rate:.0f} games/sec")
        logger.info(f"   Avg game time: {avg_game_time:.3f}μs")
        
        return test_result
    
    def batch_test(self, games_per_second: int, duration_seconds: int = 5):
        """Batch processing test for maximum throughput."""
        logger.info(f"⚡ Batch test: {games_per_second} games/sec for {duration_seconds}s")
        
        processor = BatchRPSProcessor()
        target_games = games_per_second * duration_seconds
        batch_size = min(100000, target_games)  # Process in chunks
        
        total_games = 0
        start_time = time.time()
        
        while total_games < target_games:
            remaining = min(batch_size, target_games - total_games)
            
            choices1 = [i % 3 for i in range(remaining)]
            choices2 = [(i + 1) % 3 for i in range(remaining)]
            
            batch_results, batch_duration = processor.process_batch_with_timing(choices1, choices2)
            total_games += len(batch_results)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        actual_rate = total_games / actual_duration
        
        test_result = {
            'method': 'batch',
            'target_rate': games_per_second,
            'actual_rate': actual_rate,
            'duration': actual_duration,
            'total_games': total_games,
            'success_rate': 1.0,
            'avg_game_time_us': 0.0,  # Batch mode doesn't track individual times
            'games_completed': total_games
        }
        
        logger.info(f"   Actual rate: {actual_rate:.0f} games/sec")
        logger.info(f"   Batch efficiency: {actual_rate/games_per_second:.2f}x")
        
        return test_result
    
    def multiprocessing_test(self, games_per_second: int, duration_seconds: int = 5):
        """Multi-process test for CPU-bound parallelization."""
        logger.info(f"🚀 Multi-process test: {games_per_second} games/sec for {duration_seconds}s")
        
        target_games = games_per_second * duration_seconds
        num_processes = min(os.cpu_count(), 8)  # Don't overload
        games_per_process = target_games // num_processes
        
        def worker_process(process_id: int, games_count: int):
            """Worker function for each process."""
            game = OptimizedRPSGame(f"Player{process_id}", f"Bot{process_id}")
            results = []
            
            for i in range(games_count):
                choice1 = i % 3
                choice2 = (i + 1) % 3
                result = game.play_game(choice1, choice2)
                results.append(result)
            
            return len(results)
        
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for process_id in range(num_processes):
                future = executor.submit(worker_process, process_id, games_per_process)
                futures.append(future)
            
            total_games = sum(future.result() for future in futures)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        actual_rate = total_games / actual_duration
        
        test_result = {
            'method': 'multiprocessing',
            'target_rate': games_per_second,
            'actual_rate': actual_rate,
            'duration': actual_duration,
            'total_games': total_games,
            'success_rate': 1.0,
            'num_processes': num_processes,
            'games_per_process': games_per_process,
            'games_completed': total_games
        }
        
        logger.info(f"   Processes: {num_processes}")
        logger.info(f"   Actual rate: {actual_rate:.0f} games/sec")
        logger.info(f"   Efficiency: {actual_rate/games_per_second:.2f}x")
        
        return test_result
    
    def comprehensive_ramp_test(self):
        """Comprehensive ramping test with multiple strategies."""
        logger.info("🎯 Starting comprehensive 1M+ games/sec test")
        
        # Test rates from 1K to 10M games/second
        test_rates = [1000, 10000, 100000, 1000000, 5000000, 10000000]
        all_results = []
        
        for rate in test_rates:
            logger.info(f"\n📊 Testing {rate:,} games/second")
            
            # Test multiple methods for each rate
            methods = [
                ('single_threaded', self.single_threaded_test),
                ('batch', self.batch_test),
                ('multiprocessing', self.multiprocessing_test)
            ]
            
            for method_name, method_func in methods:
                try:
                    # Adjust duration based on rate (don't run 10M games for 5 seconds!)
                    duration = max(1, min(5, 100000 // rate))
                    
                    result = method_func(rate, duration)
                    result['timestamp'] = time.time()
                    all_results.append(result)
                    
                    # Log to file
                    self.log_result(result)
                    
                    # Check if we achieved target
                    efficiency = result['actual_rate'] / rate
                    if efficiency >= 0.9:
                        logger.info(f"   ✅ {method_name}: {efficiency:.1%} efficiency")
                    else:
                        logger.info(f"   ❌ {method_name}: {efficiency:.1%} efficiency")
                        
                except Exception as e:
                    logger.error(f"   ❌ {method_name} failed: {e}")
        
        self.analyze_and_report(all_results)
        return all_results
    
    def log_result(self, result):
        """Log detailed result to file."""
        with open('load_test_results.jsonl', 'a') as f:
            f.write(json.dumps(result) + '\n')
    
    def analyze_and_report(self, results):
        """Analyze all results and create final report."""
        logger.info("\n" + "="*60)
        logger.info("📈 COMPREHENSIVE LOAD TEST RESULTS")
        logger.info("="*60)
        
        # Group by method
        by_method = {}
        for result in results:
            method = result['method']
            if method not in by_method:
                by_method[method] = []
            by_method[method].append(result)
        
        # Find best performance for each method
        for method, method_results in by_method.items():
            best = max(method_results, key=lambda r: r['actual_rate'])
            logger.info(f"\n🏆 {method.upper()}:")
            logger.info(f"   Max rate: {best['actual_rate']:,.0f} games/sec")
            logger.info(f"   Target: {best['target_rate']:,} games/sec")
            logger.info(f"   Efficiency: {best['actual_rate']/best['target_rate']:.1%}")
            
            if 'num_processes' in best:
                logger.info(f"   Processes: {best['num_processes']}")
        
        # Overall best
        overall_best = max(results, key=lambda r: r['actual_rate'])
        logger.info(f"\n🎯 OVERALL BEST PERFORMANCE:")
        logger.info(f"   Method: {overall_best['method']}")
        logger.info(f"   Rate: {overall_best['actual_rate']:,.0f} games/second")
        logger.info(f"   Target: 1,000,000 games/second")
        
        if overall_best['actual_rate'] >= 1000000:
            logger.info("   ✅ TARGET ACHIEVED!")
        else:
            needed = 1000000 / overall_best['actual_rate']
            logger.info(f"   ❌ Need {needed:.1f}x improvement")
        
        logger.info(f"\n📊 Results logged to: load_test_results.jsonl")


if __name__ == "__main__":
    # Clear previous results
    for file in ['load_test.log', 'load_test_results.jsonl']:
        if os.path.exists(file):
            os.remove(file)
    
    logger.info("ChipEngine High-Performance Load Testing")
    logger.info("Target: 1,000,000+ games per second")
    
    tester = HighPerformanceLoadTester()
    results = tester.comprehensive_ramp_test()
    
    logger.info(f"\n🏁 Testing complete. Check load_test.log for details.")