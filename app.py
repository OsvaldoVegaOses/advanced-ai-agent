"""
Simple FastAPI application for Azure deployment testing
"""
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import json
    import asyncio
except ImportError:
    # Fallback for environments without FastAPI
    print("FastAPI not available, using basic web server")
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({
                    "status": "healthy",
                    "service": "Advanced AI Agent",
                    "version": "1.0.0"
                })
                self.wfile.write(response.encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({
                    "message": "Advanced AI Agent is running!",
                    "status": "healthy"
                })
                self.wfile.write(response.encode())
    
    if __name__ == "__main__":
        server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
        server.serve_forever()

app = FastAPI(title="Advanced AI Agent", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for immediate fix
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Advanced AI Agent is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "Advanced AI Agent",
            "version": "1.0.0"
        }
    )

# Request model for chat
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

# Response model for chat
class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Simple chat endpoint that simulates AI responses
    In production, this would integrate with Azure OpenAI
    """
    try:
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Simple response logic (replace with Azure OpenAI integration)
        user_message = request.message.lower()
        
        if "hola" in user_message or "hello" in user_message:
            ai_response = "¡Hola! Soy tu Advanced AI Agent. ¿En qué puedo ayudarte hoy?"
        elif "cómo estás" in user_message or "how are you" in user_message:
            ai_response = "¡Estoy funcionando perfectamente en Azure! Listo para ayudarte con cualquier consulta."
        elif "tiempo" in user_message or "weather" in user_message:
            ai_response = "No tengo acceso a datos meteorológicos en tiempo real, pero puedo ayudarte con muchas otras consultas."
        elif "azure" in user_message:
            ai_response = "¡Perfecto! Estoy desplegado en Azure usando App Services y Static Web Apps. El sistema está funcionando al 100%."
        elif "gracias" in user_message or "thank" in user_message:
            ai_response = "¡De nada! Siempre es un placer ayudar. ¿Hay algo más en lo que pueda asistirte?"
        else:
            ai_response = f"Entiendo que me preguntas sobre: '{request.message}'. Como agente de IA, estoy aquí para ayudarte. ¿Podrías darme más detalles sobre lo que necesitas?"
        
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        
        return ChatResponse(
            response=ai_response,
            conversation_id=request.conversation_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/conversations")
async def get_conversations():
    """
    Endpoint to get conversation history (simplified for demo)
    """
    return {
        "conversations": [
            {
                "id": "default",
                "title": "Conversación Principal",
                "last_message": "Sistema listo para chat",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)