import google.generativeai as genai
import os
import logging
import random
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SimpleWeatherWorkflow:
    def __init__(self):
        self.gemini_client = self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini directly"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_weather_alert(self, location: str) -> dict:
        """Generate weather advice - SIMPLE and RELIABLE"""
        try:
            # Simulate weather data
            conditions = ['heavy rain', 'light rain', 'sunny', 'cloudy', 'dry spell']
            condition = random.choice(conditions)
            temperature = random.randint(20, 35)
            
            # Use Gemini for quick advice
            prompt = f"Give one sentence of farming advice for {location} with {condition} weather at {temperature}°C for maize crops."
            
            response = self.gemini_client.generate_content(prompt)
            
            return {
                "success": True,
                "workflow": "weather_alert",
                "location": location,
                "weather_data": {
                    "condition": condition,
                    "temperature": temperature,
                    "humidity": random.randint(40, 90)
                },
                "ai_advice": response.text,
                "timestamp": "2024-01-01T00:00:00Z"
            }
                
        except Exception as e:
            logger.error(f"Weather alert error: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow": "weather_alert",
                "location": location
            }

# Create instance
simple_weather = SimpleWeatherWorkflow()
