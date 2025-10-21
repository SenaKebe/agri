import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", 7860)),
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
    