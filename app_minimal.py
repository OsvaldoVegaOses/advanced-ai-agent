"""
Minimal Advanced AI Agent - Production Backend
Simplified version to ensure chat endpoint registers
"""
import asyncio
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

# Try to import FastAPI and related modules
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI not available: {e}")
    FASTAPI_AVAILABLE = False

# Try to import OpenAI
try:
    from openai import AsyncAzureOpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI imported successfully")
except ImportError as e:
    print(f"❌ OpenAI not available: {e}")
    OPENAI_AVAILABLE = False

# Application start time
app_start_time = datetime.now()

# Pydantic models (only if available)
if FASTAPI_AVAILABLE:
    class ChatMessage(BaseModel):
        role: str
        content: str
        timestamp: Optional[str] = None

    class ChatRequest(BaseModel):
        message: str
        conversation_id: str = "default"
        temperature: Optional[float] = 0.7
        max_tokens: Optional[int] = 1000

    class ChatResponse(BaseModel):
        response: str
        conversation_id: str
        timestamp: str
        model_used: Optional[str] = None

# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Advanced AI Agent",
        description="Minimal version for testing",
        version="1.0.0"
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # In-memory storage
    conversations: Dict[str, List[Dict]] = {}
    
    @app.get("/")
    async def root():
        return {
            "message": "Advanced AI Agent - Minimal Version",
            "status": "healthy",
            "version": "1.0.0-minimal",
            "fastapi_available": FASTAPI_AVAILABLE,
            "openai_available": OPENAI_AVAILABLE
        }
    
    @app.get("/health")
    async def health_check():
        uptime = (datetime.now() - app_start_time).total_seconds()
        return {
            "status": "healthy",
            "service": "Advanced AI Agent",
            "version": "1.0.0-minimal",
            "uptime_seconds": uptime,
            "fastapi_available": FASTAPI_AVAILABLE,
            "openai_available": OPENAI_AVAILABLE
        }
    
    @app.post("/chat")
    async def chat_endpoint(request: ChatRequest):
        """Simplified chat endpoint"""
        try:
            # Store user message
            conversation_id = request.conversation_id
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            
            user_message = {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat()
            }
            conversations[conversation_id].append(user_message)
            
            # Generate response (fallback mode)
            ai_response = f"Echo: {request.message} [Minimal mode - {datetime.now().strftime('%H:%M:%S')}]"
            
            ai_message = {
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            }
            conversations[conversation_id].append(ai_message)
            
            return ChatResponse(
                response=ai_response,
                conversation_id=conversation_id,
                timestamp=ai_message["timestamp"],
                model_used="minimal_fallback"
            )
            
        except Exception as e:
            print(f"Chat error: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Chat error: {str(e)}"
            )
    
    @app.get("/debug")
    async def debug_info():
        return {
            "service": "Advanced AI Agent - Minimal",
            "fastapi_available": FASTAPI_AVAILABLE,
            "openai_available": OPENAI_AVAILABLE,
            "total_conversations": len(conversations),
            "python_version": sys.version,
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "registered_routes": [
                {"methods": list(route.methods), "path": route.path} 
                for route in app.routes 
                if hasattr(route, 'methods') and hasattr(route, 'path')
            ]
        }
    
    print("✅ Minimal FastAPI app created with all endpoints")
    print(f"Registered routes: {len(app.routes)}")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {list(route.methods)} {route.path}")

else:
    # Fallback when FastAPI is not available
    print("⚠️ Creating fallback app")
    class FallbackApp:
        def __init__(self):
            self.name = "Fallback App"
    
    app = FallbackApp()

# Development server
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting minimal Advanced AI Agent...")
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )