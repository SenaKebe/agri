import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_rag_system():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing RAG System...")
    
    try:
        # Check RAG status
        status_response = requests.get(f"{base_url}/api/v1/rag/status")
        print("📊 RAG Status:", status_response.json())
        
        # Initialize RAG knowledge base
        print("\n🔄 Initializing RAG Knowledge Base...")
        init_response = requests.post(f"{base_url}/api/v1/rag/initialize")
        print("RAG Initialization:", init_response.json())
        
        # Check status again
        status_after = requests.get(f"{base_url}/api/v1/rag/status")
        print("📊 RAG Status After Initialization:", status_after.json())
        
        # Test RAG-enhanced questions
        test_questions = [
            "When should I plant maize in Central Ethiopia?",
            "How do I control maize stalk borer?",
            "What fertilizer should I use for maize?",
            "How to manage fall armyworm in my maize farm?"
        ]
        
        for question in test_questions:
            print(f"\n🌱 Testing: {question}")
            chat_data = {
                "message": question,
                "location": "Central Ethiopia",
                "crop_type": "maize"
            }
            response = requests.post(f"{base_url}/api/v1/chat", json=chat_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:150]}...")
                if data['agent_breakdown']:
                    sources = data['agent_breakdown'][0].get('sources', [])
                    print(f"📚 Sources: {[s.get('name', 'AI Model') for s in sources]}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")

if __name__ == "__main__":
    test_rag_system()