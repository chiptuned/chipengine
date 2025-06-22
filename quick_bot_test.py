#!/usr/bin/env python3
"""Quick test of Bot API functionality."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_bot_api():
    """Test basic bot API functionality."""
    print("🚀 Testing ChipEngine Bot API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Start server with: uv run python start_bot_api.py")
        return False
    
    # Test 2: Register bot
    print("\n2. Testing bot registration...")
    bot_name = f"TestBot_{int(time.time())}"
    try:
        response = requests.post(
            f"{BASE_URL}/bots/register",
            json={"name": bot_name}
        )
        
        if response.status_code == 200:
            bot_data = response.json()
            print("✅ Bot registration successful")
            print(f"   Bot ID: {bot_data['bot_id']}")
            print(f"   API Key: {bot_data['api_key'][:8]}...")
            
            api_key = bot_data["api_key"]
            headers = {"Authorization": f"Bearer {api_key}"}
            
        else:
            print(f"❌ Bot registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 3: Get bot info
    print("\n3. Testing bot authentication...")
    try:
        response = requests.get(f"{BASE_URL}/bots/me", headers=headers)
        if response.status_code == 200:
            print("✅ Authentication successful")
            bot_info = response.json()
            print(f"   Bot: {bot_info['name']}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False
    
    # Test 4: Create game
    print("\n4. Testing game creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/games/",
            headers=headers,
            json={
                "game_type": "rps",
                "players": ["Alice", "Bob"],
                "config": {}
            }
        )
        
        if response.status_code == 200:
            game_data = response.json()
            print("✅ Game creation successful")
            print(f"   Game ID: {game_data['game_id'][:8]}...")
            print(f"   Players: {game_data['players']}")
            
            game_id = game_data["game_id"]
            
        else:
            print(f"❌ Game creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Game creation error: {e}")
        return False
    
    # Test 5: Make moves
    print("\n5. Testing game moves...")
    try:
        # Alice plays rock
        response = requests.post(
            f"{BASE_URL}/games/{game_id}/moves",
            headers=headers,
            json={
                "player": "Alice",
                "action": "rock",
                "data": {}
            }
        )
        
        if response.status_code == 200:
            move_data = response.json()
            print("✅ First move successful")
            print(f"   Alice plays: rock")
            print(f"   Game over: {move_data['game_state']['game_over']}")
            
        else:
            print(f"❌ First move failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Bob plays scissors
        response = requests.post(
            f"{BASE_URL}/games/{game_id}/moves",
            headers=headers,
            json={
                "player": "Bob",
                "action": "scissors",
                "data": {}
            }
        )
        
        if response.status_code == 200:
            move_data = response.json()
            print("✅ Second move successful")
            print(f"   Bob plays: scissors")
            print(f"   Game over: {move_data['game_state']['game_over']}")
            print(f"   Winner: {move_data['game_state']['winner']}")
            
        else:
            print(f"❌ Second move failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Move error: {e}")
        return False
    
    # Test 6: Check game state
    print("\n6. Testing game state retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/games/{game_id}", headers=headers)
        if response.status_code == 200:
            game_state = response.json()
            print("✅ Game state retrieval successful")
            print(f"   Status: {game_state['status']}")
            print(f"   Moves: {game_state['moves_count']}")
            print(f"   Winner: {game_state['winner']}")
        else:
            print(f"❌ Game state failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Game state error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Bot API is working correctly")
    print("\nAPI Endpoints tested:")
    print("  - Health check")
    print("  - Bot registration") 
    print("  - Authentication")
    print("  - Game creation")
    print("  - Move submission")
    print("  - Game state retrieval")
    print("\n📚 Check /docs for full API documentation")
    return True

if __name__ == "__main__":
    success = test_bot_api()
    if not success:
        exit(1)