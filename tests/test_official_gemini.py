import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def test_official_gemini():
    """Test using the official Google Generative AI package directly"""
    print("🧪 Testing Official Gemini API...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    try:
        # Configure the official client
        genai.configure(api_key=api_key)
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content("Say just 'OFFICIAL_WORKING' if this works.")
        
        print(f"✅ Official API Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Official API Error: {e}")
        return False

if __name__ == "__main__":
    test_official_gemini()