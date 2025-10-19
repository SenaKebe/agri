import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_simple():
    base_url = "http://localhost:8000"
    
    print("🧪 Simple Test - Basic Functionality")
    
    try:
        # Test 1: Basic API
        print("1. Testing basic endpoints...")
        health = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Health: {health.status_code}")
        
        agents = requests.get(f"{base_url}/api/v1/agents", timeout=5)
        print(f"   Agents: {agents.status_code}")
        
        # Test 2: RAG status
        print("2. Testing RAG...")
        rag_status = requests.get(f"{base_url}/api/v1/rag/status", timeout=5)
        print(f"   RAG Status: {rag_status.json()}")
        
        # Test 3: Initialize RAG
        print("3. Initializing RAG...")
        init = requests.post(f"{base_url}/api/v1/rag/initialize", timeout=10)
        print(f"   RAG Init: {init.json()}")
        
        # Test 4: Very simple chat with short timeout
        print("4. Testing simple chat (short timeout)...")
        simple_data = {
            "message": "Hello, say hi back",
            "location": "Test",
            "crop_type": "test"
        }
        chat = requests.post(f"{base_url}/api/v1/chat", json=simple_data, timeout=15)
        
        if chat.status_code == 200:
            data = chat.json()
            print("   ✅ CHAT WORKED!")
            print(f"   Response: {data['response']}")
        else:
            print(f"   ❌ Chat failed: {chat.status_code}")
            print(f"   Error: {chat.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out - Gemini might be slow in your region")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple()