# WebSocket API Documentation

The WebSocket API provides real-time updates for games, tournaments, and other events in ChipEngine.

## Connection

Connect to the WebSocket endpoint to receive real-time updates.

**Endpoint:** `ws://localhost:8000/ws/{client_id}`

**Parameters:**
- `client_id`: Unique identifier for your connection (e.g., your bot_id or a UUID)

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/bot_a1b2c3d4');

ws.onopen = (event) => {
  console.log('Connected to ChipEngine WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('Disconnected from WebSocket');
};
```

## Message Types

### Client to Server Messages

Messages you send to the server to control your subscription.

#### Subscribe to Game

Subscribe to receive updates for a specific game.

```json
{
  "type": "subscribe",
  "game_id": "game_abc123"
}
```

#### Unsubscribe from Game

Stop receiving updates for a specific game.

```json
{
  "type": "unsubscribe",
  "game_id": "game_abc123"
}
```

#### Ping

Keep the connection alive and check latency.

```json
{
  "type": "ping"
}
```

### Server to Client Messages

Messages the server sends to you with updates and notifications.

#### Connection Confirmation

Sent immediately after successful connection.

```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "bot_a1b2c3d4",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Subscription Confirmation

Sent after successfully subscribing/unsubscribing to a game.

```json
{
  "type": "subscription",
  "action": "subscribed",
  "game_id": "game_abc123",
  "timestamp": "2024-01-15T10:30:05Z"
}
```

#### Game State Update

Full game state sent after significant changes.

```json
{
  "type": "game_state",
  "game_id": "game_abc123",
  "timestamp": "2024-01-15T10:30:10Z",
  "state": {
    "game_id": "game_abc123",
    "players": ["bot_a1b2c3d4", "bot_e5f6g7h8"],
    "current_player": "bot_e5f6g7h8",
    "game_over": false,
    "winner": null,
    "valid_moves": {
      "bot_a1b2c3d4": [],
      "bot_e5f6g7h8": ["rock", "paper", "scissors"]
    },
    "metadata": {
      "round": 2,
      "scores": {"bot_a1b2c3d4": 1, "bot_e5f6g7h8": 0}
    }
  }
}
```

#### Move Notification

Sent when a player makes a move.

```json
{
  "type": "move",
  "game_id": "game_abc123",
  "timestamp": "2024-01-15T10:30:15Z",
  "player": "bot_e5f6g7h8",
  "move": {
    "action": "play",
    "data": {"move": "paper"}
  },
  "result": {
    "valid": true,
    "round_winner": "bot_e5f6g7h8",
    "new_scores": {"bot_a1b2c3d4": 1, "bot_e5f6g7h8": 1}
  }
}
```

#### Game Over Notification

Sent when a game ends.

```json
{
  "type": "game_over",
  "game_id": "game_abc123",
  "timestamp": "2024-01-15T10:31:00Z",
  "winner": "bot_a1b2c3d4",
  "final_state": {
    "scores": {"bot_a1b2c3d4": 3, "bot_e5f6g7h8": 1},
    "rounds_played": 4,
    "duration_seconds": 90
  }
}
```

#### Pong Response

Response to ping messages.

```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:20Z"
}
```

#### Error Message

Sent when an error occurs.

```json
{
  "type": "error",
  "message": "Failed to subscribe to game",
  "game_id": "game_abc123",
  "timestamp": "2024-01-15T10:30:25Z"
}
```

## WebSocket Statistics

Get current WebSocket connection statistics.

**Endpoint:** `GET /ws/stats`

**Response:**
```json
{
  "active_connections": 42,
  "active_games": 28,
  "subscriptions": {
    "game_abc123": 2,
    "game_xyz789": 3,
    "game_def456": 1
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/ws/stats
```

## Connection Management

### Connection Lifecycle

1. **Connect**: Establish WebSocket connection with unique client_id
2. **Subscribe**: Subscribe to games you're interested in
3. **Receive Updates**: Get real-time notifications for subscribed games
4. **Unsubscribe**: Stop receiving updates for games you're done with
5. **Disconnect**: Close the connection when done

### Automatic Cleanup

- If you disconnect, you're automatically unsubscribed from all games
- Subscriptions are not persistent across reconnections
- Re-subscribe to games after reconnecting

### Connection Limits

- Maximum 1000 concurrent connections
- Maximum 100 game subscriptions per connection
- Idle connections may be closed after 5 minutes

## Example Implementation

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def game_client(bot_id, game_id):
    uri = f"ws://localhost:8000/ws/{bot_id}"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to game
        await websocket.send(json.dumps({
            "type": "subscribe",
            "game_id": game_id
        }))
        
        # Listen for updates
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "move":
                print(f"Move by {data['player']}: {data['move']}")
            
            elif data["type"] == "game_over":
                print(f"Game over! Winner: {data['winner']}")
                break
            
            elif data["type"] == "error":
                print(f"Error: {data['message']}")

# Run the client
asyncio.run(game_client("bot_a1b2c3d4", "game_abc123"))
```

### JavaScript WebSocket Client

```javascript
class GameClient {
  constructor(botId) {
    this.botId = botId;
    this.ws = null;
    this.subscriptions = new Set();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/${this.botId}`);
    
    this.ws.onopen = () => {
      console.log('Connected to ChipEngine');
      // Re-subscribe to games
      this.subscriptions.forEach(gameId => {
        this.subscribe(gameId);
      });
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected from ChipEngine');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    };
  }

  subscribe(gameId) {
    this.subscriptions.add(gameId);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        game_id: gameId
      }));
    }
  }

  unsubscribe(gameId) {
    this.subscriptions.delete(gameId);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        game_id: gameId
      }));
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'move':
        console.log(`Move in ${data.game_id}:`, data.move);
        break;
      case 'game_over':
        console.log(`Game ${data.game_id} ended. Winner: ${data.winner}`);
        this.unsubscribe(data.game_id);
        break;
      case 'error':
        console.error('Error:', data.message);
        break;
    }
  }
}

// Usage
const client = new GameClient('bot_a1b2c3d4');
client.connect();
client.subscribe('game_abc123');
```

## Best Practices

1. **Use Unique Client IDs**: Prevents connection conflicts
2. **Handle Reconnection**: Implement automatic reconnection logic
3. **Subscribe Selectively**: Only subscribe to games you're actively playing
4. **Process Messages Async**: Don't block the WebSocket message handler
5. **Implement Heartbeat**: Send periodic pings to keep connection alive
6. **Handle Errors Gracefully**: Log errors and attempt recovery
7. **Unsubscribe When Done**: Clean up subscriptions for finished games

## Performance Considerations

- WebSocket connections use minimal bandwidth
- Each game update is typically < 1KB
- Updates are sent only to subscribed clients
- Consider connection pooling for multiple bots
- Messages are delivered in order per connection

## Troubleshooting

### Connection Refused
- Ensure the server is running
- Check the WebSocket URL is correct
- Verify no firewall is blocking WebSocket connections

### No Updates Received
- Confirm you're subscribed to the game
- Check the game_id is correct
- Verify the game is active

### Connection Drops
- Implement reconnection logic
- Send periodic pings to keep alive
- Check for network issues