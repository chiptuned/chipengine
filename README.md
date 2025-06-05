# ChipEngine

A fast, lean chip engine designed for bot competitions and AI development. Starting with Rock Paper Scissors, expanding to Poker and beyond.

## Strategy: Ship Fast, Scale Smart

**Phase 1**: Rock Paper Scissors website with bot API  
**Phase 2**: Add Texas Hold'em to the same platform  
**Phase 3**: More games and optimizations

## Key Features

- **Multi-Game Architecture**: Extensible backend for any turn-based game
- **Bot-Friendly API**: Clean interface for AI development  
- **Web Frontend**: Real-time game visualization and interaction
- **Lean Development**: Ship working features fast, optimize later
- **Isolated Functions**: Each game computation is independent and testable
- **Type Safe**: Full type hints for better development experience

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI + WebSockets
- **Frontend**: React + Vite + Tailwind CSS + TypeScript
- **UI Components**: Headless UI, Heroicons, React Hot Toast
- **Real-time**: WebSocket connections for live updates
- **Database**: SQLite → PostgreSQL
- **Package Management**: uv (backend), npm/pnpm (frontend)
- **Testing**: pytest (backend), Vitest (frontend)

## Quick Start

```bash
# Install dependencies
uv sync

# Run development server
uv run python -m chipengine.server

# Run tests
uv run pytest
```

## API Example

```python
from chipengine import ChipEngine, RockPaperScissorsGame

# Create a game
engine = ChipEngine()
game_id = engine.create_game(RockPaperScissorsGame, players=2)

# Add bots
engine.add_player(game_id, "RandomBot")
engine.add_player(game_id, "MySmartBot")

# Play game
result = engine.play_game(game_id)
print(f"Winner: {result.winner}")
```

## Roadmap

1. **Week 1-2**: Rock Paper Scissors MVP
   - Web interface with bot API
   - Basic tournament system
   - Deploy and test with real users

2. **Week 3-4**: Add Texas Hold'em
   - Poker game implementation
   - Same bot interface, different game
   - Prove multi-game architecture works

3. **Week 5+**: Scale and optimize
   - Performance improvements
   - More games
   - Advanced tournament features

Perfect for AI research, bot competitions, and rapid prototyping of turn-based games.