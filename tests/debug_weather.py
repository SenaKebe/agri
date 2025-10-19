import requests
import time
from dotenv import load_dotenv

load_dotenv()

def debug_weather_endpoint():
    base_url = "http://localhost:8000"
    
    print("🔍 DEBUGGING WEATHER ENDPOINT")
    print("=" * 40)
    
    # Test 1: Check if endpoint exists
    print("1. Checking endpoint availability...")
    try:
        # Try a GET request first to see if endpoint exists
        response = requests.get(f"{base_url}/api/v1/workflows/weather-alert", timeout=5)
        print(f"   GET Status: {response.status_code}")
    except Exception as e:
        print(f"   GET Error: {e}")
    
    # Test 2: Try POST with very short timeout to see if it's hanging
    print("2. Testing POST request...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/workflows/weather-alert?location=Test",
            timeout=5
        )
        end_time = time.time()
        print(f"   POST Success: {response.status_code} in {end_time-start_time:.2f}s")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except requests.exceptions.Timeout:
        print("   ⏰ POST Timeout - Endpoint is hanging")
    except Exception as e:
        print(f"   POST Error: {e}")
    
    print("\n3. Testing alternative endpoints...")
    endpoints = ["/health", "/api/v1/agents", "/api/v1/rag/status"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   ✅ {endpoint}: {response.status_code}")
        except:
            print(f"   ❌ {endpoint}: Failed")

if __name__ == "__main__":
    debug_weather_endpoint()