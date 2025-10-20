import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CHECKING ENVIRONMENT VARIABLES")
print("=" * 40)

print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')[:20]}..." if os.getenv('GOOGLE_API_KEY') else "❌ NOT FOUND")
print(f"WEATHER_API_KEY: {os.getenv('WEATHER_API_KEY')}" if os.getenv('WEATHER_API_KEY') else "❌ NOT FOUND")

# Test if the same key works in Python
import requests
api_key = os.getenv('WEATHER_API_KEY')
if api_key:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Nairobi,KE&appid={api_key}&units=metric"
    response = requests.get(url)
    print(f"Python API Test: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Python can access API: {data['weather'][0]['description']} at {data['main']['temp']}°C")
    else:
        print(f"❌ Python API failed: {response.status_code}")