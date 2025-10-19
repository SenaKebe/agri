import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def debug_chat_step_by_step():
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging Chat Endpoint Step by Step...")
    
    # Test 1: Simple health check
    print("\n1. Testing basic API health...")
    try:
        health = requests.get(f"{base_url}/health")
        print(f"   ✅ Health: {health.status_code}")
    except Exception as e:
        print(f"   ❌ Health failed: {e}")
        return
    
    # Test 2: Test agents endpoint
    print("\n2. Testing agents endpoint...")
    try:
        agents = requests.get(f"{base_url}/api/v1/agents")
        print(f"   ✅ Agents: {agents.status_code}")
        print(f"   Agents data: {agents.json()}")
    except Exception as e:
        print(f"   ❌ Agents failed: {e}")
    
    # Test 3: Test RAG status
    print("\n3. Testing RAG status...")
    try:
        rag_status = requests.get(f"{base_url}/api/v1/rag/status")
        print(f"   ✅ RAG Status: {rag_status.json()}")
    except Exception as e:
        print(f"   ❌ RAG status failed: {e}")
    
    # Test 4: Try a very simple chat message
    print("\n4. Testing simple chat message...")
    try:
        simple_data = {
            "message": "Hello, are you working?",
            "location": "Test",
            "crop_type": "test"
        }
        response = requests.post(f"{base_url}/api/v1/chat", json=simple_data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chat successful!")
            print(f"   Response: {data['response'][:200]}...")
        else:
            print(f"   ❌ Chat failed with status: {response.status_code}")
            print(f"   Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out - Gemini might be slow")
    except Exception as e:
        print(f"   ❌ Chat request failed: {e}")

if __name__ == "__main__":
    debug_chat_step_by_step()