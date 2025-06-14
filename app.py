"""
Advanced AI Agent - Production Backend
Integrated with Azure OpenAI and full enterprise features
"""
import asyncio
import os
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add core module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

try:
    from fastapi import FastAPI, HTTPException, Request, Depends
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    
    # Import core modules with fallback
    try:
        from core.config import settings
        from core.ai.model_manager import model_manager, ModelType
        FULL_AI_AVAILABLE = True
    except ImportError as e:
        print(f"Full AI modules not available: {e}")
        try:
            from simple_config import settings
            from openai import AsyncAzureOpenAI
            SIMPLE_AI_AVAILABLE = True
        except ImportError:
            SIMPLE_AI_AVAILABLE = False
        FULL_AI_AVAILABLE = False
        
except ImportError:
    print("FastAPI not available, using basic fallback")
    FULL_AI_AVAILABLE = False
    SIMPLE_AI_AVAILABLE = False


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(default=None)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: str = Field(default="default", description="Conversation ID")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)
    stream: Optional[bool] = Field(default=False)

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: str = Field(..., description="Response timestamp")
    model_used: Optional[str] = Field(default=None)
    tokens_used: Optional[int] = Field(default=None)
    processing_time_ms: Optional[float] = Field(default=None)

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    ai_models: Optional[Dict[str, Any]] = Field(default=None)
    uptime_seconds: Optional[float] = Field(default=None)

class ConversationInfo(BaseModel):
    id: str
    title: str
    last_message: str
    message_count: int
    created_at: str
    updated_at: str


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

# Track application start time
app_start_time = datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting Advanced AI Agent...")
    
    if FULL_AI_AVAILABLE:
        try:
            await model_manager.initialize()
            print("✅ AI Model Manager initialized successfully")
        except Exception as e:
            print(f"⚠️ AI initialization failed: {e}")
    elif SIMPLE_AI_AVAILABLE:
        print("✅ Simple Azure OpenAI client available")
    else:
        print("⚠️ Running in fallback mode (AI features limited)")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Advanced AI Agent...")
    if FULL_AI_AVAILABLE:
        try:
            await model_manager.cleanup()
            print("✅ AI cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="Advanced AI Agent",
    description="Enterprise AI Agent with Azure OpenAI integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://delightful-coast-07a54bc1e.1.azurestaticapps.net",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Trusted Host Middleware (in production)
if FULL_AI_AVAILABLE and hasattr(settings, 'ALLOWED_HOSTS'):
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# =============================================================================
# CONVERSATION STORAGE (In-Memory for demo)
# =============================================================================

conversations: Dict[str, List[ChatMessage]] = {}
conversation_metadata: Dict[str, ConversationInfo] = {}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_conversation_title(messages: List[ChatMessage]) -> str:
    """Generate conversation title from first message"""
    if messages:
        first_msg = messages[0].content[:50]
        return first_msg + "..." if len(first_msg) >= 50 else first_msg
    return "Nueva conversación"

def get_conversation(conversation_id: str) -> List[ChatMessage]:
    """Get conversation messages"""
    if conversation_id not in conversations:
        conversations[conversation_id] = []
        conversation_metadata[conversation_id] = ConversationInfo(
            id=conversation_id,
            title="Nueva conversación",
            last_message="",
            message_count=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    return conversations[conversation_id]

def add_message_to_conversation(conversation_id: str, message: ChatMessage):
    """Add message to conversation"""
    conversation = get_conversation(conversation_id)
    message.timestamp = datetime.now().isoformat()
    conversation.append(message)
    
    # Update metadata
    metadata = conversation_metadata[conversation_id]
    metadata.last_message = message.content[:100]
    metadata.message_count = len(conversation)
    metadata.updated_at = message.timestamp
    
    if metadata.title == "Nueva conversación" and len(conversation) >= 2:
        metadata.title = get_conversation_title(conversation)

async def generate_ai_response_advanced(messages: List[ChatMessage], 
                                      temperature: float = 0.7,
                                      max_tokens: int = 1000) -> Dict[str, Any]:
    """Generate AI response using Azure OpenAI"""
    # Try full AI system first
    if FULL_AI_AVAILABLE and model_manager.initialized:
        try:
            # Convert to OpenAI format
            openai_messages = []
            for msg in messages[-10:]:  # Keep last 10 messages for context
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add system message for context
            system_message = {
                "role": "system",
                "content": """Eres un Advanced AI Agent profesional y útil desplegado en Azure.

Características de tu personalidad:
- Profesional pero amigable
- Conocimiento técnico especializado en desarrollo web, Azure, y tecnología
- Respuestas concisas pero informativas
- Siempre dispuesto a ayudar

Contexto del sistema:
- Estás ejecutándose en Azure App Services
- Usas Azure OpenAI con modelos GPT-4o Mini
- Frontend desplegado en Azure Static Web Apps
- Sistema completamente operacional y escalable

Instrucciones:
- Responde de manera útil y precisa
- Si no sabes algo, admítelo honestamente
- Mantén un tono profesional pero accesible
- Puedes ayudar con desarrollo, tecnología, Azure, negocios y temas generales"""
            }
            
            openai_messages.insert(0, system_message)
            
            # Generate response using model manager
            response = await model_manager.chat_completion(
                messages=openai_messages,
                model_type=ModelType.CHAT,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response["content"],
                "model_used": response["model"],
                "tokens_used": response["usage"]["total_tokens"],
                "processing_time_ms": response["processing_time"] * 1000
            }
            
        except Exception as e:
            print(f"Full AI generation error: {e}")
    
    # Try simple Azure OpenAI client
    if SIMPLE_AI_AVAILABLE and settings.has_azure_openai():
        try:
            return await generate_simple_ai_response(messages, temperature, max_tokens)
        except Exception as e:
            print(f"Simple AI generation error: {e}")
    
    # Fallback to mock responses
    return await generate_fallback_response(messages[-1].content if messages else "")

async def generate_simple_ai_response(messages: List[ChatMessage], 
                                    temperature: float = 0.7,
                                    max_tokens: int = 1000) -> Dict[str, Any]:
    """Generate AI response using simple Azure OpenAI client"""
    import time
    start_time = time.time()
    
    # Create simple client
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_VERSION
    )
    
    # Convert to OpenAI format
    openai_messages = []
    for msg in messages[-10:]:  # Keep last 10 messages for context
        openai_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add system message
    system_message = {
        "role": "system",
        "content": """Eres un Advanced AI Agent profesional desplegado en Azure.
        
Responde de manera útil, concisa y profesional. Puedes ayudar con desarrollo web, tecnología, Azure, consultas de negocio y temas generales."""
    }
    
    openai_messages.insert(0, system_message)
    
    # Generate response
    response = await client.chat.completions.create(
        model=settings.AZURE_CHAT_DEPLOYMENT,
        messages=openai_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    processing_time = time.time() - start_time
    content = response.choices[0].message.content
    
    return {
        "content": content,
        "model_used": f"azure_{settings.AZURE_CHAT_DEPLOYMENT}",
        "tokens_used": response.usage.total_tokens if response.usage else None,
        "processing_time_ms": processing_time * 1000
    }

async def generate_fallback_response(user_message: str) -> Dict[str, Any]:
    """Generate fallback response when AI is not available"""
    await asyncio.sleep(0.5)  # Simulate processing
    
    msg_lower = user_message.lower()
    
    responses = {
        "hola|hello|hi": "¡Hola! 👋 Soy tu Advanced AI Agent. Estoy funcionando en Azure y listo para ayudarte. ¿En qué puedo asistirte?",
        "cómo estás|how are you": "¡Estoy funcionando perfectamente! 🚀 Mi backend está desplegado en Azure App Services con Azure OpenAI. Todo el sistema está operativo al 100%.",
        "azure|cloud": "¡Perfecto! Estoy desplegado en Azure Cloud usando App Services para el backend y Static Web Apps para el frontend. El sistema está optimizado y escalable. 💙☁️",
        "ayuda|help": "¡Por supuesto! Puedo ayudarte con desarrollo web, tecnología, Azure, consultas de negocio y muchos otros temas. ¿Qué necesitas? 🤝",
        "desarrollo|programming|código": "¡Excelente! Tengo experiencia en desarrollo web, APIs, bases de datos, deployment en cloud, y muchas tecnologías. ¿En qué proyecto estás trabajando? 💻",
        "gracias|thank": "¡De nada! 😊 Es un placer ayudarte. Si tienes más preguntas o necesitas asistencia adicional, estaré aquí.",
        "precio|cost|presupuesto": "Para consultas de presupuesto y servicios personalizados, puedo ayudarte a evaluar tus necesidades y sugerir soluciones. ¿Podrías contarme más sobre tu proyecto? 💰",
        "tiempo|cuando|deadline": "Puedo ayudarte a estimar tiempos de desarrollo según la complejidad del proyecto. ¿Qué tipo de aplicación o servicio necesitas? ⏰"
    }
    
    # Find matching response
    for patterns, response in responses.items():
        if any(pattern in msg_lower for pattern in patterns.split("|")):
            return {
                "content": response,
                "model_used": "fallback_system",
                "tokens_used": None,
                "processing_time_ms": 500
            }
    
    # Default response
    return {
        "content": f'Entiendo que me preguntas sobre: "{user_message}". Como Advanced AI Agent, estoy aquí para ayudarte con desarrollo, tecnología, Azure, consultas de negocio y muchos otros temas. ¿Podrías ser más específico sobre lo que necesitas? 🤖💭',
        "model_used": "fallback_system", 
        "tokens_used": None,
        "processing_time_ms": 500
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle all OPTIONS requests for CORS preflight"""
    return {}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Advanced AI Agent is running!",
        "status": "healthy",
        "version": "1.0.0",
        "ai_enabled": str(FULL_AI_AVAILABLE or SIMPLE_AI_AVAILABLE)
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    health_data = {
        "status": "healthy",
        "service": "Advanced AI Agent",
        "version": "1.0.0",
        "uptime_seconds": uptime
    }
    
    # Add AI model status if available
    if FULL_AI_AVAILABLE and model_manager.initialized:
        try:
            ai_status = await model_manager.get_status()
            health_data["ai_models"] = ai_status
        except Exception as e:
            health_data["ai_models"] = {"error": str(e)}
    elif SIMPLE_AI_AVAILABLE:
        health_data["ai_models"] = {"status": "simple_mode", "azure_openai": "available"}
    else:
        health_data["ai_models"] = {"status": "fallback_mode", "reason": "AI modules not available"}
    
    return health_data

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with Azure OpenAI integration"""
    try:
        # Get conversation
        conversation = get_conversation(request.conversation_id)
        
        # Add user message
        user_message = ChatMessage(role="user", content=request.message)
        add_message_to_conversation(request.conversation_id, user_message)
        
        # Generate AI response
        ai_result = await generate_ai_response_advanced(
            conversation,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Add AI response to conversation
        ai_message = ChatMessage(role="assistant", content=ai_result["content"])
        add_message_to_conversation(request.conversation_id, ai_message)
        
        # Return response
        return ChatResponse(
            response=ai_result["content"],
            conversation_id=request.conversation_id,
            timestamp=ai_message.timestamp,
            model_used=ai_result.get("model_used"),
            tokens_used=ai_result.get("tokens_used"),
            processing_time_ms=ai_result.get("processing_time_ms")
        )
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.get("/conversations", response_model=Dict[str, List[ConversationInfo]])
async def get_conversations():
    """Get all conversation metadata"""
    return {
        "conversations": list(conversation_metadata.values())
    }

@app.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_detail(conversation_id: str):
    """Get detailed conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = conversations[conversation_id]
    metadata = conversation_metadata[conversation_id]
    
    return {
        "metadata": metadata,
        "messages": messages
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del conversations[conversation_id]
    del conversation_metadata[conversation_id]
    
    return {"message": "Conversation deleted successfully"}

@app.get("/status", response_model=Dict[str, Any])
async def detailed_status():
    """Detailed system status"""
    status = {
        "service": "Advanced AI Agent",
        "version": "1.0.0",
        "uptime_seconds": (datetime.now() - app_start_time).total_seconds(),
        "ai_enabled": FULL_AI_AVAILABLE or SIMPLE_AI_AVAILABLE,
        "total_conversations": len(conversations),
        "total_messages": sum(len(conv) for conv in conversations.values()),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "azure_deployment": True
    }
    
    if FULL_AI_AVAILABLE and model_manager.initialized:
        try:
            status["ai_models"] = await model_manager.get_status()
        except Exception as e:
            status["ai_error"] = str(e)
    
    return status


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    print(f"Unhandled exception: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Advanced AI Agent in development mode...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )