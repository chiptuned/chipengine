"""
Stress Test API routes for ChipEngine.

Provides REST endpoints for:
- Starting stress tests
- Monitoring test progress
- Stopping tests
- Getting test results
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models import (
    StressTestRequest, StressTestResponse, StressTestStatus
)
from ..stress_test_manager import stress_test_manager
from datetime import datetime

router = APIRouter(prefix="/stress-tests", tags=["stress-tests"])


@router.post("/", response_model=StressTestResponse)
async def start_stress_test(request: StressTestRequest):
    """Start a new stress test."""
    try:
        test_id = stress_test_manager.start_stress_test(request)
        
        return StressTestResponse(
            test_id=test_id,
            status="started",
            config=request,
            started_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[StressTestStatus])
async def list_stress_tests():
    """Get all active stress tests."""
    return stress_test_manager.list_active_tests()


@router.get("/{test_id}", response_model=StressTestStatus)
async def get_stress_test_status(test_id: str):
    """Get status of a specific stress test."""
    status = stress_test_manager.get_test_status(test_id)
    if not status:
        raise HTTPException(status_code=404, detail="Stress test not found")
    return status


@router.delete("/{test_id}")
async def stop_stress_test(test_id: str):
    """Stop a running stress test."""
    if not stress_test_manager.stop_stress_test(test_id):
        raise HTTPException(status_code=404, detail="Stress test not found")
    
    return {"message": "Stress test stopped successfully"}


@router.get("/{test_id}/metrics")
async def get_stress_test_metrics(test_id: str):
    """Get detailed metrics for a stress test."""
    status = stress_test_manager.get_test_status(test_id)
    if not status:
        raise HTTPException(status_code=404, detail="Stress test not found")
    
    return {
        "test_id": test_id,
        "performance": {
            "games_per_second": status.current_rps,
            "peak_games_per_second": status.peak_rps,
            "average_game_duration_ms": status.avg_game_duration * 1000,
            "success_rate": (
                status.games_completed / max(status.games_created, 1) * 100
                if status.games_created > 0 else 0
            ),
            "completion_rate": (
                status.games_completed / max(status.config.total_games or 1000, 1) * 100
            )
        },
        "counters": {
            "games_created": status.games_created,
            "games_completed": status.games_completed,
            "games_failed": status.games_failed,
            "total_games_target": status.config.total_games or (
                status.config.games_per_second * status.config.duration_seconds
            )
        },
        "timing": {
            "elapsed_seconds": status.elapsed_seconds,
            "target_duration": status.config.duration_seconds,
            "progress_percentage": min(
                status.elapsed_seconds / status.config.duration_seconds * 100, 100
            )
        },
        "errors": status.errors
    }