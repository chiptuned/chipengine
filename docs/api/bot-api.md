# Bot API Documentation

The Bot API allows you to register bots, manage authentication, and perform bot-specific operations.

## Authentication

All Bot API endpoints (except registration) require authentication using an API key in the `X-API-Key` header.

## Endpoints

### Register Bot

Register a new bot and receive an API key.

**Endpoint:** `POST /api/bots/register`

**Request Body:**
```json
{
  "name": "string"  // Required: Bot name (3-50 characters)
}
```

**Response:**
```json
{
  "bot_id": "bot_a1b2c3d4",
  "name": "MyBot",
  "api_key": "chp_32_character_api_key_here",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/bots/register \
  -H "Content-Type: application/json" \
  -d '{"name": "AlphaBot"}'
```

---

### Get Bot Info

Retrieve information about your bot.

**Endpoint:** `GET /api/bots/{bot_id}`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Response:**
```json
{
  "bot_id": "bot_a1b2c3d4",
  "name": "MyBot",
  "created_at": "2024-01-15T10:30:00Z",
  "games_created": 42,
  "last_request_time": "2024-01-15T12:45:30Z",
  "rate_limit": 100
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/bots/bot_a1b2c3d4 \
  -H "X-API-Key: chp_your_api_key"
```

---

### Create Game

Create a new game as a bot.

**Endpoint:** `POST /api/bots/games`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Request Body:**
```json
{
  "game_type": "string",           // Required: Game type (e.g., "rps")
  "opponent_bot_id": "string",     // Optional: Bot ID to play against
  "config": {                      // Optional: Game-specific configuration
    "rounds": 3,
    "time_limit": 30
  }
}
```

**Response:**
```json
{
  "game_id": "game_xyz789",
  "game_type": "rps",
  "players": ["bot_a1b2c3d4", "bot_e5f6g7h8"],
  "status": "created",
  "your_player_id": "bot_a1b2c3d4"
}
```

**Example:**
```bash
# Create game with specific opponent
curl -X POST http://localhost:8000/api/bots/games \
  -H "X-API-Key: chp_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "rps",
    "opponent_bot_id": "bot_e5f6g7h8"
  }'

# Create open game
curl -X POST http://localhost:8000/api/bots/games \
  -H "X-API-Key: chp_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"game_type": "rps"}'
```

---

### Get Game State

Retrieve the current state of a game.

**Endpoint:** `GET /api/bots/games/{game_id}`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Response:**
```json
{
  "game_id": "game_xyz789",
  "players": ["bot_a1b2c3d4", "bot_e5f6g7h8"],
  "current_player": "bot_a1b2c3d4",
  "game_over": false,
  "winner": null,
  "valid_moves": {
    "bot_a1b2c3d4": ["rock", "paper", "scissors"],
    "bot_e5f6g7h8": []
  },
  "metadata": {
    "round": 1,
    "scores": {"bot_a1b2c3d4": 0, "bot_e5f6g7h8": 0}
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/bots/games/game_xyz789 \
  -H "X-API-Key: chp_your_api_key"
```

---

### Make Move

Make a move in a game.

**Endpoint:** `POST /api/bots/games/{game_id}/move`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Request Body:**
```json
{
  "action": "string",    // Required: Action type (game-specific)
  "data": {              // Optional: Additional move data
    "move": "rock"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Move applied successfully",
  "game_state": {
    "game_id": "game_xyz789",
    "players": ["bot_a1b2c3d4", "bot_e5f6g7h8"],
    "current_player": "bot_e5f6g7h8",
    "game_over": false,
    "winner": null,
    "valid_moves": {
      "bot_a1b2c3d4": [],
      "bot_e5f6g7h8": ["rock", "paper", "scissors"]
    },
    "metadata": {
      "round": 1,
      "last_moves": {"bot_a1b2c3d4": "rock"}
    }
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/bots/games/game_xyz789/move \
  -H "X-API-Key: chp_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "play",
    "data": {"move": "paper"}
  }'
```

---

### List Bot Games

List all games for your bot.

**Endpoint:** `GET /api/bots/games`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Query Parameters:**
- `status_filter` (optional): Filter by status ("active", "completed", or omit for all)

**Response:**
```json
{
  "games": [
    {
      "game_id": "game_xyz789",
      "game_type": "rps",
      "players": ["bot_a1b2c3d4", "bot_e5f6g7h8"],
      "current_player": null,
      "game_over": true,
      "winner": "bot_a1b2c3d4",
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total_games": 42,
  "active_games": 3,
  "completed_games": 39
}
```

**Example:**
```bash
# Get all games
curl -X GET http://localhost:8000/api/bots/games \
  -H "X-API-Key: chp_your_api_key"

# Get only active games
curl -X GET http://localhost:8000/api/bots/games?status_filter=active \
  -H "X-API-Key: chp_your_api_key"
```

---

### Get Bot Statistics

Get detailed statistics for your bot.

**Endpoint:** `GET /api/bots/stats`

**Headers:**
- `X-API-Key: {your_api_key}` (Required)

**Response:**
```json
{
  "bot_id": "bot_a1b2c3d4",
  "name": "MyBot",
  "created_at": "2024-01-15T10:30:00Z",
  "total_games": 42,
  "active_games": 3,
  "completed_games": 39,
  "wins": 25,
  "losses": 10,
  "draws": 4,
  "win_rate": 0.641,
  "game_types_played": {
    "rps": 35,
    "poker": 7
  },
  "rate_limit_usage": {
    "current_requests": 15,
    "max_requests": 100,
    "window_seconds": 60
  },
  "last_request_time": "2024-01-15T12:45:30Z"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/bots/stats \
  -H "X-API-Key: chp_your_api_key"
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "API key required"
}
```

### 403 Forbidden
```json
{
  "detail": "Cannot access other bot's information"
}
```

### 404 Not Found
```json
{
  "detail": "Game not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Max 100 requests per minute."
}
```

## Rate Limiting

Bot API endpoints are rate-limited to:
- 100 requests per minute per bot
- Rate limit is applied per API key
- Exceeding the limit returns HTTP 429

## Best Practices

1. **Store API Keys Securely**: Never commit API keys to version control
2. **Handle Rate Limits**: Implement exponential backoff when receiving 429 errors
3. **Check Game State**: Always check if it's your turn before making a move
4. **Validate Moves**: Use the `valid_moves` field to ensure your move is legal
5. **Monitor Active Games**: Regularly check and complete active games
6. **Error Handling**: Implement proper error handling for all API calls

## Game-Specific Move Formats

### Rock Paper Scissors (rps)
```json
{
  "action": "play",
  "data": {
    "move": "rock"  // Options: "rock", "paper", "scissors"
  }
}
```

### Poker (coming soon)
```json
{
  "action": "bet",
  "data": {
    "amount": 100
  }
}
```