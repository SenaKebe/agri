import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

def test_all_fastapi_endpoints():
    base_url = "http://localhost:8000"
    
    print("🚀 TESTING ALL FASTAPI ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        # Basic endpoints
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/test-imports", "Import status"),
        ("GET", "/system/info", "System information"),
        
        # Agent endpoints
        ("GET", "/api/v1/agents", "List agents"),
        ("GET", "/api/v1/examples", "Example questions"),
        
        # RAG endpoints
        ("GET", "/api/v1/rag/status", "RAG status"),
        ("POST", "/api/v1/rag/initialize", "Initialize RAG"),
        
        # Chat endpoints
        ("POST", "/api/v1/chat", "Chat with advisor"),
        
        # Workflow endpoints
        ("POST", "/api/v1/workflows/weather-alert", "Weather alert workflow"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n🔍 {method} {endpoint} - {description}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            elif method == "POST":
                if endpoint == "/api/v1/chat":
                    data = {
                        "message": "Test message - are you working?",
                        "location": "Test Location",
                        "crop_type": "maize"
                    }
                    response = requests.post(f"{base_url}{endpoint}", json=data, timeout=15)
                elif endpoint == "/api/v1/rag/initialize":
                    response = requests.post(f"{base_url}{endpoint}", timeout=15)
                elif endpoint == "/api/v1/workflows/weather-alert":
                    response = requests.post(f"{base_url}{endpoint}?location=Central+Kenya", timeout=15)
                else:
                    response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS - Response keys: {list(data.keys())}")
                except:
                    print(f"   ✅ SUCCESS - Non-JSON response")
            else:
                print(f"   ❌ FAILED - Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Endpoint took too long")
        except Exception as e:
            print(f"   💥 ERROR - {e}")

def test_chat_with_different_questions():
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 50)
    print("💬 TESTING CHAT WITH DIFFERENT QUESTION TYPES")
    print("=" * 50)
    
    test_cases = [
        {
            "message": "Hello! What can you help me with?",
            "location": "Central Kenya",
            "crop_type": "maize",
            "type": "greeting"
        },
        {
            "message": "When should I plant maize?",
            "location": "Western Kenya", 
            "crop_type": "maize",
            "type": "planting_timing"
        },
        {
            "message": "What about the weather for planting?",
            "location": "Central Kenya",
            "crop_type": "maize", 
            "type": "weather_advice"
        },
        {
            "message": "How do I control pests in my maize farm?",
            "location": "Eastern Kenya",
            "crop_type": "maize",
            "type": "pest_control"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['type']}")
        print(f"   Question: {test_case['message']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/v1/chat",
                json=test_case,
                timeout=20
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                agents = [agent['agent_type'] for agent in data['agent_breakdown']]
                print(f"   ✅ Response time: {end_time - start_time:.2f}s")
                print(f"   🤖 Agents used: {agents}")
                print(f"   📝 Response preview: {data['response'][:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    test_all_fastapi_endpoints()
    test_chat_with_different_questions()