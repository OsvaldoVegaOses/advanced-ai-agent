"""
API v1 Routes - Main Router Configuration
Centralized routing for all API endpoints
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Import all route modules
from api.v1.conversation import router as conversation_router
from api.v1.agents import router as agents_router
from api.v1.business import router as business_router
from api.v1.integrations import router as integrations_router
from api.v1.analytics import router as analytics_router
from api.v1.admin import router as admin_router
from api.v1.auth import router as auth_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers with prefixes
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    conversation_router,
    prefix="/conversation",
    tags=["Conversation"]
)

api_router.include_router(
    agents_router,
    prefix="/agents",
    tags=["AI Agents"]
)

api_router.include_router(
    business_router,
    prefix="/business",
    tags=["Business Operations"]
)

api_router.include_router(
    integrations_router,
    prefix="/integrations",
    tags=["External Integrations"]
)

api_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics & Reporting"]
)

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Administration"]
)


@api_router.get("/")
async def api_root():
    """API root endpoint with available endpoints"""
    return {
        "message": "Advanced AI Agent API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "conversation": "/api/v1/conversation",
            "agents": "/api/v1/agents",
            "business": "/api/v1/business",
            "integrations": "/api/v1/integrations",
            "analytics": "/api/v1/analytics",
            "admin": "/api/v1/admin"
        },
        "documentation": "/docs"
    }


@api_router.get("/status")
async def api_status():
    """API status and health information"""
    from core.database import db_manager
    
    try:
        # Check database health
        db_health = await db_manager.health_check()
        
        # Check AI model status
        from core.ai.model_manager import model_manager
        model_status = await model_manager.get_status()
        
        overall_status = "healthy"
        if any(service["status"] != "healthy" for service in db_health.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": "2024-01-01T00:00:00Z",  # This would be dynamic
            "database": db_health,
            "ai_models": model_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )