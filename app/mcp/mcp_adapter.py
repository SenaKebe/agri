from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class N8NMCPService:
    def __init__(self):
        self.name = "n8n-weather-adapter"
    
    async def process_n8n_weather_data(self, city: str, weather_data: Dict[str, Any], orchestrator, weather_alert) -> Dict[str, Any]:
        """Process n8n weather data through your MCP system"""
        try:
            # Map city to region for your agricultural system
            region_map = {
                "Addis Ababa": "Central Ethiopia",
                "Bahir Dar": "Amhara Region", 
                "Hawassa": "Southern Region",
                "Mekele": "Tigray Region",
                "Dire Dawa": "Eastern Ethiopia",
                "Jimma": "Oromia Region"
            }
            
            region = region_map.get(city, "Central Ethiopia")
            
            # Import here to avoid circular imports
            from app.models.schemas import ChatRequest
            
            # Get enhanced agricultural analysis from your existing system
            chat_request = ChatRequest(
                message=f"Weather update for {city}: {weather_data['condition']}, {weather_data['temperature']}°C. What agricultural advice?",
                location=region,
                crop_type="maize"
            )
            
            # Use your existing orchestrator
            chat_response = await orchestrator.chat_with_advisor(chat_request)
            
            # Get weather risk analysis from your existing system
            weather_alert_result = weather_alert.generate_weather_alert(region, use_real_weather=True)
            
            return {
                "success": True,
                "city": city,
                "region": region,
                "basic_weather": weather_data,
                "agricultural_analysis": chat_response.response,
                "risk_analysis": weather_alert_result.get("ai_advice", {}),
                "agent_breakdown": getattr(chat_response, 'agent_breakdown', []),
                "timestamp": weather_data.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error processing n8n data: {e}")
            return {
                "success": False,
                "error": str(e),
                "city": city,
                "basic_weather": weather_data
            }

# Initialize service
n8n_service = N8NMCPService()

# Dependency to get orchestrator and weather_alert
async def get_services():
    from app.agents.orchestrator import orchestrator
    from app.workflows.weather_alert import weather_alert
    return orchestrator, weather_alert

@router.post("/mcp/n8n/process-weather")
async def process_n8n_weather(data: Dict[str, Any], services = Depends(get_services)):
    """Endpoint that accepts your existing n8n weather data format"""
    try:
        orchestrator, weather_alert = services
        city = data.get('city')
        weather_data = {
            'temperature': data.get('temperature'),
            'condition': data.get('condition'),
            'humidity': data.get('humidity'),
            'risk': data.get('risk'),
            'timestamp': data.get('timestamp')
        }
        
        result = await n8n_service.process_n8n_weather_data(city, weather_data, orchestrator, weather_alert)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/n8n/enhance-alert")
async def enhance_n8n_alert(data: Dict[str, Any], services = Depends(get_services)):
    """Enhance your existing n8n alerts with agricultural intelligence"""
    try:
        orchestrator, weather_alert = services
        city = data.get('city')
        basic_alert = data.get('recommendation', '')
        risk_level = data.get('risk', 'Low')
        
        # Get specialized agricultural advice based on risk level
        region_map = {
            "Addis Ababa": "Central Ethiopia",
            "Bahir Dar": "Amhara Region",
            "Hawassa": "Southern Region", 
            "Mekele": "Tigray Region",
            "Dire Dawa": "Eastern Ethiopia",
            "Jimma": "Oromia Region"
        }
        
        region = region_map.get(city, "Central Ethiopia")
        
        if risk_level in ["High", "Medium"]:
            # Use your weather advisor agent for high/medium risk
            state = {"location": region, "context": f"High risk alert: {basic_alert}"}
            agent_response = await orchestrator.get_agent_response(
                "WEATHER_ADVISOR", 
                f"High risk weather in {city}: {basic_alert}. Provide specific agricultural emergency advice.",
                state
            )
            enhanced_advice = agent_response.response
        else:
            # Use agronomist for normal conditions
            state = {"location": region, "context": f"Normal conditions: {basic_alert}"}
            agent_response = await orchestrator.get_agent_response(
                "AGRONOMIST",
                f"Normal weather in {city}: {basic_alert}. Provide optimal farming advice.",
                state
            )
            enhanced_advice = agent_response.response
        
        return {
            "success": True,
            "city": city,
            "region": region,
            "original_alert": basic_alert,
            "enhanced_agricultural_advice": enhanced_advice,
            "risk_level": risk_level,
            "agents_consulted": [agent_response.agent_type.value],
            "confidence": agent_response.confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp/n8n/health")
async def n8n_health_check():
    """Health check for n8n integration"""
    return {
        "status": "healthy",
        "service": "n8n-mcp-adapter",
        "capabilities": [
            "process-n8n-weather",
            "enhance-n8n-alerts", 
            "agricultural-risk-analysis"
        ],
        "compatible_with_existing_n8n": True
    }