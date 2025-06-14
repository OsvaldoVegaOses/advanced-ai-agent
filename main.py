"""
Advanced AI Agent - Main Application Entry Point
FastAPI application with comprehensive business automation capabilities
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from core.config import settings
from core.database import init_db
from core.exceptions import AgentException
from core.logging import setup_logging
from api.v1.routes import api_router
from services.health import health_router


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Advanced AI Agent...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI models and caches
    from core.ai.model_manager import ModelManager
    model_manager = ModelManager()
    await model_manager.initialize()
    
    # Initialize vector databases
    from core.memory.vector_store import VectorStoreManager
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    # Start background tasks
    from services.automation.scheduler import start_scheduler
    scheduler_task = asyncio.create_task(start_scheduler())
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Advanced AI Agent...")
    
    # Cancel background tasks
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    
    # Cleanup resources
    await model_manager.cleanup()
    await vector_manager.cleanup()
    
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Advanced AI Agent",
    description="Enterprise Conversational AI Platform with Business Automation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Prometheus metrics (optional)
if PROMETHEUS_AVAILABLE:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
    logger.info("Prometheus metrics enabled")
else:
    logger.warning("Prometheus metrics not available - continuing without monitoring")


# Exception handlers
@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    """Handle custom agent exceptions"""
    logger.error(f"Agent exception: {exc.detail}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.detail,
            "type": "agent_error"
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal error occurred",
            "type": "server_error"
        }
    )


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with basic information"""
    return {
        "name": "Advanced AI Agent",
        "version": "1.0.0",
        "status": "operational",
        "description": "Enterprise Conversational AI Platform",
        "docs": "/docs" if settings.DEBUG else "Contact admin for API documentation",
        "capabilities": [
            "Multi-agent conversation",
            "Multimodal processing",
            "Business automation",
            "CRM integration",
            "Real-time analytics"
        ]
    }


# Metrics endpoint
@app.get("/metrics/summary")
async def metrics_summary() -> Dict[str, Any]:
    """Application metrics summary"""
    from services.analytics.metrics_collector import MetricsCollector
    
    collector = MetricsCollector()
    return await collector.get_summary_metrics()


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info",
        access_log=True
    )