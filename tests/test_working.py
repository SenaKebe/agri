import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_working():
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Working Implementation")
    
    try:
        # Test basic connectivity
        print("1. Testing server connectivity...")
        health = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Server is running: {health.status_code}")
        
        # Test RAG initialization
        print("2. Initializing RAG...")
        init_response = requests.post(f"{base_url}/api/v1/rag/initialize", timeout=10)
        print(f"   ✅ RAG Initialized: {init_response.json()}")
        
        # Test with a very simple message first
        print("3. Testing simple greeting...")
        simple_data = {
            "message": "Hello! Can you say hi back?",
            "location": "Test",
            "crop_type": "test"
        }
        
        response = requests.post(f"{base_url}/api/v1/chat", json=simple_data, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ CHAT SUCCESS!")
            print(f"   Response: {data['response']}")
            print(f"   Agents used: {[agent['agent_type'] for agent in data['agent_breakdown']]}")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("   🔌 Connection error - is the server running?")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_working()