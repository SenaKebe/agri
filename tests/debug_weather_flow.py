import requests
import os
from dotenv import load_dotenv

load_dotenv()

def debug_weather_flow():
    """Debug exactly where the weather flow is breaking"""
    
    print("🔍 DEBUGGING WEATHER DATA FLOW")
    print("=" * 50)
    
    # Test 1: Direct API call (like your curl)
    print("1. Testing Direct API Call...")
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Nairobi,KE&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   ✅ Direct API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🌡️  Real Temp: {data['main']['temp']}°C")
            print(f"   ☁️  Real Condition: {data['weather'][0]['description']}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   💥 API Exception: {e}")
    
    # Test 2: Your weather endpoint
    print("\n2. Testing Your Weather Endpoint...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/workflows/weather-alert",
            params={"location": "Central Ethiopia", "use_real_weather": "true"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            weather_data = data['weather_data']
            print(f"   ✅ Endpoint Status: 200")
            print(f"   📡 Data Source: {weather_data.get('success', 'unknown')}")
            print(f"   🌡️  Returned Temp: {weather_data['temperature']}°C")
            print(f"   ☁️  Returned Condition: {weather_data['condition']}")
            
            if weather_data.get('success'):
                print("   🎯 USING REAL WEATHER DATA!")
            else:
                print("   🔄 USING SIMULATED DATA (API call might be failing)")
        else:
            print(f"   ❌ Endpoint Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   💥 Endpoint Exception: {e}")

if __name__ == "__main__":
    debug_weather_flow()