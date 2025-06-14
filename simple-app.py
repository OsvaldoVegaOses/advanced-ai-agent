#!/usr/bin/env python3
"""
Simple test application for Azure App Service
This file will be deployed to test the basic functionality
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {
        "message": "🚀 Advanced AI Agent is running!",
        "status": "healthy",
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "azure_openai_endpoint": os.getenv('AZURE_OPENAI_ENDPOINT', 'not configured'),
        "version": "1.0.0"
    }

@app.route('/health')
def health():
    return {"status": "healthy", "message": "App Service is running"}

@app.route('/health/live')
def health_live():
    return {"status": "healthy", "timestamp": "2025-06-14"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)