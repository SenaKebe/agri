from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.schemas import ChatRequest, ChatResponse, AgentResponse, AgentType, UserCreate, UserLogin, Token
from app.workflows.weather_alert import RealWeatherWorkflow , weather_alert # Assuming this is the weather workflow
from app.agents.base import BaseAgent
from typing import List, Dict, Any, Optional
from app.rag.rag_manager import rag_manager
from app.workflows.simple_weather import simple_weather
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Security configurations
SECRET_KEY = "your-secret-key-here"  # Replace with os.getenv("JWT_SECRET_KEY") for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (replace with database later)
fake_users_db = {}

# OAuth2 scheme for token dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    user = fake_users_db.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(email)
    if user is None:
        raise credentials_exception
    return user

class AgronomistAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert agronomist specializing in maize cultivation in Ethiopia. 
        Provide practical, actionable advice for small-scale farmers. Focus on:
        - Planting timing and techniques
        - Soil preparation and fertilizer recommendations
        - Pest and disease management
        - Water management and irrigation
        - Harvesting and post-harvest handling
        
        Be specific to Ethiopian growing conditions and use simple, clear language."""
        super().__init__("Agronomist", system_prompt)

class WeatherAdvisorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a weather advisor for farmers in Ethiopia. 
        Provide weather-based agricultural recommendations focusing on:
        - Optimal planting windows based on rainfall patterns
        - Weather risk management (drought, heavy rain, storms)
        - Harvest timing considering weather forecasts
        - Microclimate considerations for different Ethiopian regions
        
        Base your advice on typical Ethiopian weather patterns and seasons."""
        super().__init__("Weather Advisor", system_prompt)

class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator"
        self.role = "Route queries to appropriate specialist agents"
        self.agronomist = AgronomistAgent()
        self.weather_advisor = WeatherAdvisorAgent()
        self.weather_workflow = RealWeatherWorkflow()  # Initialize weather workflow

    def analyze_query(self, query: str) -> List[AgentType]:
        """Determine which agents should handle this query"""
        query_lower = query.lower()
        agents_to_engage = []
        
        agricultural_keywords = ['plant', 'crop', 'maize', 'fertilizer', 'pest', 'harvest', 'soil', 'seed', 'cultivation', 'yield']
        weather_keywords = ['weather', 'rain', 'forecast', 'dry', 'drought', 'storm', 'season', 'rainfall']
        
        if any(keyword in query_lower for keyword in agricultural_keywords):
            agents_to_engage.append(AgentType.AGRONOMIST)
        if any(keyword in query_lower for keyword in weather_keywords):
            agents_to_engage.append(AgentType.WEATHER_ADVISOR)
        if not agents_to_engage:
            agents_to_engage.append(AgentType.AGRONOMIST)
        return agents_to_engage

    async def get_agent_response(self, agent_type: AgentType, query: str, state: Dict) -> AgentResponse:
        """Get response from a specific agent with shared state"""
        try:
            context = state.get("context", "")
            if agent_type == AgentType.WEATHER_ADVISOR:
                # Fetch weather data and update state
                location = state.get("location", "Central Ethiopia")
                weather_data = self.weather_workflow.get_real_weather_data(location)
                state["weather_data"] = weather_data  # Share weather data with other agents
                response = await self.weather_advisor.generate_response(query, f"Weather Context: {weather_data}")
                return AgentResponse(
                    agent_type=AgentType.WEATHER_ADVISOR,
                    response=response,
                    confidence=0.80,
                    sources=[{"type": "weather_api", "provider": "real_weather"}]
                )
            elif agent_type == AgentType.AGRONOMIST:
                # Use weather data from state if available
                weather_context = f"Weather: {state.get('weather_data', 'No weather data available')}" if "weather_data" in state else ""
                rag_context = rag_manager.get_agricultural_context(query)
                full_context = f"{weather_context}\n\nRelevant Agricultural Knowledge: {rag_context}"
                response = await self.agronomist.generate_response(query, full_context)
                return AgentResponse(
                    agent_type=AgentType.AGRONOMIST,
                    response=response,
                    confidence=0.85,
                    sources=self._extract_sources_from_context(rag_context)
                )
        except Exception as e:
            logger.error(f"Error from {agent_type}: {str(e)}")
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
                    sources.append({"type": "document", "name": source_name, "provider": "agricultural_knowledge_base"})
        if not sources:
            sources.append({"type": "ai_model", "model": "Gemini Pro"})
        return sources

    def format_response(self, agent_responses: List[AgentResponse]) -> str:
        """Combine agent responses into a coherent answer"""
        if not agent_responses:
            return "I'm not sure how to help with that. Could you provide more details about your agricultural question?"
        if len(agent_responses) == 1:
            return agent_responses[0].response
        combined = f"{agent_responses[0].response}\n\n"
        for i, agent_resp in enumerate(agent_responses[1:], 1):
            agent_type_name = agent_resp.agent_type.value.replace('_', ' ')
            combined += f"Additionally, from a {agent_type_name} perspective: {agent_resp.response}\n"
        return combined

# Initialize orchestrator
orchestrator = OrchestratorAgent()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.email] = {"name": user.name, "hashed_password": hashed_password}
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login and get access token"""
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    user_dict = fake_users_db.get(user.email)
    if not user_dict or not verify_password(user.password, user_dict["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(request: ChatRequest):
    """Main chat endpoint for agricultural advice with agent communication"""
    try:
        logger.info(f"Chat request - Location: {request.location}, Crop: {request.crop_type}")
        
        # Initialize shared state
        state = {
            "context": f"Location: {request.location or 'Ethiopia'}, Crop: {request.crop_type or 'maize'}",
            "location": request.location or "Central Ethiopia"
        }
        
        agents_needed = orchestrator.analyze_query(request.message)
        logger.info(f"Agents needed: {agents_needed}")
        
        agent_responses = []
        for agent_type in agents_needed:
            try:
                response = await orchestrator.get_agent_response(agent_type, request.message, state)
                agent_responses.append(response)
                # Update state with the latest response for subsequent agents
                state["context"] += f"\n\nPrevious Response ({response.agent_type.value}): {response.response}"
            except Exception as agent_error:
                logger.error(f"Error from {agent_type}: {str(agent_error)}")
                agent_responses.append(AgentResponse(
                    agent_type=agent_type,
                    response=f"The {agent_type.value} is currently unavailable.",
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
    location: str = "Central Ethiopia",
    use_real_weather: bool = True
):
    """Enhanced weather alert with real API data"""
    try:
        result = weather_alert.generate_weather_alert(location, use_real_weather)
        return result
    except Exception as e:
        logger.error(f"Weather alert error: {e}")
        raise HTTPException(status_code=500, detail=f"Weather alert error: {str(e)}")    

@router.get("/examples")
async def get_example_questions():
    """Get example questions to test the system"""
    return {
        "example_questions": [
            {
                "question": "When is the best time to plant maize in Central Ethiopia?",
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