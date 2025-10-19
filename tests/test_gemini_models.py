import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import asyncio

load_dotenv()

async def test_gemini_models():
    """Test different Gemini model names to find which works"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    model_names = [
        "gemini-1.5-flash"
    ]
    
    for model_name in model_names:
        print(f"\n🧪 Testing model: {model_name}")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.1,
                max_tokens=100
            )
            
            # Simple test
            response = await llm.ainvoke([HumanMessage(content="Say just 'WORKING' if you can hear me.")])
            print(f"   ✅ SUCCESS: {response.content}")
            print(f"   🎯 This model works: {model_name}")
            return model_name
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
    
    print("\n❌ No Gemini models worked. Please check your API key and region.")
    return None

if __name__ == "__main__":
    working_model = asyncio.run(test_gemini_models())
    if working_model:
        print(f"\n🎯 Use this model in your code: '{working_model}'")