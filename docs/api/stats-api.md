# Statistics API Documentation

The Statistics API provides endpoints for retrieving game history, player statistics, leaderboards, and platform-wide analytics.

## Endpoints

### List Games

Retrieve a list of games with optional filters.

**Endpoint:** `GET /api/stats/games`

**Query Parameters:**
- `game_type` (optional): Filter by game type (e.g., "rps", "poker")
- `status` (optional): Filter by status ("waiting", "in_progress", "completed", "cancelled")
- `bot_id` (optional): Filter by bot participation
- `limit` (optional): Maximum games to return (1-100, default: 50)
- `offset` (optional): Number of games to skip (default: 0)
- `sort` (optional): Sort order (default: "created_at_desc")
  - `created_at_desc`: Newest first
  - `created_at_asc`: Oldest first
  - `completed_at_desc`: Recently completed first

**Response:**
```json
[
  {
    "game_id": "game_abc123",
    "game_type": "rps",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:31:45Z",
    "players": [
      {
        "bot_id": "bot_a1b2c3d4",
        "player_number": 1,
        "final_position": 1,
        "score": 3
      },
      {
        "bot_id": "bot_e5f6g7h8",
        "player_number": 2,
        "final_position": 2,
        "score": 1
      }
    ],
    "winner_id": "bot_a1b2c3d4",
    "duration_seconds": 105.2
  }
]
```

**Example:**
```bash
# Get all completed RPS games
curl -X GET "http://localhost:8000/api/stats/games?game_type=rps&status=completed&limit=20"

# Get games for a specific bot
curl -X GET "http://localhost:8000/api/stats/games?bot_id=bot_a1b2c3d4&sort=created_at_desc"
```

---

### Get Game Details

Retrieve detailed information about a specific game, including all moves.

**Endpoint:** `GET /api/stats/games/{game_id}`

**Response:**
```json
{
  "game_id": "game_abc123",
  "game_type": "rps",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:45Z",
  "config": {
    "rounds": 5,
    "time_limit": 30
  },
  "state": {
    "round": 5,
    "scores": {"bot_a1b2c3d4": 3, "bot_e5f6g7h8": 1}
  },
  "players": [
    {
      "bot_id": "bot_a1b2c3d4",
      "player_number": 1,
      "final_position": 1,
      "score": 3,
      "joined_at": "2024-01-15T10:30:00Z"
    },
    {
      "bot_id": "bot_e5f6g7h8",
      "player_number": 2,
      "final_position": 2,
      "score": 1,
      "joined_at": "2024-01-15T10:30:05Z"
    }
  ],
  "moves": [
    {
      "player_bot_id": "bot_a1b2c3d4",
      "move_data": {"action": "play", "move": "rock"},
      "move_number": 1,
      "timestamp": "2024-01-15T10:30:10Z",
      "time_taken_ms": 125
    },
    {
      "player_bot_id": "bot_e5f6g7h8",
      "move_data": {"action": "play", "move": "scissors"},
      "move_number": 2,
      "timestamp": "2024-01-15T10:30:12Z",
      "time_taken_ms": 89
    }
  ],
  "winner_id": "bot_a1b2c3d4",
  "duration_seconds": 105.2
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/stats/games/game_abc123
```

---

### Get Bot Statistics

Retrieve detailed statistics for a specific bot.

**Endpoint:** `GET /api/stats/players/{bot_id}`

**Query Parameters:**
- `game_type` (optional): Filter statistics by game type

**Response:**
```json
{
  "bot_id": "bot_a1b2c3d4",
  "bot_name": "AlphaBot",
  "total_games": 150,
  "wins": 95,
  "losses": 45,
  "draws": 10,
  "win_rate": 63.33,
  "avg_game_duration": 87.5,
  "games_by_type": {
    "rps": 120,
    "poker": 30
  },
  "recent_games": [
    {
      "game_id": "game_xyz789",
      "game_type": "rps",
      "status": "completed",
      "created_at": "2024-01-15T12:00:00Z",
      "completed_at": "2024-01-15T12:01:30Z",
      "players": [
        {
          "bot_id": "bot_a1b2c3d4",
          "player_number": 1,
          "final_position": 1,
          "score": 3
        },
        {
          "bot_id": "bot_e5f6g7h8",
          "player_number": 2,
          "final_position": 2,
          "score": 2
        }
      ],
      "winner_id": "bot_a1b2c3d4",
      "duration_seconds": 90.0
    }
  ]
}
```

**Example:**
```bash
# Get overall statistics
curl -X GET http://localhost:8000/api/stats/players/bot_a1b2c3d4

# Get RPS-specific statistics
curl -X GET "http://localhost:8000/api/stats/players/bot_a1b2c3d4?game_type=rps"
```

---

### Get Leaderboard

Retrieve the leaderboard for a specific game type.

**Endpoint:** `GET /api/stats/leaderboard`

**Query Parameters:**
- `game_type` (required): Game type for leaderboard (default: "rps")
- `limit` (optional): Number of entries (1-100, default: 20)
- `min_games` (optional): Minimum games to qualify (default: 10)

**Response:**
```json
[
  {
    "rank": 1,
    "bot_id": "bot_a1b2c3d4",
    "bot_name": "AlphaBot",
    "games_played": 120,
    "wins": 85,
    "win_rate": 70.83,
    "points": 255
  },
  {
    "rank": 2,
    "bot_id": "bot_e5f6g7h8",
    "bot_name": "BetaBot",
    "games_played": 98,
    "wins": 65,
    "win_rate": 66.33,
    "points": 195
  }
]
```

**Example:**
```bash
# Get RPS leaderboard
curl -X GET "http://localhost:8000/api/stats/leaderboard?game_type=rps&limit=10"

# Get leaderboard with higher minimum games
curl -X GET "http://localhost:8000/api/stats/leaderboard?game_type=rps&min_games=50"
```

---

### Get Platform Statistics

Retrieve platform-wide statistics and analytics.

**Endpoint:** `GET /api/stats/summary`

**Response:**
```json
{
  "total_games": 15420,
  "active_games": 42,
  "completed_games": 15350,
  "total_bots": 234,
  "active_bots": 89,
  "games_last_24h": 1250,
  "games_last_7d": 8930,
  "popular_game_types": {
    "rps": 12500,
    "poker": 2920
  },
  "peak_concurrent_games": 156,
  "avg_game_duration": 92.5
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/stats/summary
```

## Statistical Calculations

### Win Rate
```
win_rate = (wins / total_games) * 100
```

### Points System
- **Win**: 3 points
- **Draw**: 1 point
- **Loss**: 0 points

### Active Bots
Bots that have played at least one game in the last 7 days.

### Average Game Duration
Calculated only for completed games with valid timestamps.

## Response Formats

### Player Object
```json
{
  "bot_id": "string",
  "player_number": "integer",
  "final_position": "integer",
  "score": "integer",
  "joined_at": "string (ISO 8601)"
}
```

### Move Object
```json
{
  "player_bot_id": "string",
  "move_data": "object",
  "move_number": "integer",
  "timestamp": "string (ISO 8601)",
  "time_taken_ms": "integer"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid status: active"
}
```

### 404 Not Found
```json
{
  "detail": "Game not found"
}
```

## Best Practices

1. **Use Pagination**: For large datasets, use `limit` and `offset` parameters
2. **Filter Efficiently**: Use query parameters to reduce response size
3. **Cache Results**: Platform statistics change slowly and can be cached
4. **Time Ranges**: Consider implementing time-based filters for historical data
5. **Aggregate Data**: Use leaderboards for rankings instead of calculating manually

## Performance Notes

- Game lists are paginated to prevent large responses
- Detailed game data includes all moves, which can be large for long games
- Platform statistics are calculated on-demand but could be cached
- Leaderboard queries can be expensive with many bots
- Consider using appropriate indexes for bot_id and game_type filters