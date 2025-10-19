import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_simple_weather():
    base_url = "http://localhost:8000"
    
    print("🌤️ TESTING SIMPLE WEATHER WORKFLOW")
    print("=" * 40)
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/workflows/simple-weather-alert?location=Central+Kenya",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SIMPLE WEATHER WORKFLOW SUCCESS!")
            print(f"Location: {data['location']}")
            print(f"Weather: {data['weather_data']['condition']}")
            print(f"Temperature: {data['weather_data']['temperature']}°C")
            print(f"AI Advice: {data['ai_advice']}")
        else:
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - There's a deeper issue")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_simple_weather()