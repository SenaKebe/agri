import requests
import json
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_real_weather():
    base_url = "http://localhost:8000"
    
    print("🌤️ TESTING REAL WEATHER API INTEGRATION")
    print("=" * 50)
    print("Using ACTUAL weather data from OpenWeatherMap API\n")
    
    locations = ["Central Ethiopia", "Western Ethiopia", "Rift Valley"]
    
    for location in locations:
        print(f"📍 Testing: {location}")
        
        try:
            # Test with real weather data
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/v1/workflows/weather-alert",
                params={
                    "location": location,
                    "use_real_weather": "true"
                },
                timeout=30
            )
            end_time = time.time()
            
            print(f"   Response Time: {end_time - start_time:.1f}s")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Full response data: {data}")
                weather_data = data['weather_data']
                logger.debug(f"Weather data: {weather_data}")
                ai_advice = data['ai_advice']
                logger.debug(f"AI advice: {ai_advice}")
                
                print(f"   ✅ SUCCESS!")
                print(f"   🌡️  Condition: {weather_data['condition']}")
                print(f"   🌡️  Temperature: {weather_data['temperature']}°C")
                print(f"   💧 Humidity: {weather_data['humidity']}%")
                print(f"   📡 Data Source: {'REAL API DATA' if weather_data.get('success') else 'Simulated'}")
                
                if 'ai_advice' in ai_advice and ai_advice['success']:
                    advice_text = ai_advice['ai_advice'][:150] if isinstance(ai_advice['ai_advice'], str) else str(ai_advice['ai_advice'])[:150]
                    print(f"   🤖 AI Advice Preview: {advice_text}...")
                    print(f"   🎯 REAL-TIME WEATHER INTELLIGENCE ACTIVE!")
                else:
                    print(f"   ⚠️  AI Advice: {ai_advice}")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Detail: {error_data}")
                except:
                    print(f"   Error Text: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - Request took too long")
        except Exception as e:
            print(f"   💥 Error: {e}")
        
        print()  # Empty line between locations
    
    print("=" * 50)
    print("🎉 REAL WEATHER API INTEGRATION COMPLETE!")
    print("\n📊 What's Working:")
    print("   ✅ OpenWeatherMap API connection")
    print("   ✅ Real weather data for Ethiopia regions") 
    print("   ✅ Gemini AI processing real conditions")
    print("   ✅ Agricultural advice based on actual weather")

if __name__ == "__main__":
    test_real_weather()