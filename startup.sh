#!/bin/bash

# Azure App Service startup script for Advanced AI Agent
# This script handles the initialization and startup of the FastAPI application

echo "🚀 Starting Advanced AI Agent on Azure App Service..."

# Set environment variables for Azure
export ENVIRONMENT="production"
export DEBUG="False"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Install production dependencies if needed
if [ ! -d "/home/site/wwwroot/.venv" ]; then
    echo "📦 Installing Python dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
fi

# Download spaCy models
echo "📥 Downloading spaCy models..."
python -m spacy download es_core_news_sm || echo "Spanish model not available, continuing..."
python -m spacy download en_core_web_sm || echo "English model not available, continuing..."

# Create necessary directories
mkdir -p /home/site/wwwroot/static
mkdir -p /home/site/wwwroot/logs

# Run database migrations if needed
echo "🗃️ Running database migrations..."
python -c "
try:
    from core.database import init_db
    import asyncio
    asyncio.run(init_db())
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️ Database initialization skipped: {e}')
"

# Start the application
echo "🎯 Starting FastAPI application..."
exec gunicorn main:app \
    --bind 0.0.0.0:${PORT:-8000} \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --keep-alive 65 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload