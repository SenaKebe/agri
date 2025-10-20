from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Crop Advisor API",
    description="An intelligent agricultural advisory system with RAG and multi-agent architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter setup
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/day"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Crop Advisor API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Crop Advisor API",
        "rag_initialized": False
    }

# Import routers with error handling
try:
    from app.agents.orchestrator import router  # Ensure this matches your file structure
    app.include_router(router, prefix="/api/v1", tags=["AI Agents"])
    logger.info("✅ Agents router loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load agents router: {e}")

# Test imports endpoint
@app.get("/test-imports")
async def test_imports():
    imports_status = {}
    
    try:
        from app.rag.vector_store import vector_store
        imports_status["vector_store"] = "✅ OK"
    except Exception as e:
        imports_status["vector_store"] = f"❌ {e}"
    
    try:
        from app.rag.rag_manager import rag_manager
        imports_status["rag_manager"] = "✅ OK"
    except Exception as e:
        imports_status["rag_manager"] = f"❌ {e}"
        
    try:
        from app.agents.base import BaseAgent
        imports_status["base_agent"] = "✅ OK"
    except Exception as e:
        imports_status["base_agent"] = f"❌ {e}"
    
    try:
        from app.workflows.weather_alert import weather_alert
        imports_status["weather_alert"] = "✅ OK"
    except Exception as e:
        imports_status["weather_alert"] = f"❌ {e}"
    
    return imports_status

# System info endpoint
@app.get("/system/info")
async def system_info():
    try:
        from app.rag.rag_manager import rag_manager
        
        rag_status = rag_manager.get_knowledge_base_status()
        
        return {
            "system": "AI Crop Advisor",
            "version": "1.0.0",
            "components": {
                "fastapi": "running",
                "gemini_ai": "integrated",
                "rag_system": rag_status.get("status", "unknown"),
                "multi_agent": "active",
                "vector_database": "chromadb"
            },
            "rag_system": rag_status,
            "agents": ["agronomist", "weather_advisor", "orchestrator"],
            "supported_crops": ["maize", "beans", "wheat"],
            "supported_regions": ["Central Ethiopia", "Western Ethiopia", "Eastern Ethiopia", "Rift Valley"]
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system information")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)