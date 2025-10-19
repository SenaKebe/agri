import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

def test_fix():
    base_url = "http://localhost:8000"
    
    print("🔧 Testing the fix...")
    
    try:
        # Test basic health
        print("1. Testing health endpoint...")
        health = requests.get(f"{base_url}/health")
        print(f"   Health: {health.json()}")
        
        # Test imports
        print("2. Testing imports...")
        imports = requests.get(f"{base_url}/test-imports")
        print(f"   Imports: {imports.json()}")
        
        # Test RAG status (should work now)
        print("3. Testing RAG status...")
        rag_status = requests.get(f"{base_url}/api/v1/rag/status")
        print(f"   RAG Status: {rag_status.json()}")
        
        # Initialize RAG
        print("4. Initializing RAG...")
        init_response = requests.post(f"{base_url}/api/v1/rag/initialize")
        print(f"   Init Response: {init_response.json()}")
        
        # Check status again
        print("5. Checking RAG status after initialization...")
        rag_status_after = requests.get(f"{base_url}/api/v1/rag/status")
        print(f"   RAG Status After: {rag_status_after.json()}")
        
        # Test a simple chat
        print("6. Testing chat with RAG...")
        chat_data = {
            "message": "When to plant maize in Kenya?",
            "location": "Central Kenya",
            "crop_type": "maize"
        }
        chat_response = requests.post(f"{base_url}/api/v1/chat", json=chat_data)
        if chat_response.status_code == 200:
            data = chat_response.json()
            print(f"   ✅ Chat successful!")
            print(f"   Response preview: {data['response'][:100]}...")
        else:
            print(f"   ❌ Chat failed: {chat_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fix()