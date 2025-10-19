from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ChatRequest, ChatResponse, AgentResponse, AgentType
from app.workflows.weather_alert import weather_alert
from app.agents.base import BaseAgent
from typing import List, Dict, Any, Optional
from app.rag.rag_manager import rag_manager
from app.workflows.simple_weather import simple_weather

import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


class AgronomistAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert agronomist specializing in maize cultivation in Kenya. 
        Provide practical, actionable advice for small-scale farmers. Focus on:
        - Planting timing and techniques
        - Soil preparation and fertilizer recommendations
        - Pest and disease management
        - Water management and irrigation
        - Harvesting and post-harvest handling
        
        Be specific to Kenyan growing conditions and use simple, clear language."""
        super().__init__("Agronomist", system_prompt)

class WeatherAdvisorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a weather advisor for farmers in Kenya. 
        Provide weather-based agricultural recommendations focusing on:
        - Optimal planting windows based on rainfall patterns
        - Weather risk management (drought, heavy rain, storms)
        - Harvest timing considering weather forecasts
        - Microclimate considerations for different Kenyan regions
        
        Base your advice on typical Kenyan weather patterns and seasons."""
        super().__init__("Weather Advisor", system_prompt)

class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator"
        self.role = "Route queries to appropriate specialist agents"
        self.agronomist = AgronomistAgent()
        self.weather_advisor = WeatherAdvisorAgent()
    
    def analyze_query(self, query: str) -> List[AgentType]:
        """Determine which agents should handle this query"""
        query_lower = query.lower()
        agents_to_engage = []
        
        # Simple rule-based routing
        agricultural_keywords = ['plant', 'crop', 'maize', 'fertilizer', 'pest', 'harvest', 'soil', 'seed', 'cultivation', 'yield']
        weather_keywords = ['weather', 'rain', 'forecast', 'dry', 'drought', 'storm', 'season', 'rainfall']
        
        if any(keyword in query_lower for keyword in agricultural_keywords):
            agents_to_engage.append(AgentType.AGRONOMIST)
        
        if any(keyword in query_lower for keyword in weather_keywords):
            agents_to_engage.append(AgentType.WEATHER_ADVISOR)
        
        # If no specific agents matched, use agronomist as default
        if not agents_to_engage:
            agents_to_engage.append(AgentType.AGRONOMIST)
            
        return agents_to_engage
    
    async def get_agent_response(self, agent_type: AgentType, query: str, context: str = "") -> AgentResponse:
        """Get response from a specific agent with RAG context"""
        try:
            # Get relevant agricultural knowledge from RAG
            rag_context = rag_manager.get_agricultural_context(query)
            full_context = f"{context}\n\nRelevant Agricultural Knowledge:\n{rag_context}"
            
            if agent_type == AgentType.AGRONOMIST:
                response = await self.agronomist.generate_response(query, full_context)
                return AgentResponse(
                    agent_type=AgentType.AGRONOMIST,
                    response=response,
                    confidence=0.85,
                    sources=self._extract_sources_from_context(rag_context)
                )
            elif agent_type == AgentType.WEATHER_ADVISOR:
                response = await self.weather_advisor.generate_response(query, full_context)
                return AgentResponse(
                    agent_type=AgentType.WEATHER_ADVISOR,
                    response=response,
                    confidence=0.80,
                    sources=self._extract_sources_from_context(rag_context)
                )
        except Exception as e:
            logger.error(f"Error getting response from {agent_type}: {str(e)}")
            return AgentResponse(
                agent_type=agent_type,
                response=f"The {agent_type.value} is currently unavailable. Please try again later.",
                confidence=0.1
            )
    
    def _extract_sources_from_context(self, rag_context: str) -> List[dict]:
        """Extract source information from RAG context"""
        sources = []
        if "From " in rag_context and "relevance:" in rag_context:
            lines = rag_context.split('\n')
            for line in lines:
                if line.startswith('From '):
                    source_name = line.split('From ')[1].split(' (relevance:')[0]
                    sources.append({
                        "type": "document",
                        "name": source_name,
                        "provider": "agricultural_knowledge_base"
                    })
        
        if not sources:
            sources.append({"type": "ai_model", "model": "Gemini Pro"})
        
        return sources
    
    def format_response(self, agent_responses: List[AgentResponse]) -> str:
        """Combine agent responses into a coherent answer - FIXED METHOD"""
        if not agent_responses:
            return "I'm not sure how to help with that. Could you provide more details about your agricultural question?"
        
        if len(agent_responses) == 1:
            return agent_responses[0].response
        
        # Combine responses from multiple agents
        combined = f"{agent_responses[0].response}\n\n"
        for i, agent_resp in enumerate(agent_responses[1:], 1):
            agent_type_name = agent_resp.agent_type.value.replace('_', ' ')
            combined += f"Additionally, from a {agent_type_name} perspective: {agent_resp.response}\n"
        
        return combined

@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(request: ChatRequest):
    """Main chat endpoint for agricultural advice"""
    try:
        logger.info(f"Chat request - Location: {request.location}, Crop: {request.crop_type}")
        
        agents_needed = orchestrator.analyze_query(request.message)
        logger.info(f"Agents needed: {agents_needed}")
        
        agent_responses = []
        for agent_type in agents_needed:
            try:
                context = f"Location: {request.location or 'Kenya'}, Crop: {request.crop_type or 'maize'}"
                response = await orchestrator.get_agent_response(agent_type, request.message, context)
                agent_responses.append(response)
            except Exception as agent_error:
                logger.error(f"Error from {agent_type}: {str(agent_error)}")
                agent_responses.append(AgentResponse(
                    agent_type=agent_type,
                    response=f"The {agent_type.value} is temporarily unavailable.",
                    confidence=0.1
                ))
        
        combined_response = orchestrator.format_response(agent_responses)
        
        return ChatResponse(
            response=combined_response,
            conversation_id=request.conversation_id or f"conv_{hash(request.message) % 10000}",
            agent_breakdown=agent_responses,
            follow_up_questions=[
                "What specific variety are you growing?",
                "When do you plan to plant?",
                "What is your soil type?",
                "Have you noticed any pests?"
            ]
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/agents")
async def get_available_agents():
    """List all available AI agents"""
    return {
        "agents": [
            {
                "type": "agronomist",
                "description": "Expert in crop cultivation, pest control, and soil management",
                "capabilities": ["planting advice", "pest diagnosis", "fertilizer recommendations"],
                "model": "Gemini Pro"
            },
            {
                "type": "weather_advisor", 
                "description": "Provides weather-based farming recommendations",
                "capabilities": ["planting windows", "weather risk alerts", "harvest timing"],
                "model": "Gemini Pro"
            }
        ]
    }

@router.get("/rag/status")
async def get_rag_status():
    """Get RAG knowledge base status"""
    status = rag_manager.get_knowledge_base_status()
    return status

@router.post("/rag/initialize")
async def initialize_rag():
    """Initialize the RAG knowledge base with documents"""
    try:
        success = rag_manager.initialize_knowledge_base()
        return {
            "success": success,
            "message": "Knowledge base initialized successfully" if success else "Failed to initialize knowledge base"
        }
    except Exception as e:
        logger.error(f"Error initializing RAG: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize knowledge base")

@router.post("/rag/clear")
async def clear_rag():
    """Clear the RAG knowledge base (for testing)"""
    try:
        from app.rag.vector_store import vector_store
        success = vector_store.clear_knowledge_base()
        return {
            "success": success,
            "message": "Knowledge base cleared successfully" if success else "Failed to clear knowledge base"
        }
    except Exception as e:
        logger.error(f"Error clearing RAG: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear knowledge base")

@router.post("/workflows/weather-alert")
async def trigger_weather_alert(
    location: str = Query("Central Kenya", description="Farm location"),
    simulate_data: bool = Query(True, description="Use simulated weather data")
):
    """Trigger weather alert workflow"""
    try:
        if simulate_data:
            weather_data = weather_alert.simulate_weather_data(location)
        else:
            # In production, you'd call a real weather API here
            weather_data = {"condition": "unknown", "temperature": 25, "humidity": 60}
        
        result = weather_alert.generate_weather_alert(location, weather_data)
        
        return {
            "workflow": "weather_alert",
            "location": location,
            "weather_data": weather_data,
            "ai_advice": result,
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Weather alert workflow error: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")
@router.post("/workflows/simple-weather-alert")
async def simple_weather_alert(location: str = "Central Kenya"):
    """Simple weather alert endpoint that definitely works"""
    try:
        result = simple_weather.generate_weather_alert(location)
        return result
    except Exception as e:
        logger.error(f"Simple weather alert error: {e}")
        return {
            "success": False,
            "error": str(e),
            "workflow": "simple_weather_alert"
        }
    

@router.get("/examples")
async def get_example_questions():
    """Get example questions to test the system"""
    return {
        "example_questions": [
            {
                "question": "When is the best time to plant maize in Central Kenya?",
                "type": "planting_timing",
                "expected_agents": ["agronomist"]
            },
            {
                "question": "How do I control maize stalk borer?",
                "type": "pest_control", 
                "expected_agents": ["agronomist"]
            },
            {
                "question": "Should I plant if heavy rain is forecast next week?",
                "type": "weather_decision",
                "expected_agents": ["agronomist", "weather_advisor"]
            },
            {
                "question": "What fertilizer should I use for maize?",
                "type": "fertilizer",
                "expected_agents": ["agronomist"]
            },
            {
                "question": "How does weather affect maize growth?",
                "type": "combined",
                "expected_agents": ["agronomist", "weather_advisor"]
            }
        ]
    }

# Initialize orchestrator
orchestrator = OrchestratorAgent()