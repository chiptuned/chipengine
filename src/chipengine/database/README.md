# ChipEngine Database Module

This module provides the database infrastructure for ChipEngine using SQLAlchemy 2.0+.

## Models

### Bot
Represents an AI player/bot in the system.
- `id`: UUID primary key
- `name`: Unique bot name
- `api_key`: Auto-generated secure API key for authentication
- `created_at`: Timestamp of creation
- `is_active`: Whether the bot is currently active
- `description`: Optional bot description
- `owner_email`: Optional owner email
- `last_active`: Timestamp of last activity

### Game
Represents a single game instance.
- `id`: UUID primary key
- `game_type`: Type of game (e.g., "rock_paper_scissors", "poker")
- `state`: JSON field storing game state
- `status`: Game status (waiting, in_progress, completed, cancelled)
- `created_at`: Game creation timestamp
- `completed_at`: Game completion timestamp
- `winner_id`: Reference to winning bot
- `tournament_id`: Optional reference to tournament
- `round_number`: Round number if part of tournament
- `config`: JSON field for game-specific configuration

### Player
Represents a bot's participation in a specific game.
- `id`: UUID primary key
- `bot_id`: Reference to bot
- `game_id`: Reference to game
- `player_number`: Player position in game
- `final_position`: Final ranking (1st, 2nd, etc.)
- `score`: Player's score
- `joined_at`: When player joined
- `left_at`: When player left (if disconnected)

### Move
Represents a single action/move in a game.
- `id`: UUID primary key
- `game_id`: Reference to game
- `player_id`: Reference to player
- `move_data`: JSON field with move details
- `timestamp`: When move was made
- `move_number`: Sequential move number
- `time_taken_ms`: Time taken to make move

### Tournament
Represents a competition between multiple bots.
- `id`: UUID primary key
- `name`: Tournament name
- `game_type`: Type of game
- `format`: Tournament format (single_elimination, double_elimination, round_robin, swiss)
- `status`: Tournament status
- `created_at`: Creation timestamp
- `start_time`: Scheduled start time
- `end_time`: Actual end time
- `max_participants`: Maximum number of participants
- `config`: JSON field for tournament-specific settings

### TournamentParticipant
Association table for bots participating in tournaments.
- `tournament_id`: Reference to tournament
- `bot_id`: Reference to bot
- `registered_at`: Registration timestamp
- `seed`: Initial seeding
- `final_rank`: Final tournament ranking
- `wins`: Number of wins
- `losses`: Number of losses
- `draws`: Number of draws
- `games_played`: Total games played
- `score`: Points scored (for point-based tournaments)
- `eliminated`: Whether bot has been eliminated

## Usage

### Initialize Database

```python
from chipengine.database import init_db

# Create all tables
init_db()
```

Or run the initialization script:
```bash
python -m chipengine.database.init_db
```

### Session Management

```python
from chipengine.database.session import get_db_context, DatabaseSession

# Using context manager
with get_db_context() as db:
    bots = db.query(Bot).all()

# Using class-based session
with DatabaseSession() as db:
    game = db.query(Game).first()

# For FastAPI dependency injection
from chipengine.database.session import get_db

@app.get("/bots")
def list_bots(db: Session = Depends(get_db)):
    return db.query(Bot).all()
```

### Environment Variables

- `DATABASE_URL`: Database connection string (defaults to `sqlite:///./chipengine.db`)
- `DATABASE_ECHO`: Set to "true" to log SQL queries (useful for debugging)

### Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Example Usage

See `example_usage.py` for comprehensive examples of:
- Creating bots, games, and tournaments
- Recording moves and game results
- Querying data with relationships
- Complex queries with aggregations

## Database Support

The models are designed to work with both PostgreSQL (production) and SQLite (development):
- PostgreSQL: Full support with connection pooling
- SQLite: Development support with appropriate settings
- Other databases: Should work with minor adjustments

## Indexes

The models include indexes on commonly queried fields:
- Bot: name, owner_email
- Game: game_type, status, created_at, completed_at
- Move: game_id + timestamp, player_id + timestamp
- Tournament: name, game_type, status
- TournamentParticipant: tournament_id + final_rank

## Relationships

- Bot -> Player (one-to-many)
- Bot -> TournamentParticipant (one-to-many)
- Game -> Player (one-to-many)
- Game -> Move (one-to-many)
- Player -> Move (one-to-many)
- Tournament -> TournamentParticipant (one-to-many)
- Tournament -> Game (one-to-many)