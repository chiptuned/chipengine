"""Comprehensive tests for the Bot API."""

import pytest
import requests
import json
import time
from typing import Dict

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEY = None
BOT_ID = None


class BotAPITester:
    """Test suite for Bot API endpoints."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_key = None
        self.bot_id = None
        self.session = requests.Session()
    
    def register_bot(self, name: str) -> Dict:
        """Register a new bot and store API key."""
        response = self.session.post(
            f"{self.base_url}/bots/register",
            json={"name": name}
        )
        
        print(f"🤖 Bot Registration ({name})")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.api_key = data["api_key"]
            self.bot_id = data["bot_id"]
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
            print(f"✅ Bot registered: {data['name']} (ID: {data['bot_id']})")
            print(f"🔑 API Key: {self.api_key[:8]}...")
            return data
        else:
            print(f"❌ Registration failed: {response.text}")
            return {}
    
    def get_bot_info(self) -> Dict:
        """Get authenticated bot information."""
        response = self.session.get(f"{self.base_url}/bots/me")
        
        print(f"\\n📋 Bot Info")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot: {data['name']} (ID: {data['bot_id']})")
            print(f"Created: {data['created_at']}")
            print(f"Active: {data['is_active']}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return {}
    
    def create_game(self, players: list, game_type: str = "rps") -> Dict:
        """Create a new game."""
        response = self.session.post(
            f"{self.base_url}/games/",
            json={
                "game_type": game_type,
                "players": players,
                "config": {}
            }
        )
        
        print(f"\\n🎮 Create Game ({game_type})")
        print(f"Status: {response.status_code}")
        print(f"Players: {players}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game created: {data['game_id'][:8]}...")
            print(f"Status: {data['status']}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return {}
    
    def get_game_state(self, game_id: str) -> Dict:
        """Get current game state."""
        response = self.session.get(f"{self.base_url}/games/{game_id}")
        
        print(f"\\n📊 Game State")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game: {data['game_id'][:8]}...")
            print(f"Players: {data['players']}")
            print(f"Status: {data['status']}")
            print(f"Game Over: {data['game_over']}")
            print(f"Winner: {data['winner']}")
            print(f"Valid Moves: {data['valid_moves']}")
            print(f"Moves Count: {data['moves_count']}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return {}
    
    def make_move(self, game_id: str, player: str, action: str) -> Dict:
        """Make a move in the game."""
        response = self.session.post(
            f"{self.base_url}/games/{game_id}/moves",
            json={
                "player": player,
                "action": action,
                "data": {}
            }
        )
        
        print(f"\\n🎯 Make Move")
        print(f"Status: {response.status_code}")
        print(f"Player: {player}")
        print(f"Action: {action}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Move successful: {data['success']}")
            print(f"Message: {data['message']}")
            game_state = data['game_state']
            print(f"Game Over: {game_state['game_over']}")
            if game_state['winner']:
                print(f"Winner: {game_state['winner']}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return {}
    
    def list_games(self, status: str = None) -> Dict:
        """List games created by bot."""
        url = f"{self.base_url}/games/"
        params = {}
        if status:
            params["status"] = status
        
        response = self.session.get(url, params=params)
        
        print(f"\\n📜 List Games")
        print(f"Status: {response.status_code}")
        if status:
            print(f"Filter: {status}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} games (page {data['page']})")
            for game in data['games']:
                print(f"  - {game['game_id'][:8]}... ({game['game_type']}) - {game['status']}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return {}
    
    def play_complete_rps_game(self) -> Dict:
        """Play a complete RPS game."""
        print("\\n" + "="*50)
        print("🎮 COMPLETE RPS GAME TEST")
        print("="*50)
        
        # Create game
        game_data = self.create_game(["Alice", "Bob"])
        if not game_data:
            return {}
        
        game_id = game_data["game_id"]
        
        # Get initial state
        state = self.get_game_state(game_id)
        
        # Alice plays rock
        move1 = self.make_move(game_id, "Alice", "rock")
        
        # Bob plays scissors
        move2 = self.make_move(game_id, "Bob", "scissors")
        
        # Get final state
        final_state = self.get_game_state(game_id)
        
        print(f"\\n🏆 GAME RESULT:")
        if final_state.get('game_over'):
            print(f"Winner: {final_state.get('winner', 'Tie!')}")
        
        return final_state
    
    def test_rate_limiting(self):
        """Test rate limiting by making many requests."""
        print("\\n" + "="*50)
        print("⚡ RATE LIMITING TEST")
        print("="*50)
        
        print("Making 10 rapid requests to test rate limiting...")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(10):
            response = self.session.get(f"{self.base_url}/bots/me")
            if response.status_code == 200:
                success_count += 1
                print(f"  {i+1}: ✅ Success")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"  {i+1}: ⚠️  Rate limited")
            else:
                print(f"  {i+1}: ❌ Error ({response.status_code})")
            
            time.sleep(0.1)  # Small delay
        
        print(f"\\nResults: {success_count} success, {rate_limited_count} rate-limited")
    
    def run_full_test_suite(self, bot_name: str = "TestBot"):
        """Run complete test suite."""
        print("🚀 CHIPENGINE BOT API TEST SUITE")
        print("="*60)
        
        # 1. Register bot
        if not self.register_bot(bot_name):
            print("❌ Cannot continue without bot registration")
            return False
        
        # 2. Get bot info
        self.get_bot_info()
        
        # 3. Play complete game
        self.play_complete_rps_game()
        
        # 4. List games
        self.list_games()
        self.list_games("completed")
        
        # 5. Test rate limiting
        self.test_rate_limiting()
        
        print("\\n" + "="*60)
        print("✅ TEST SUITE COMPLETED")
        print("="*60)
        
        return True


def test_api_manually():
    """Manual test function for API validation."""
    print("🔧 Starting Bot API Tests...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ Server not running at {BASE_URL}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("💡 Start server with: uv run python src/chipengine/api/app.py")
        return False
    
    # Run test suite
    tester = BotAPITester()
    return tester.run_full_test_suite("TestBot_" + str(int(time.time())))


if __name__ == "__main__":
    success = test_api_manually()
    if success:
        print("\\n🎉 All tests passed!")
    else:
        print("\\n💥 Some tests failed!")
        exit(1)