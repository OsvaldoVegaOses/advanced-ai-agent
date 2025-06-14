#!/bin/bash

echo "🚀 Starting Simple App for Advanced AI Agent..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-simple.txt

# Start the application
echo "🎯 Starting Flask application..."
exec gunicorn simple-app:app \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -