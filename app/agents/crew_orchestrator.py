from crewai import Agent, Task, Crew
from langchain_core.messages import HumanMessage
from langchain.tools import tool  # Import LangChain tool decorator
from app.agents.base import BaseAgent
from app.workflows.weather_alert import RealWeatherWorkflow
from app.models.schemas import ChatRequest
from app.rag.rag_manager import rag_manager
from typing import Dict

# Initialize your existing components
weather_workflow = RealWeatherWorkflow()
base_llm = BaseAgent("Test", "Test prompt").llm

# Define a custom tool using LangChain's @tool decorator
@tool
def get_real_weather_data(location: str) -> str:
    """Fetches real-time weather data for a given location in Ethiopia.
    Args:
        location (str): The location in Ethiopia (e.g., 'Central Ethiopia').
    Returns:
        str: Weather data as a string.
    """
    return str(weather_workflow.get_real_weather_data(location))

# Define CrewAI agents using your system prompts
weather_agent = Agent(
    role="Weather Advisor",
    goal="Fetch real weather data and provide weather-based farming advice for Ethiopian maize farmers",
    backstory="You are an expert in Ethiopian weather patterns and how they affect maize cultivation.",
    llm=base_llm,
    tools=[get_real_weather_data],  # Pass the decorated tool
    allow_tools=True
)

agronomist_agent = Agent(
    role="Agronomist Expert",
    goal="Provide maize-specific recommendations, incorporating weather data and RAG context",
    backstory="You specialize in maize farming in Ethiopia, focusing on pests, soil, and irrigation.",
    llm=base_llm
)

# Define tasks with delegation
weather_task = Task(
    description="Get current weather for {location} and analyze risks for maize farming.",
    agent=weather_agent,
    expected_output="Weather summary, risks, and basic advice."
)

advice_task = Task(
    description="Using {weather_summary} and RAG context, give actionable maize advice for {location}.",
    agent=agronomist_agent,
    context=[weather_task],
    expected_output="Cohesive agricultural recommendations."
)

# Create the crew (orchestration)
crew = Crew(
    agents=[weather_agent, agronomist_agent],
    tasks=[weather_task, advice_task],
    verbose=True
)

# Usage in your router (/chat endpoint)
async def chat_with_advisor(request: ChatRequest) -> Dict:
    location = request.location or "Central Ethiopia"
    crop_type = request.crop_type or "maize"
    rag_context = rag_manager.get_agricultural_context(request.message) or "No additional context available"
    inputs = {
        "location": location,
        "weather_summary": rag_context,
        "crop_type": crop_type
    }
    result = crew.kickoff(inputs=inputs)
    return {
        "response": result,
        "weather_data": getattr(weather_agent, "last_output", "No weather data available"),
        "agronomist_advice": getattr(advice_task, "last_output", "No agronomist advice available")
    }
    