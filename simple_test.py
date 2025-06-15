"""
Simple test to verify chat endpoint registration
"""
try:
    from fastapi import FastAPI
    
    app = FastAPI(title="Test", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "Simple test app"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "test": "simple"}
    
    @app.post("/chat")
    async def chat(request):
        return {"response": "Test response", "request_received": True}
    
    print("✅ Simple app created successfully")
    print(f"Routes: {len(app.routes)}")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {list(route.methods)} {route.path}")
            
except Exception as e:
    print(f"❌ Simple app failed: {e}")