"""
Optimized FastAPI server for testing 1M+ games/second performance.

Simple endpoints for frontend testing of the high-performance RPS engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import time
import random
from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from chipengine.games.rps_optimized import OptimizedRPSGame, BatchRPSProcessor

app = FastAPI(title="ChipEngine Optimized API", version="1.0.0")

# Global game processor for maximum performance
batch_processor = BatchRPSProcessor()
game_counter = 0


class PlayGameRequest(BaseModel):
    player1_choice: str  # "rock", "paper", "scissors"
    player2_choice: str


class PlayGameResponse(BaseModel):
    winner: Optional[str]
    player1_choice: str
    player2_choice: str
    game_duration_us: float
    game_id: int


class BatchGameRequest(BaseModel):
    count: int  # Number of games to play
    player1_choices: Optional[List[str]] = None  # If not provided, random
    player2_choices: Optional[List[str]] = None  # If not provided, random


class BatchGameResponse(BaseModel):
    total_games: int
    player1_wins: int
    player2_wins: int
    ties: int
    total_duration_ms: float
    games_per_second: float


class StressTestResponse(BaseModel):
    games_completed: int
    duration_seconds: float
    games_per_second: float
    target_rate: int
    success: bool


@app.get("/", response_class=HTMLResponse)
async def get_test_page():
    """Serve the test webpage."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChipEngine Performance Test</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        .test-section {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
        }
        .choice-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 20px 0;
        }
        .choice-btn {
            padding: 15px 25px;
            font-size: 1.5em;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            transition: all 0.3s;
        }
        .choice-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }
        .choice-btn.selected {
            background: #4CAF50;
        }
        .test-btn {
            padding: 12px 30px;
            font-size: 1.1em;
            border: none;
            border-radius: 8px;
            background: #FF6B6B;
            color: white;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
        }
        .test-btn:hover {
            background: #FF5252;
            transform: translateY(-2px);
        }
        .test-btn:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .results {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .loading {
            text-align: center;
            font-size: 1.2em;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .performance-chart {
            margin: 20px 0;
            text-align: center;
        }
        input[type="number"] {
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            width: 100px;
            text-align: center;
        }
        input[type="number"]::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 ChipEngine Performance Test</h1>
        <p class="subtitle">Testing 1M+ games/second RPS engine</p>
        
        <!-- Single Game Test -->
        <div class="test-section">
            <h2>🎯 Single Game Test</h2>
            <p>Play Rock Paper Scissors against the optimized engine</p>
            
            <div class="choice-buttons">
                <button class="choice-btn" onclick="selectChoice('rock')">🪨 Rock</button>
                <button class="choice-btn" onclick="selectChoice('paper')">📄 Paper</button>
                <button class="choice-btn" onclick="selectChoice('scissors')">✂️ Scissors</button>
            </div>
            
            <div style="text-align: center;">
                <button class="test-btn" onclick="playSingleGame()" id="playBtn" disabled>Play Game</button>
            </div>
            
            <div id="singleGameResult" class="results" style="display: none;"></div>
        </div>
        
        <!-- Batch Test -->
        <div class="test-section">
            <h2>⚡ Batch Performance Test</h2>
            <p>Test batch processing performance</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <label>Number of games: </label>
                <input type="number" id="batchCount" value="10000" min="1" max="1000000">
                <button class="test-btn" onclick="runBatchTest()">Run Batch Test</button>
            </div>
            
            <div id="batchResult" class="results" style="display: none;"></div>
        </div>
        
        <!-- Stress Test -->
        <div class="test-section">
            <h2>🔥 Stress Test</h2>
            <p>Push the engine to its limits</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="test-btn" onclick="runStressTest(1000)">1K games/sec</button>
                <button class="test-btn" onclick="runStressTest(10000)">10K games/sec</button>
                <button class="test-btn" onclick="runStressTest(100000)">100K games/sec</button>
                <button class="test-btn" onclick="runStressTest(1000000)">1M games/sec</button>
            </div>
            
            <div id="stressResult" class="results" style="display: none;"></div>
        </div>
    </div>

    <script>
        let selectedChoice = null;
        
        function selectChoice(choice) {
            selectedChoice = choice;
            
            // Update button styles
            document.querySelectorAll('.choice-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            event.target.classList.add('selected');
            
            // Enable play button
            document.getElementById('playBtn').disabled = false;
        }
        
        async function playSingleGame() {
            if (!selectedChoice) return;
            
            const botChoice = ['rock', 'paper', 'scissors'][Math.floor(Math.random() * 3)];
            
            try {
                const response = await fetch('/play', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        player1_choice: selectedChoice,
                        player2_choice: botChoice
                    })
                });
                
                const result = await response.json();
                
                document.getElementById('singleGameResult').innerHTML = `
                    <h3>Game Result</h3>
                    <div class="metric"><span>Your choice:</span><span>${result.player1_choice} ${getEmoji(result.player1_choice)}</span></div>
                    <div class="metric"><span>Bot choice:</span><span>${result.player2_choice} ${getEmoji(result.player2_choice)}</span></div>
                    <div class="metric"><span>Winner:</span><span>${result.winner || 'Tie!'}</span></div>
                    <div class="metric"><span>Game duration:</span><span>${result.game_duration_us.toFixed(3)}μs</span></div>
                    <div class="metric"><span>Game ID:</span><span>#${result.game_id}</span></div>
                `;
                document.getElementById('singleGameResult').style.display = 'block';
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        async function runBatchTest() {
            const count = parseInt(document.getElementById('batchCount').value);
            
            document.getElementById('batchResult').innerHTML = '<div class="loading">Running batch test...</div>';
            document.getElementById('batchResult').style.display = 'block';
            
            try {
                const response = await fetch('/batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ count: count })
                });
                
                const result = await response.json();
                
                document.getElementById('batchResult').innerHTML = `
                    <h3>Batch Test Results</h3>
                    <div class="metric"><span>Total games:</span><span>${result.total_games.toLocaleString()}</span></div>
                    <div class="metric"><span>Player 1 wins:</span><span>${result.player1_wins.toLocaleString()}</span></div>
                    <div class="metric"><span>Player 2 wins:</span><span>${result.player2_wins.toLocaleString()}</span></div>
                    <div class="metric"><span>Ties:</span><span>${result.ties.toLocaleString()}</span></div>
                    <div class="metric"><span>Duration:</span><span>${result.total_duration_ms.toFixed(2)}ms</span></div>
                    <div class="metric"><span>Games/second:</span><span><strong>${result.games_per_second.toLocaleString()}</strong></span></div>
                `;
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('batchResult').innerHTML = '<div>Error running batch test</div>';
            }
        }
        
        async function runStressTest(targetRate) {
            document.getElementById('stressResult').innerHTML = '<div class="loading">Running stress test...</div>';
            document.getElementById('stressResult').style.display = 'block';
            
            try {
                const response = await fetch(`/stress/${targetRate}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                const success = result.success ? '✅' : '❌';
                const efficiency = ((result.games_per_second / targetRate) * 100).toFixed(1);
                
                document.getElementById('stressResult').innerHTML = `
                    <h3>Stress Test Results ${success}</h3>
                    <div class="metric"><span>Target rate:</span><span>${targetRate.toLocaleString()} games/sec</span></div>
                    <div class="metric"><span>Actual rate:</span><span><strong>${result.games_per_second.toLocaleString()} games/sec</strong></span></div>
                    <div class="metric"><span>Games completed:</span><span>${result.games_completed.toLocaleString()}</span></div>
                    <div class="metric"><span>Duration:</span><span>${result.duration_seconds.toFixed(2)}s</span></div>
                    <div class="metric"><span>Efficiency:</span><span>${efficiency}%</span></div>
                `;
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('stressResult').innerHTML = '<div>Error running stress test</div>';
            }
        }
        
        function getEmoji(choice) {
            const emojis = { rock: '🪨', paper: '📄', scissors: '✂️' };
            return emojis[choice] || '❓';
        }
    </script>
</body>
</html>"""


@app.post("/play", response_model=PlayGameResponse)
async def play_single_game(request: PlayGameRequest):
    """Play a single optimized game."""
    global game_counter
    game_counter += 1
    
    game = OptimizedRPSGame("Player1", "Player2")
    
    choice_map = {"rock": 0, "paper": 1, "scissors": 2}
    choice1 = choice_map.get(request.player1_choice.lower())
    choice2 = choice_map.get(request.player2_choice.lower())
    
    if choice1 is None or choice2 is None:
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    result = game.play_game(choice1, choice2)
    
    return PlayGameResponse(
        winner=result.winner,
        player1_choice=request.player1_choice,
        player2_choice=request.player2_choice,
        game_duration_us=result.duration_ns / 1000,  # Convert to microseconds
        game_id=game_counter
    )


@app.post("/batch", response_model=BatchGameResponse)
async def play_batch_games(request: BatchGameRequest):
    """Play multiple games in batch for performance testing."""
    start_time = time.time()
    
    # Generate random choices if not provided
    choices = ["rock", "paper", "scissors"]
    if not request.player1_choices:
        player1_choices = [random.choice(choices) for _ in range(request.count)]
    else:
        player1_choices = request.player1_choices[:request.count]
    
    if not request.player2_choices:
        player2_choices = [random.choice(choices) for _ in range(request.count)]
    else:
        player2_choices = request.player2_choices[:request.count]
    
    # Convert to integers for batch processing
    choice_map = {"rock": 0, "paper": 1, "scissors": 2}
    choices1 = [choice_map[c] for c in player1_choices]
    choices2 = [choice_map[c] for c in player2_choices]
    
    # Process batch
    results = batch_processor.process_batch(choices1, choices2)
    
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    
    # Count results
    player1_wins = sum(1 for r in results if r == 0)
    player2_wins = sum(1 for r in results if r == 1)
    ties = sum(1 for r in results if r is None)
    
    games_per_second = request.count / (duration_ms / 1000) if duration_ms > 0 else 0
    
    return BatchGameResponse(
        total_games=request.count,
        player1_wins=player1_wins,
        player2_wins=player2_wins,
        ties=ties,
        total_duration_ms=duration_ms,
        games_per_second=games_per_second
    )


@app.post("/stress/{target_rate}", response_model=StressTestResponse)
async def stress_test(target_rate: int):
    """Run a stress test at target games per second."""
    duration_seconds = 2  # Short test for web interface
    target_games = target_rate * duration_seconds
    
    start_time = time.time()
    
    # Generate random choices
    choices1 = [random.randint(0, 2) for _ in range(target_games)]
    choices2 = [random.randint(0, 2) for _ in range(target_games)]
    
    # Process in batches to avoid memory issues
    batch_size = min(100000, target_games)
    completed_games = 0
    
    for i in range(0, target_games, batch_size):
        batch_end = min(i + batch_size, target_games)
        batch_choices1 = choices1[i:batch_end]
        batch_choices2 = choices2[i:batch_end]
        
        batch_processor.process_batch(batch_choices1, batch_choices2)
        completed_games += len(batch_choices1)
    
    end_time = time.time()
    actual_duration = end_time - start_time
    actual_rate = completed_games / actual_duration if actual_duration > 0 else 0
    
    success = actual_rate >= target_rate * 0.8  # 80% efficiency threshold
    
    return StressTestResponse(
        games_completed=completed_games,
        duration_seconds=actual_duration,
        games_per_second=actual_rate,
        target_rate=target_rate,
        success=success
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "games_processed": game_counter}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)