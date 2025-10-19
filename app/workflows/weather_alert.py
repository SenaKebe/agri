import requests
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

logger = logging.getLogger(__name__)

class WeatherAlertWorkflow:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        # Initialize Gemini directly for faster responses
        self.gemini_client = self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini directly for workflow use"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_weather_alert(self, location: str, weather_data: Dict) -> Dict[str, Any]:
        """Generate agricultural advice based on weather data - FIXED VERSION"""
        try:
            # Use Gemini directly instead of calling our own API (avoids loops)
            condition = weather_data.get('condition', 'unknown')
            temperature = weather_data.get('temperature', 25)
            
            prompt = f"""As a weather advisor for Kenyan farmers, provide brief, actionable advice for maize cultivation.

Location: {location}
Weather Condition: {condition}
Temperature: {temperature}°C
Humidity: {weather_data.get('humidity', 60)}%

Provide 2-3 specific recommendations for maize farmers in this weather:"""
            
            response = self.gemini_client.generate_content(prompt)
            
            return {
                "success": True,
                "location": location,
                "weather_condition": condition,
                "ai_advice": response.text,
                "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
            }
                
        except Exception as e:
            logger.error(f"Weather alert error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def simulate_weather_data(self, location: str) -> Dict[str, Any]:
        """Simulate weather data for demo purposes"""
        import random
        conditions = ['heavy rain', 'light rain', 'sunny', 'cloudy', 'dry spell']
        condition = random.choice(conditions)
        
        return {
            "location": location,
            "condition": condition,
            "temperature": random.randint(20, 35),
            "humidity": random.randint(40, 90),
            "forecast": "next 3 days"
        }

# Initialize the instance properly
weather_alert = WeatherAlertWorkflow()