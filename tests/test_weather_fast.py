import requests
import time

def test_weather_fast():
    base_url = "http://localhost:8000"
    
    print("🌤️ QUICK WEATHER TEST (5s timeout)")
    print("=" * 40)
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/workflows/weather-alert?location=Central+Ethiopia",
            timeout=5  # Short timeout
        )
        end_time = time.time()
        
        print(f"✅ SUCCESS! Response time: {end_time - start_time:.1f}s")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Real Data: {data['weather_data'].get('success', False)}")
            print(f"Condition: {data['weather_data']['condition']}")
            print(f"Temperature: {data['weather_data']['temperature']}°C")
        else:
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Weather endpoint is hanging (took >5 seconds)")
        print("This means the API call or Gemini is blocking")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_weather_fast()