#!/usr/bin/env python3
"""
Simple HTTP server with CORS support for Azure App Service
No dependencies required - uses only Python standard library
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class CORSHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
        print("✅ CORS preflight request handled")
    
    def do_GET(self):
        print(f"📡 GET request to: {self.path}")
        
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "healthy", 
                "service": "Advanced AI Agent",
                "version": "1.0.0",
                "cors": "enabled"
            }
            self.wfile.write(json.dumps(response).encode())
            print("✅ Health check response sent with CORS")
            
        elif self.path == '/' or self.path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers() 
            self.end_headers()
            
            response = {
                "message": "Advanced AI Agent is running!",
                "status": "healthy",
                "endpoints": ["/health", "/"],
                "cors": "enabled"
            }
            self.wfile.write(json.dumps(response).encode())
            print("✅ Root response sent with CORS")
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {"error": "Not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())

def main():
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting Advanced AI Agent server on port {port}")
    print(f"🌐 CORS enabled for all origins")
    print(f"📡 Endpoints available: /health, /")
    
    server = HTTPServer(('0.0.0.0', port), CORSHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Server stopped")
        server.server_close()

if __name__ == "__main__":
    main()