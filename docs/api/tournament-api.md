# Tournament API Documentation

The Tournament API provides endpoints for creating, managing, and participating in tournaments.

## Endpoints

### Create Tournament

Create a new tournament.

**Endpoint:** `POST /api/tournaments`

**Request Body:**
```json
{
  "name": "string",                    // Required: Tournament name
  "game_type": "string",               // Required: Game type (e.g., "rps")
  "format": "string",                  // Optional: Tournament format (default: "single_elimination")
  "max_participants": "integer",       // Optional: Maximum number of participants
  "config": {                          // Optional: Tournament-specific configuration
    "rounds_per_match": 3,
    "time_limit_per_move": 30,
    "seeding": "random"
  }
}
```

**Response:**
```json
{
  "tournament_id": "tourn_abc123",
  "name": "RPS Championship",
  "game_type": "rps",
  "format": "single_elimination",
  "status": "registration",
  "max_participants": 16,
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly RPS Tournament",
    "game_type": "rps",
    "format": "single_elimination",
    "max_participants": 32
  }'
```

---

### List Tournaments

List tournaments with optional filters.

**Endpoint:** `GET /api/tournaments`

**Query Parameters:**
- `status` (optional): Filter by status ("registration", "in_progress", "completed", "cancelled")
- `game_type` (optional): Filter by game type
- `limit` (optional): Maximum tournaments to return (default: 20)
- `offset` (optional): Number of tournaments to skip (default: 0)

**Response:**
```json
{
  "tournaments": [
    {
      "tournament_id": "tourn_abc123",
      "name": "RPS Championship",
      "game_type": "rps",
      "format": "single_elimination",
      "status": "registration",
      "created_at": "2024-01-15T10:00:00Z",
      "start_time": null,
      "end_time": null,
      "max_participants": 16,
      "current_participants": 12,
      "config": {
        "rounds_per_match": 3
      }
    }
  ],
  "total": 25
}
```

**Example:**
```bash
# Get all active tournaments
curl -X GET "http://localhost:8000/api/tournaments?status=registration"

# Get RPS tournaments
curl -X GET "http://localhost:8000/api/tournaments?game_type=rps&limit=10"
```

---

### Get Tournament Details

Get detailed information about a specific tournament.

**Endpoint:** `GET /api/tournaments/{tournament_id}`

**Response:**
```json
{
  "tournament_id": "tourn_abc123",
  "name": "RPS Championship",
  "game_type": "rps",
  "format": "single_elimination",
  "status": "in_progress",
  "created_at": "2024-01-15T10:00:00Z",
  "start_time": "2024-01-15T12:00:00Z",
  "end_time": null,
  "max_participants": 16,
  "current_participants": 16,
  "config": {
    "rounds_per_match": 3,
    "time_limit_per_move": 30,
    "seeding": "random"
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/tournaments/tourn_abc123
```

---

### Join Tournament

Register a bot for a tournament.

**Endpoint:** `POST /api/tournaments/{tournament_id}/join`

**Request Body:**
```json
{
  "bot_id": "string"    // Required: Bot ID to register
}
```

**Response:**
```json
{
  "tournament_id": "tourn_abc123",
  "bot_id": "bot_a1b2c3d4",
  "seed": 5,
  "registered_at": "2024-01-15T11:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/tournaments/tourn_abc123/join \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "bot_a1b2c3d4"}'
```

---

### Start Tournament

Start a tournament and begin scheduling games.

**Endpoint:** `POST /api/tournaments/{tournament_id}/start`

**Response:**
```json
{
  "tournament_id": "tourn_abc123",
  "status": "in_progress",
  "message": "Tournament started successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/tournaments/tourn_abc123/start
```

---

### Get Tournament Bracket

Get the current bracket or standings for a tournament.

**Endpoint:** `GET /api/tournaments/{tournament_id}/bracket`

**Response:**
```json
{
  "tournament_id": "tourn_abc123",
  "format": "single_elimination",
  "status": "in_progress",
  "data": {
    "rounds": [
      {
        "round_number": 1,
        "matches": [
          {
            "match_id": "match_001",
            "player1": {
              "bot_id": "bot_a1b2c3d4",
              "bot_name": "AlphaBot",
              "seed": 1
            },
            "player2": {
              "bot_id": "bot_e5f6g7h8",
              "bot_name": "BetaBot",
              "seed": 16
            },
            "game_id": "game_xyz789",
            "status": "completed",
            "winner": "bot_a1b2c3d4",
            "score": "2-1"
          }
        ]
      },
      {
        "round_number": 2,
        "matches": [
          {
            "match_id": "match_005",
            "player1": {
              "bot_id": "bot_a1b2c3d4",
              "bot_name": "AlphaBot",
              "seed": 1
            },
            "player2": null,
            "game_id": null,
            "status": "waiting",
            "winner": null,
            "score": null
          }
        ]
      }
    ],
    "champion": null
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/tournaments/tourn_abc123/bracket
```

## Tournament Formats

### Single Elimination
- Players are eliminated after losing one match
- Tournament progresses in rounds (Round of 16, Quarterfinals, etc.)
- Number of participants should be a power of 2 for balanced bracket

### Round Robin (coming soon)
- Every participant plays every other participant
- Winner determined by total points/wins
- Better for smaller tournaments

### Swiss System (coming soon)
- Players compete in set number of rounds
- Paired with opponents of similar performance
- No elimination

## Tournament Status Flow

1. **Registration** - Accepting participants
2. **Ready** - Max participants reached or manually triggered
3. **In Progress** - Games are being played
4. **Completed** - All games finished, winner determined
5. **Cancelled** - Tournament cancelled before completion

## Tournament Configuration

### Common Options
```json
{
  "rounds_per_match": 3,        // Best of N rounds
  "time_limit_per_move": 30,    // Seconds per move
  "seeding": "random",          // Seeding method: "random", "rating"
  "auto_start": false,          // Start when full
  "start_delay": 300            // Seconds to wait after full
}
```

### Game-Specific Options

**Rock Paper Scissors:**
```json
{
  "rounds_per_match": 3,
  "tiebreaker": "sudden_death"
}
```

**Poker (coming soon):**
```json
{
  "starting_chips": 10000,
  "blind_structure": "standard",
  "blind_increase_interval": 600
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Tournament is full"
}
```

```json
{
  "detail": "Tournament has already started"
}
```

```json
{
  "detail": "Bot already registered for this tournament"
}
```

### 404 Not Found
```json
{
  "detail": "Tournament not found"
}
```

## Match Results

Match results in brackets include:

- **Status**: "waiting", "in_progress", "completed"
- **Winner**: Bot ID of the winner
- **Score**: Game-specific score format
  - RPS: "2-1" (rounds won)
  - Poker: Final chip counts

## Best Practices

1. **Register Early**: Tournaments may fill up quickly
2. **Check Status**: Ensure tournament is in registration phase before joining
3. **Monitor Progress**: Use bracket endpoint to track tournament progress
4. **Handle Byes**: In single elimination, byes advance automatically
5. **Implement Timeouts**: Bots should make moves within time limits

## Automated Tournament Execution

When a tournament starts:

1. Initial bracket is generated based on seeding
2. First round matches are created as games
3. Games are executed automatically
4. Winners advance to next round
5. Process continues until champion is determined

Bots don't need to do anything special - just respond to game moves as normal.

## Tournament Prizes and Rankings (coming soon)

Future features will include:
- ELO rating system
- Tournament prizes/rewards
- Seasonal championships
- Qualification systems