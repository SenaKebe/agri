from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import os
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, system_prompt: str, tools: Optional[List[Any]] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize Gemini LLM using official approach"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.3,
                max_tokens=1000,
                timeout=30
            )
            
            logger.info("Testing Gemini connection...")
            test_response = llm.invoke("Say 'TEST'")
            logger.info(f"Gemini test successful: {test_response.content}")
            
            return llm
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    async def generate_response(self, user_message: str, context: str = "") -> str:
        """Generate response using Gemini with proper error handling"""
        try:
            full_prompt = f"""You are: {self.system_prompt}

Context information:
{context}

User question: {user_message}

Please provide a helpful, accurate response based on the context and your expertise:"""
            
            logger.info(f"Sending request to Gemini for {self.name}")
            response = await self.llm.ainvoke([HumanMessage(content=full_prompt)])
            
            logger.info(f"Successfully received response from {self.name}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in {self.name} response generation: {str(e)}")
            return f"I apologize, but I encountered an issue while processing your request. Please try again in a moment."

    def to_crewai_agent(self):
        """Convert to CrewAI agent format"""
        from crewai import Agent
        
        return Agent(
            role=self.system_prompt.split('.')[0] if '.' in self.system_prompt else self.system_prompt,
            goal=f"Provide expert advice as {self.name}",
            backstory=self.system_prompt,
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )