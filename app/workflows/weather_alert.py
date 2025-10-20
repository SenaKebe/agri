import requests
import os
import logging
import google.generativeai as genai
import random
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

logger = logging.getLogger(__name__)

class RealWeatherWorkflow:
    def __init__(self):
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        if not self.weather_api_key:
            raise ValueError("WEATHER_API_KEY not found in environment variables")
        self.gemini_client = self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini with enhanced configuration"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    
    def get_real_weather_data(self, location: str) -> Dict[str, Any]:
        """Get real weather data from OpenWeatherMap API with enhanced error handling and retries"""
        try:
            location_map = {
               "Central Ethiopia": "Addis Ababa,ET",
               "Amhara Region": "Bahir Dar,ET", 
               "Oromia Region": "Jimma,ET",
               "Southern Region": "Hawassa,ET",
               "Tigray Region": "Mekele,ET"
            }
            
            city = location_map.get(location, "Nairobi,KE")
            
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            logger.debug(f"API request URL: {url}")
            
            
            session = requests.Session()
            retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            
            response = session.get(url, timeout=60)  # Increased to 60 seconds
            logger.debug(f"API response status: {response.status_code}, text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved real weather data for {location}: {data['weather'][0]['description']}")
                return {
                    "success": True,
                    "location": location,
                    "city": city.split(',')[0],
                    "condition": data['weather'][0]['description'],
                    "temperature": round(data['main']['temp']),
                    "feels_like": round(data['main']['feels_like']),
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "wind_speed": data['wind']['speed'],
                    "visibility": data.get('visibility', 'N/A'),
                    "forecast": "current",
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Weather API failed for {location} with status {response.status_code}, response text: {response.text}")
                raise Exception(f"API failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed for {location}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in weather API for {location}: {e}")
            raise

    # def _simulate_weather_data(self, location: str) -> Dict[str, Any]:
    #     """Enhanced simulated weather data with Ethiopia-specific patterns"""
    #     seasonal_conditions = {
    #         "Central Ethiopia": ['light rain', 'cloudy', 'partly cloudy', 'sunny'],
    #         "Western Ethiopia": ['moderate rain', 'overcast clouds', 'light rain', 'humid'],
    #         "Eastern Ethiopia": ['sunny', 'dry', 'clear sky', 'hot'],
    #         "Rift Valley": ['sunny', 'clear sky', 'light breeze', 'cool'],
    #         "Coastal Ethiopia": ['humid', 'partly cloudy', 'breezy', 'warm']
    #     }
        
    #     conditions = seasonal_conditions.get(location, ['sunny', 'cloudy', 'rain'])
    #     condition = random.choice(conditions)
        
    #     temp_ranges = {
    #         "Central Ethiopia": (15, 25),
    #         "Western Ethiopia": (18, 28),
    #         "Eastern Ethiopia": (22, 35),
    #         "Rift Valley": (12, 22),
    #         "Coastal Ethiopia": (24, 32)
    #     }
        
    #     temp_min, temp_max = temp_ranges.get(location, (20, 30))
        
    #     return {
    #         "success": False,
    #         "location": location,
    #         "condition": condition,
    #         "temperature": random.randint(temp_min, temp_max),
    #         "humidity": random.randint(50, 85),
    #         "forecast": "simulated",
    #         "retrieved_at": datetime.now().isoformat(),
    #         "note": "Simulated data due to API failure"
    #     }
    
    def generate_weather_alert(self, location: str, use_real_weather: bool = True) -> Dict[str, Any]:
        """Generate comprehensive agricultural advice with real weather data or fallback to simulation"""
        try:
            # Get weather data (real or simulated)
            if use_real_weather and self.weather_api_key:
                try:
                    weather_data = self.get_real_weather_data(location)
                    is_real_data = weather_data.get('success', False)
                    data_source = "Real-time OpenWeatherMap API" if is_real_data else "Simulated (API unavailable)"
                except Exception as e:
                    logger.warning(f"Fallback to simulation for {location} due to: {e}")
                    weather_data = self._simulate_weather_data(location)
                    is_real_data = False
                    data_source = "Simulated (API failure)"
            else:
                weather_data = self._simulate_weather_data(location)
                is_real_data = False
                data_source = "Simulated by request"
            
            # Enhanced prompt for more contextual advice
            condition = weather_data['condition']
            temperature = weather_data['temperature']
            humidity = weather_data['humidity']
            
            prompt = f"""**ROLE**: Expert Agricultural Weather Advisor for Ethiopian Maize Farmers
**LOCATION**: {location}
**CURRENT WEATHER**:
- Condition: {condition}
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Data Source: {data_source}

**YOUR TASK**: Provide SPECIFIC, ACTIONABLE advice for small-scale maize farmers in Ethiopia.

**STRUCTURE YOUR RESPONSE**:

1. **IMMEDIATE ACTIONS** (What to do today/tomorrow)
2. **CROP-SPECIFIC RISKS** (Disease, pests, growth issues)
3. **WEATHER OPPORTUNITIES** (How to leverage current conditions)
4. **3-DAY OUTLOOK** (Specific recommendations)
5. **WARNINGS/ALERTS** (Critical issues to watch for)

**KEY FOCUS**: Practical, affordable solutions for small-scale farmers. Consider soil moisture, pest activity, and growth stages.

**RESPONSE FORMAT**: Use clear, simple language with bullet points."""

            logger.info(f"Generating weather advice for {location} with {condition} at {temperature}°C")
            response = self.gemini_client.generate_content(prompt)
            
            return {
                "success": True,
                "workflow": "weather_alert",
                "location": location,
                "weather_data": weather_data,
                "ai_advice": {
                    "success": True,
                    "location": location,
                    "weather_condition": condition,
                    "temperature": temperature,
                    "ai_advice": response.text,
                    "data_source": data_source,
                    "generated_at": datetime.now().isoformat()
                },
                "metadata": {
                    "data_source": "real" if is_real_data else "simulated",
                    "response_time": "real_time" if is_real_data else "simulated",
                    "agricultural_focus": "maize_cultivation",
                    "farmer_level": "small_scale"
                },
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Weather alert generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow": "weather_alert",
                "timestamp": datetime.now().isoformat()
            }

# Initialize the enhanced workflow
weather_alert = RealWeatherWorkflow()