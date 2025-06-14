#!/bin/bash

# Advanced AI Agent Startup Script
# This script initializes and starts the AI Agent application

set -e

echo "🚀 Starting Advanced AI Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration before proceeding."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy models
echo "🧠 Downloading NLP models..."
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# Check database connection
echo "🔍 Checking database connection..."
python -c "
import asyncio
from core.database import test_database_connection, test_redis_connection

async def test_connections():
    try:
        await test_database_connection()
        await test_redis_connection()
        print('✅ Database connections successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)

asyncio.run(test_connections())
"

# Run database migrations (placeholder)
echo "🗄️  Running database migrations..."
# python manage.py migrate

# Start the application
echo "🎯 Starting application..."
if [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
elif [ "$1" = "prod" ]; then
    echo "🏭 Starting in production mode..."
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
    echo "📖 Usage: ./scripts/start.sh [dev|prod]"
    echo "   dev  - Development mode with auto-reload"
    echo "   prod - Production mode with Gunicorn"
    exit 1
fi