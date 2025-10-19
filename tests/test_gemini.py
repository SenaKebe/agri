import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import asyncio

load_dotenv()

async def test_gemini_directly():
    """Test Gemini API directly"""
    print("🧪 Testing Gemini API directly...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        # Simple test message
        messages = [HumanMessage(content="Hello, are you working? Respond with 'YES' if working.")]
        response = await llm.ainvoke(messages)
        
        print(f"✅ Gemini Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini_directly())