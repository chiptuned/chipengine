# Game API Documentation

The Game API provides endpoints for creating and managing games directly, without bot authentication. These endpoints are useful for administrative purposes, testing, and building custom game interfaces.

## Endpoints

### Create Game

Create a new game with specified players.

**Endpoint:** `POST /games`

**Request Body:**
```json
{
  "game_type": "string",      // Required: Game type (e.g., "rps", "poker")
  "players": ["string"],      // Required: Array of player IDs
  "config": {                 // Optional: Game-specific configuration
    "rounds": 3,
    "time_limit": 30
  }
}
```

**Response:**
```json
{
  "game_id": "game_abc123",
  "game_type": "rps",
  "players": ["player1", "player2"],
  "status": "created"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/games \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "rps",
    "players": ["alice", "bob"],
    "config": {"rounds": 5}
  }'
```

---

### Get Game State

Retrieve the current state of a game.

**Endpoint:** `GET /games/{game_id}/state`

**Response:**
```json
{
  "game_id": "game_abc123",
  "players": ["player1", "player2"],
  "current_player": "player1",
  "game_over": false,
  "winner": null,
  "valid_moves": {
    "player1": ["rock", "paper", "scissors"],
    "player2": []
  },
  "metadata": {
    "round": 1,
    "scores": {"player1": 0, "player2": 0},
    "history": []
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/games/game_abc123/state
```

---

### Make Move

Make a move in a game.

**Endpoint:** `POST /games/{game_id}/moves`

**Request Body:**
```json
{
  "player": "string",         // Required: Player making the move
  "action": "string",         // Required: Action type (game-specific)
  "data": {                   // Optional: Additional move data
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
    "game_id": "game_abc123",
    "players": ["player1", "player2"],
    "current_player": "player2",
    "game_over": false,
    "winner": null,
    "valid_moves": {
      "player1": [],
      "player2": ["rock", "paper", "scissors"]
    },
    "metadata": {
      "round": 1,
      "scores": {"player1": 0, "player2": 0},
      "last_moves": {"player1": "rock"}
    }
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/games/game_abc123/moves \
  -H "Content-Type: application/json" \
  -d '{
    "player": "player1",
    "action": "play",
    "data": {"move": "paper"}
  }'
```

---

### Get Game Result

Get the final result of a completed game.

**Endpoint:** `GET /games/{game_id}/result`

**Response:**
```json
{
  "game_id": "game_abc123",
  "winner": "player1",
  "players": ["player1", "player2"],
  "duration_seconds": 45.2,
  "metadata": {
    "final_scores": {"player1": 3, "player2": 1},
    "rounds_played": 4,
    "move_history": [
      {"round": 1, "player1": "rock", "player2": "scissors", "winner": "player1"},
      {"round": 2, "player1": "paper", "player2": "paper", "winner": null},
      {"round": 3, "player1": "scissors", "player2": "rock", "winner": "player2"},
      {"round": 4, "player1": "rock", "player2": "scissors", "winner": "player1"}
    ]
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/games/game_abc123/result
```

---

### Delete Game

Delete a game from memory.

**Endpoint:** `DELETE /games/{game_id}`

**Response:**
```json
{
  "message": "Game deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/games/game_abc123
```

---

### Get Game Manager Stats

Get statistics about the game manager.

**Endpoint:** `GET /games/stats`

**Response:**
```json
{
  "active_games": 42,
  "total_games_created": 1337,
  "games_by_type": {
    "rps": 1200,
    "poker": 137
  },
  "average_game_duration": 62.5,
  "peak_concurrent_games": 156,
  "memory_usage": {
    "games_in_memory": 42,
    "estimated_mb": 2.5
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/games/stats
```

---

### Cleanup Finished Games

Remove finished games from memory to free resources.

**Endpoint:** `POST /games/cleanup`

**Response:**
```json
{
  "message": "Cleaned up 25 finished games"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/games/cleanup
```

## Game States

Games progress through the following states:

1. **Created** - Game is created but not started
2. **In Progress** - Game is active and accepting moves
3. **Completed** - Game has ended with a winner or draw
4. **Cancelled** - Game was cancelled before completion

## Valid Moves

The `valid_moves` field in the game state indicates which moves are currently available for each player. This is game-specific:

### Rock Paper Scissors
- When it's your turn: `["rock", "paper", "scissors"]`
- When it's not your turn: `[]`
- When game is over: `[]`

### Poker (coming soon)
- Actions: `["check", "bet", "raise", "call", "fold"]`
- Depends on game state and previous actions

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid move: It's not your turn"
}
```

### 404 Not Found
```json
{
  "detail": "Game not found"
}
```

## Game Configuration

Each game type supports different configuration options:

### Rock Paper Scissors
```json
{
  "rounds": 3,           // Number of rounds (default: 3)
  "time_limit": 30       // Time limit per move in seconds (optional)
}
```

### Poker (coming soon)
```json
{
  "starting_chips": 1000,
  "small_blind": 10,
  "big_blind": 20,
  "max_players": 6
}
```

## Move Data Formats

### Rock Paper Scissors
```json
{
  "player": "player1",
  "action": "play",
  "data": {
    "move": "rock"  // Options: "rock", "paper", "scissors"
  }
}
```

### Poker (coming soon)
```json
{
  "player": "player1",
  "action": "bet",
  "data": {
    "amount": 100
  }
}
```

## Best Practices

1. **Validate Game State**: Always check the game state before making moves
2. **Handle Game Over**: Check `game_over` flag and stop making moves
3. **Use Valid Moves**: Only attempt moves listed in `valid_moves`
4. **Clean Up Games**: Use the cleanup endpoint to free memory
5. **Monitor Active Games**: Track and complete games to avoid memory leaks

## Performance Considerations

- Games are stored in memory for fast access
- Finished games should be cleaned up regularly
- The game manager can handle thousands of concurrent games
- Each game type has different memory requirements:
  - RPS: ~1KB per game
  - Poker: ~10KB per game (estimated)