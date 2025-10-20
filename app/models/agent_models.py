from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentType(str, Enum):
    WEATHER_ADVISOR = "weather_advisor"
    AGRONOMIST = "agronomist"
    ORCHESTRATOR = "orchestrator"

class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    model: str = "gemini-2.5-flash"

class AgentResponse(BaseModel):
    agent: str
    response: str
    confidence: Optional[float] = None