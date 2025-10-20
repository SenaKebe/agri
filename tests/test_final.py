import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_final():
    base_url = "http://localhost:8000"
    
    print("🎯 Final Test - Chat with RAG")
    
    try:
        # Initialize RAG first
        print("1. Initializing RAG...")
        init_response = requests.post(f"{base_url}/api/v1/rag/initialize")
        print(f"   {init_response.json()}")
        
        # Test chat with agricultural question
        print("\n2. Testing agricultural question...")
        chat_data = {
            "message": "When is the best time to plant maize in Central Ethiopia?",
            "location": "Central Ethiopia",
            "crop_type": "maize"
        }
        response = requests.post(f"{base_url}/api/v1/chat", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ CHAT SUCCESS!")
            print(f"   Response: {data['response']}")
            print(f"   Agents used: {[agent['agent_type'] for agent in data['agent_breakdown']]}")
            if data.get('sources'):
                print(f"   Sources: {data['sources']}")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        # Test another question
        print("\n3. Testing pest control question...")
        pest_data = {
            "message": "How do I control maize stalk borer?",
            "location": "Western Ethiopia", 
            "crop_type": "maize"
        }
        pest_response = requests.post(f"{base_url}/api/v1/chat", json=pest_data, timeout=30)
        
        if pest_response.status_code == 200:
            data = pest_response.json()
            print("   ✅ PEST CHAT SUCCESS!")
            print(f"   Response: {data['response'][:200]}...")  # First 200 chars
        else:
            print(f"   ❌ Pest chat failed: {pest_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_final()