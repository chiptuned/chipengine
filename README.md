# ChipEngine

A fast, lean chip engine designed for bot competitions and AI development. Starting with Rock Paper Scissors, expanding to Poker and beyond.

## Strategy: Ship Fast, Scale Smart

**Phase 1**: Rock Paper Scissors website with bot API  
**Phase 2**: Add Texas Hold'em to the same platform  
**Phase 3**: More games and optimizations

## Key Features

- **Multi-Game Architecture**: Extensible backend for any turn-based game
- **Bot-Friendly REST API**: Clean interface for AI development with JWT authentication
- **Tournament System**: Create and manage competitions with various formats
- **Real-time Updates**: WebSocket connections for live game state and tournament updates
- **Game History & Statistics**: Track performance, analyze strategies, view replays
- **Web Frontend**: Interactive game visualization with responsive design
- **PostgreSQL Database**: Robust data persistence for games, users, and tournaments
- **Comprehensive API Documentation**: OpenAPI/Swagger docs for easy integration
- **Type Safe**: Full type hints for better development experience
- **High Performance**: 15M+ RPS games/second on standard hardware

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI + WebSockets
- **Frontend**: React + Vite + Tailwind CSS + TypeScript
- **UI Components**: Headless UI, Heroicons, React Hot Toast
- **Real-time**: WebSocket connections for live updates
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with secure bot API keys
- **Package Management**: uv (backend), npm/pnpm (frontend)
- **Testing**: pytest (backend), Vitest (frontend)
- **Documentation**: OpenAPI/Swagger auto-generated from FastAPI

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+

### Development Setup

```bash
# Backend setup
cd backend
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
uv run alembic upgrade head

# Start backend server
uv run python -m chipengine.api.app

# Frontend setup (in another terminal)
cd frontend
npm install

# Start frontend dev server
npm run dev
```

### Docker Deployment (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Bot API Examples

### Authentication

```bash
# Register your bot
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "mybot", "password": "secure_password"}'

# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "mybot", "password": "secure_password"}'
# Returns: {"access_token": "your_jwt_token", "token_type": "bearer"}
```

### Playing Games

```python
import requests

# Set up authentication
headers = {"Authorization": "Bearer your_jwt_token"}
base_url = "http://localhost:8000/api/v1"

# Create a game
response = requests.post(f"{base_url}/games", 
    headers=headers,
    json={"game_type": "rock_paper_scissors", "max_players": 2}
)
game = response.json()

# Make a move
move_response = requests.post(
    f"{base_url}/games/{game['id']}/moves",
    headers=headers,
    json={"move": "rock"}
)

# Get game state
state = requests.get(f"{base_url}/games/{game['id']}", headers=headers).json()
print(f"Game status: {state['status']}, Winner: {state.get('winner')}")
```

### WebSocket Real-time Updates

```javascript
// Connect to game updates
const ws = new WebSocket('ws://localhost:8000/ws/games/game_id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Game update:', data);
  // Handle move made, game ended, etc.
};

// Send authentication
ws.send(JSON.stringify({
  type: 'auth',
  token: 'your_jwt_token'
}));
```

### Tournament Participation

```python
# Join a tournament
tournament_response = requests.post(
    f"{base_url}/tournaments/tournament_id/join",
    headers=headers
)

# Get tournament status
tournament = requests.get(
    f"{base_url}/tournaments/tournament_id",
    headers=headers
).json()

# View your matches
matches = requests.get(
    f"{base_url}/tournaments/tournament_id/matches",
    headers=headers
).json()
```

### Statistics & History

```python
# Get your bot's statistics
stats = requests.get(f"{base_url}/users/me/stats", headers=headers).json()
print(f"Win rate: {stats['win_rate']}%, Games played: {stats['total_games']}")

# Get game history
history = requests.get(
    f"{base_url}/users/me/games",
    headers=headers,
    params={"limit": 10, "game_type": "rock_paper_scissors"}
).json()

# View specific game replay
replay = requests.get(
    f"{base_url}/games/{game_id}/replay",
    headers=headers
).json()
```

## API Documentation

Full API documentation is available at `http://localhost:8000/docs` when running the server. Key endpoints include:

- **Authentication**: `/api/v1/auth/register`, `/api/v1/auth/login`
- **Games**: `/api/v1/games` (create, list, get state, make moves)
- **Tournaments**: `/api/v1/tournaments` (create, join, view standings)
- **Users**: `/api/v1/users` (profile, statistics, game history)
- **WebSocket**: `/ws/games/{game_id}`, `/ws/tournaments/{tournament_id}`

## Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost/chipengine
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Testing

```bash
# Backend tests
cd backend
uv run pytest -v

# Frontend tests
cd frontend
npm run test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Deployment

### Production with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with environment variables
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Run database migrations: `alembic upgrade head`
4. Build frontend: `npm run build`
5. Serve frontend with nginx/caddy
6. Run backend with gunicorn: `gunicorn chipengine.api.app:app`

## Roadmap

### ✅ Completed
- Rock Paper Scissors with 15M+ games/second
- REST API with JWT authentication
- WebSocket real-time updates
- PostgreSQL database integration
- Tournament system
- Game history and statistics
- Docker deployment

### 🚧 In Progress
- Texas Hold'em implementation
- Advanced tournament formats
- Bot leaderboards and rankings

### 📋 Planned
- More games (Blackjack, Go Fish, etc.)
- Machine learning bot templates
- Performance optimizations for 100M+ games/second
- Distributed tournament processing
- Bot marketplace

Perfect for AI research, bot competitions, and rapid prototyping of turn-based games.