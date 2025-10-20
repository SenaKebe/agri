from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentType(str, Enum):
    AGRONOMIST = "agronomist"
    WEATHER_ADVISOR = "weather_advisor" 
    SOIL_SPECIALIST = "soil_specialist"
    PEST_MANAGEMENT = "pest_management"

class ChatRequest(BaseModel):
    message: str
    location: Optional[str] = "Central Ethiopia"
    crop_type: Optional[str] = "maize"
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    agent_type: AgentType
    response: str
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_breakdown: List[AgentResponse]
    follow_up_questions: List[str]

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str