from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentType(str, Enum):
    AGRONOMIST = "agronomist"
    WEATHER_ADVISOR = "weather_advisor"
    ORCHESTRATOR = "orchestrator"

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question or message")
    conversation_id: Optional[str] = Field(None, description="Unique conversation ID")
    location: Optional[str] = Field(None, description="User's location (e.g., 'Central Kenya')")
    crop_type: Optional[str] = Field("maize", description="Type of crop")

class AgentResponse(BaseModel):
    agent_type: AgentType
    response: str
    confidence: float = Field(..., ge=0, le=1)
    sources: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_breakdown: List[AgentResponse]
    follow_up_questions: Optional[List[str]] = None

class RAGDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    source: str

class WeatherRequest(BaseModel):
    location: str
    days: int = Field(7, ge=1, le=14)