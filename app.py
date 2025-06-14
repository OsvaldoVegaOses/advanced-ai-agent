"""
Simple FastAPI application for Azure deployment testing
"""
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)