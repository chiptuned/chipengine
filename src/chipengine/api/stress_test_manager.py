"""
Stress Test Manager for ChipEngine.

Handles high-performance stress testing with real-time monitoring.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import threading
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from .models import StressTestRequest, StressTestStatus
from .game_manager import game_manager


@dataclass
class StressTestMetrics:
    """Metrics for a running stress test."""
    test_id: str
    status: str = "running"
    started_at: float = field(default_factory=time.time)
    games_created: int = 0
    games_completed: int = 0
    games_failed: int = 0
    current_rps: float = 0.0
    peak_rps: float = 0.0
    avg_game_duration: float = 0.0
    errors: List[str] = field(default_factory=list)
    config: StressTestRequest = None
    
    def to_status(self) -> StressTestStatus:
        """Convert to API status model."""
        return StressTestStatus(
            test_id=self.test_id,
            status=self.status,
            started_at=datetime.fromtimestamp(self.started_at).isoformat(),
            elapsed_seconds=time.time() - self.started_at,
            games_created=self.games_created,
            games_completed=self.games_completed,
            games_failed=self.games_failed,
            current_rps=self.current_rps,
            peak_rps=self.peak_rps,
            avg_game_duration=self.avg_game_duration,
            errors=self.errors[-10:],  # Last 10 errors
            config=self.config
        )


class StressTestManager:
    """
    High-performance stress test manager.
    
    Manages concurrent game creation and execution with real-time monitoring.
    """
    
    def __init__(self):
        self.active_tests: Dict[str, StressTestMetrics] = {}
        self.test_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=100)  # Limit concurrent game simulations
    
    def start_stress_test(self, config: StressTestRequest) -> str:
        """Start a new stress test."""
        test_id = str(uuid.uuid4())
        
        metrics = StressTestMetrics(
            test_id=test_id,
            config=config
        )
        
        with self._lock:
            self.active_tests[test_id] = metrics
        
        # Start test in background thread
        thread = threading.Thread(
            target=self._run_stress_test,
            args=(test_id, config),
            daemon=True
        )
        thread.start()
        self.test_threads[test_id] = thread
        
        return test_id
    
    def get_test_status(self, test_id: str) -> Optional[StressTestStatus]:
        """Get current status of a stress test."""
        with self._lock:
            metrics = self.active_tests.get(test_id)
            if not metrics:
                return None
            return metrics.to_status()
    
    def stop_stress_test(self, test_id: str) -> bool:
        """Stop a running stress test."""
        with self._lock:
            if test_id in self.active_tests:
                self.active_tests[test_id].status = "stopped"
                return True
            return False
    
    def list_active_tests(self) -> List[StressTestStatus]:
        """Get all active stress tests."""
        with self._lock:
            return [metrics.to_status() for metrics in self.active_tests.values()]
    
    def _run_stress_test(self, test_id: str, config: StressTestRequest):
        """Run the actual stress test."""
        metrics = self.active_tests[test_id]
        
        try:
            start_time = time.time()
            last_rps_check = start_time
            games_at_last_check = 0
            
            # Calculate total games if not specified
            total_games = config.total_games or (config.games_per_second * config.duration_seconds)
            
            # Game creation timing
            target_interval = 1.0 / config.games_per_second
            
            while (metrics.status == "running" and 
                   metrics.games_created < total_games and
                   (time.time() - start_time) < config.duration_seconds):
                
                batch_start = time.time()
                
                # Create games in batches to maintain target RPS
                batch_size = min(10, total_games - metrics.games_created)
                
                for _ in range(batch_size):
                    if metrics.status != "running":
                        break
                    
                    try:
                        # Create game
                        game_id = game_manager.create_game(
                            game_type=config.game_type,
                            players=[f"Player_{metrics.games_created}", "Bot"],
                            config={"total_rounds": 1}
                        )
                        metrics.games_created += 1
                        
                        # Simulate game play asynchronously
                        self._simulate_game_async(game_id, metrics)
                        
                    except Exception as e:
                        metrics.games_failed += 1
                        if len(metrics.errors) < 100:  # Limit error storage
                            metrics.errors.append(f"Game creation failed: {str(e)}")
                
                # Calculate current RPS
                current_time = time.time()
                if current_time - last_rps_check >= 1.0:
                    games_this_period = metrics.games_created - games_at_last_check
                    time_period = current_time - last_rps_check
                    metrics.current_rps = games_this_period / time_period
                    metrics.peak_rps = max(metrics.peak_rps, metrics.current_rps)
                    
                    last_rps_check = current_time
                    games_at_last_check = metrics.games_created
                
                # Sleep to maintain target RPS
                elapsed = time.time() - batch_start
                target_duration = target_interval * batch_size
                if elapsed < target_duration:
                    time.sleep(target_duration - elapsed)
            
            metrics.status = "completed"
            
        except Exception as e:
            metrics.status = "failed"
            metrics.errors.append(f"Test failed: {str(e)}")
        
        # Cleanup
        if test_id in self.test_threads:
            del self.test_threads[test_id]
        
        # Auto-cleanup completed tests after 5 minutes
        self._schedule_cleanup(test_id, 300)
    
    def _simulate_game_async(self, game_id: str, metrics: StressTestMetrics):
        """Simulate a game asynchronously."""
        def simulate():
            try:
                game_start = time.time()
                
                # Make moves for both players
                game_manager.make_move(game_id, f"Player_{metrics.games_created}", "rock")
                game_manager.make_move(game_id, "Bot", "paper")
                
                # Update metrics
                game_duration = time.time() - game_start
                total_duration = metrics.avg_game_duration * metrics.games_completed + game_duration
                metrics.games_completed += 1
                metrics.avg_game_duration = total_duration / metrics.games_completed
                
                # Clean up game
                if game_id in game_manager.active_games:
                    del game_manager.active_games[game_id]
                    
            except Exception as e:
                metrics.games_failed += 1
                if len(metrics.errors) < 100:
                    metrics.errors.append(f"Game simulation failed: {str(e)}")
        
        # Run in thread pool to limit concurrent simulations
        self._executor.submit(simulate)
    
    def _schedule_cleanup(self, test_id: str, delay_seconds: int):
        """Schedule cleanup of completed test after delay."""
        def cleanup():
            time.sleep(delay_seconds)
            with self._lock:
                if test_id in self.active_tests and self.active_tests[test_id].status in ["completed", "failed", "stopped"]:
                    del self.active_tests[test_id]
        
        threading.Thread(target=cleanup, daemon=True).start()


# Global stress test manager instance
stress_test_manager = StressTestManager()