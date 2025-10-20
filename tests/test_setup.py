import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_api():
    base_url = "http://localhost:8000"
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        return
    
    print("✅ GOOGLE_API_KEY found")
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health")
        print("✅ Health Check:", health_response.json())
        
        # Test agents endpoint
        agents_response = requests.get(f"{base_url}/api/v1/agents")
        print("✅ Available Agents:", agents_response.json())
        
        # Test chat endpoint with agricultural question
        print("\n🧪 Testing Agronomist Agent...")
        chat_data = {
            "message": "When is the best time to plant maize in Central Ethiopia?",
            "location": "Central Ethiopia",
            "crop_type": "maize"
        }
        chat_response = requests.post(f"{base_url}/api/v1/chat", json=chat_data)
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("✅ Chat Response Received!")
            print(f"🤖 Response: {response_data['response']}")
            print(f"🔧 Agents used: {[agent['agent_type'] for agent in response_data['agent_breakdown']]}")
        else:
            print(f"❌ Chat failed: {chat_response.status_code} - {chat_response.text}")
        
        # Test weather-related question
        print("\n🧪 Testing Weather Advisor Agent...")
        weather_data = {
            "message": "Should I plant maize if heavy rain is forecast next week?",
            "location": "Western Ethiopia", 
            "crop_type": "maize"
        }
        weather_response = requests.post(f"{base_url}/api/v1/chat", json=weather_data)
        if weather_response.status_code == 200:
            response_data = weather_response.json()
            print("✅ Weather Response Received!")
            print(f"🤖 Response: {response_data['response'][:200]}...")  # First 200 chars
            print(f"🔧 Agents used: {[agent['agent_type'] for agent in response_data['agent_breakdown']]}")
        else:
            print(f"❌ Weather chat failed: {weather_response.status_code} - {weather_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api()