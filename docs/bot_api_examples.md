# ChipEngine Bot API Examples

Complete examples for using the ChipEngine Bot API to create automated game bots.

## Quick Start

### 1. Register Your Bot

```bash
curl -X POST "http://localhost:8000/bots/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyAwesomeBot"}'
```

Response:
```json
{
  "bot_id": 1,
  "name": "MyAwesomeBot", 
  "api_key": "abc123...",
  "message": "Bot 'MyAwesomeBot' registered successfully! Store your API key securely."
}
```

⚠️ **Save your API key** - it cannot be retrieved later!

### 2. Authenticate Requests

Use the API key as a Bearer token in all subsequent requests:

```bash
export API_KEY="your_api_key_here"
```

### 3. Create a Game

```bash
curl -X POST "http://localhost:8000/games/" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "rps",
    "players": ["Alice", "Bob"],
    "config": {}
  }'
```

Response:
```json
{
  "game_id": "uuid-game-id",
  "game_type": "rps",
  "players": ["Alice", "Bob"],
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 4. Make Moves

```bash
# Alice plays rock
curl -X POST "http://localhost:8000/games/{game_id}/moves" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "player": "Alice",
    "action": "rock",
    "data": {}
  }'

# Bob plays scissors  
curl -X POST "http://localhost:8000/games/{game_id}/moves" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "player": "Bob", 
    "action": "scissors",
    "data": {}
  }'
```

Response:
```json
{
  "success": true,
  "message": "Move made successfully",
  "game_state": {
    "game_id": "uuid-game-id",
    "game_over": true,
    "winner": "Alice",
    "valid_moves": [],
    "moves_count": 2
  }
}
```

### 5. Check Game State

```bash
curl -X GET "http://localhost:8000/games/{game_id}" \
  -H "Authorization: Bearer $API_KEY"
```

## Python Bot Example

```python
import requests
import random

class RPSBot:
    def __init__(self, name: str, base_url: str = "http://localhost:8000"):
        self.name = name
        self.base_url = base_url
        self.api_key = None
        self.session = requests.Session()
    
    def register(self):
        """Register the bot and get API key."""
        response = self.session.post(
            f"{self.base_url}/bots/register",
            json={"name": self.name}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.api_key = data["api_key"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
            print(f"🤖 Registered as {data['name']}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    
    def create_game(self, players: list):
        """Create a new RPS game."""
        response = self.session.post(
            f"{self.base_url}/games/",
            json={
                "game_type": "rps",
                "players": players,
                "config": {}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎮 Created game {data['game_id'][:8]}...")
            return data["game_id"]
        else:
            print(f"❌ Game creation failed: {response.text}")
            return None
    
    def make_move(self, game_id: str, player: str, action: str):
        """Make a move in the game."""
        response = self.session.post(
            f"{self.base_url}/games/{game_id}/moves",
            json={
                "player": player,
                "action": action,
                "data": {}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Move failed: {response.text}")
            return None
    
    def get_random_move(self):
        """Get random RPS move."""
        return random.choice(["rock", "paper", "scissors"])
    
    def play_game(self, opponent: str = "Human"):
        """Play a complete game."""
        # Create game
        game_id = self.create_game([self.name, opponent])
        if not game_id:
            return
        
        # Bot makes first move
        bot_move = self.get_random_move()
        print(f"🤖 {self.name} plays: {bot_move}")
        
        result = self.make_move(game_id, self.name, bot_move)
        if not result:
            return
        
        # Check if game needs opponent move
        game_state = result["game_state"]
        if not game_state["game_over"]:
            # Opponent makes move (random for demo)
            opponent_move = self.get_random_move()
            print(f"👤 {opponent} plays: {opponent_move}")
            
            result = self.make_move(game_id, opponent, opponent_move)
            if result:
                game_state = result["game_state"]
        
        # Show result
        if game_state["game_over"]:
            winner = game_state["winner"]
            if winner == self.name:
                print(f"🏆 {self.name} wins!")
            elif winner:
                print(f"😞 {winner} wins!")
            else:
                print(f"🤝 It's a tie!")
        
        return game_state

# Usage
if __name__ == "__main__":
    bot = RPSBot("SmartBot")
    
    if bot.register():
        # Play 5 games
        for i in range(5):
            print(f"\\n--- Game {i+1} ---")
            bot.play_game("RandomOpponent")
```

## Advanced Features

### Rate Limiting

The API includes built-in rate limiting:
- **General API**: 1000 requests/minute per bot
- **Game Creation**: 10 games/minute per bot

Handle rate limits gracefully:

```python
def safe_request(self, method, url, **kwargs):
    """Make request with rate limit handling."""
    try:
        response = method(url, **kwargs)
        if response.status_code == 429:
            print("⚠️ Rate limited, waiting...")
            time.sleep(60)  # Wait 1 minute
            response = method(url, **kwargs)
        return response
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None
```

### Game State Monitoring

```python
def wait_for_opponent_move(self, game_id: str, timeout: int = 30):
    """Wait for opponent to make a move."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = self.session.get(f"{self.base_url}/games/{game_id}")
        
        if response.status_code == 200:
            game_state = response.json()
            
            if game_state["game_over"] or game_state["moves_count"] > 1:
                return game_state
        
        time.sleep(1)  # Poll every second
    
    print("⏰ Timeout waiting for opponent")
    return None
```

### Tournament Bot

```python
class TournamentBot(RPSBot):
    def __init__(self, name: str, strategy: str = "random"):
        super().__init__(name)
        self.strategy = strategy
        self.wins = 0
        self.losses = 0
        self.ties = 0
    
    def get_strategic_move(self, opponent_history: list = None):
        """Get move based on strategy."""
        if self.strategy == "always_rock":
            return "rock"
        elif self.strategy == "counter_rock":
            return "paper"  # Always beat rock
        elif self.strategy == "adaptive" and opponent_history:
            # Beat most common opponent move
            most_common = max(set(opponent_history), key=opponent_history.count)
            counters = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
            return counters[most_common]
        else:
            return self.get_random_move()
    
    def tournament_play(self, opponents: list, games_per_opponent: int = 10):
        """Play tournament against multiple opponents."""
        print(f"🏟️ Starting tournament: {len(opponents)} opponents, {games_per_opponent} games each")
        
        for opponent in opponents:
            print(f"\\n🆚 vs {opponent}")
            
            for game_num in range(games_per_opponent):
                result = self.play_game(opponent)
                
                if result and result["game_over"]:
                    winner = result["winner"]
                    if winner == self.name:
                        self.wins += 1
                    elif winner:
                        self.losses += 1
                    else:
                        self.ties += 1
        
        # Print final stats
        total_games = self.wins + self.losses + self.ties
        win_rate = (self.wins / total_games * 100) if total_games > 0 else 0
        
        print(f"\\n📊 Tournament Results:")
        print(f"Wins: {self.wins}")
        print(f"Losses: {self.losses}")
        print(f"Ties: {self.ties}")
        print(f"Win Rate: {win_rate:.1f}%")

# Run tournament
if __name__ == "__main__":
    tournament_bot = TournamentBot("TournamentChamp", strategy="adaptive")
    
    if tournament_bot.register():
        opponents = ["RandomBot", "RockBot", "PaperBot", "ScissorsBot"]
        tournament_bot.tournament_play(opponents, games_per_opponent=5)
```

## API Reference

### Authentication
All endpoints except `/bots/register` require Bearer token authentication:
```
Authorization: Bearer your_api_key
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bots/register` | Register new bot |
| GET | `/bots/me` | Get bot info |
| GET | `/bots/` | List all bots |
| DELETE | `/bots/me` | Deactivate bot |
| POST | `/games/` | Create game |
| GET | `/games/{id}` | Get game state |
| POST | `/games/{id}/moves` | Make move |
| GET | `/games/` | List bot's games |
| GET | `/health` | API health status |

### Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid move, game type, etc.)
- `401` - Unauthorized (invalid/missing API key)
- `404` - Not Found (game doesn't exist)
- `409` - Conflict (bot name already exists)
- `429` - Rate Limited

All errors include descriptive messages:

```json
{
  "detail": "Invalid move: rock vs scissors - game already completed"
}
```

## Testing Your Bot

Use the provided test script:

```bash
# Run comprehensive API tests
uv run python tests/test_bot_api.py

# Or test specific functionality
python -c "
from tests.test_bot_api import BotAPITester
tester = BotAPITester()
tester.run_full_test_suite('MyBot')
"
```

This will validate:
- ✅ Bot registration
- ✅ Authentication
- ✅ Game creation
- ✅ Move validation
- ✅ Game completion
- ✅ Rate limiting
- ✅ Error handling

Ready to build your bot? Start with the examples above and check `/docs` for the interactive API documentation!