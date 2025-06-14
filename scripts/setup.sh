#!/bin/bash

# Advanced AI Agent Setup Script
# This script sets up the development environment

set -e

echo "🔧 Setting up Advanced AI Agent Development Environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy

# Download spaCy models
echo "🧠 Downloading spaCy models..."
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p static
mkdir -p media
mkdir -p data
mkdir -p tests

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Set executable permissions
chmod +x scripts/*.sh

# Install pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Installing pre-commit hooks..."
    pre-commit install
fi

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Azure OpenAI credentials"
echo "2. Start Docker services: docker-compose up -d"
echo "3. Run the application: ./scripts/start.sh dev"
echo ""
echo "🔗 Useful commands:"
echo "  - Start development: ./scripts/start.sh dev"
echo "  - Run tests: pytest"
echo "  - Format code: black . && isort ."
echo "  - Check types: mypy ."