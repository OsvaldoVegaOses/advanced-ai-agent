"""
Health Check Service
Comprehensive system health monitoring and reporting
"""

import asyncio
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import db_manager, cache_manager
from core.logging import get_logger

logger = get_logger(__name__)

health_router = APIRouter()


class HealthChecker:
    """Comprehensive health checking service"""
    
    def __init__(self):
        self.logger = get_logger("health")
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            health_data = await db_manager.health_check()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy" if all(
                    service["status"] == "healthy" 
                    for service in health_data.values()
                ) else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "details": health_data
            }
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None
            }
    
    async def check_ai_models(self) -> Dict[str, Any]:
        """Check AI model availability and performance"""
        try:
            from core.ai.model_manager import model_manager
            
            start_time = time.time()
            model_status = await model_manager.get_status()
            response_time = (time.time() - start_time) * 1000
            
            all_healthy = all(
                model.get("status") == "ready" 
                for model in model_status.values()
            )
            
            return {
                "status": "healthy" if all_healthy else "degraded",
                "response_time_ms": round(response_time, 2),
                "models": model_status
            }
        except Exception as e:
            self.logger.error(f"AI models health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None
            }
    
    async def check_external_integrations(self) -> Dict[str, Any]:
        """Check external service integrations"""
        integration_status = {}
        overall_status = "healthy"
        
        # Check enabled integrations
        enabled_integrations = settings.integrations_enabled
        
        for service, enabled in enabled_integrations.items():
            if not enabled:
                integration_status[service] = {
                    "status": "disabled",
                    "enabled": False
                }
                continue
            
            try:
                # Perform basic connectivity check for each service
                start_time = time.time()
                
                if service == "sendgrid":
                    status = await self._check_sendgrid()
                elif service == "twilio":
                    status = await self._check_twilio()
                elif service == "hubspot":
                    status = await self._check_hubspot()
                elif service == "stripe":
                    status = await self._check_stripe()
                else:
                    status = {"status": "unknown", "message": "No health check implemented"}
                
                response_time = (time.time() - start_time) * 1000
                
                integration_status[service] = {
                    **status,
                    "enabled": True,
                    "response_time_ms": round(response_time, 2)
                }
                
                if status["status"] != "healthy":
                    overall_status = "degraded"
                    
            except Exception as e:
                integration_status[service] = {
                    "status": "unhealthy",
                    "enabled": True,
                    "error": str(e)
                }
                overall_status = "degraded"
        
        return {
            "status": overall_status,
            "integrations": integration_status
        }
    
    async def _check_sendgrid(self) -> Dict[str, Any]:
        """Check SendGrid API connectivity"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.sendgrid.com/v3/user/profile",
                    headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {"status": "healthy"}
                else:
                    return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def _check_twilio(self) -> Dict[str, Any]:
        """Check Twilio API connectivity"""
        try:
            import httpx
            import base64
            
            auth_string = base64.b64encode(
                f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()
            ).decode()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}.json",
                    headers={"Authorization": f"Basic {auth_string}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {"status": "healthy"}
                else:
                    return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def _check_hubspot(self) -> Dict[str, Any]:
        """Check HubSpot API connectivity"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.hubapi.com/contacts/v1/lists/all/contacts/all",
                    headers={"Authorization": f"Bearer {settings.HUBSPOT_API_KEY}"},
                    params={"count": 1},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {"status": "healthy"}
                else:
                    return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def _check_stripe(self) -> Dict[str, Any]:
        """Check Stripe API connectivity"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.stripe.com/v1/customers",
                    headers={"Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}"},
                    params={"limit": 1},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {"status": "healthy"}
                else:
                    return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine overall status
            status = "healthy"
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = "critical"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 70:
                status = "warning"
            
            return {
                "status": status,
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "disk_percent": round(disk_percent, 2),
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "available_disk_gb": round(disk.free / (1024**3), 2)
            }
        except Exception as e:
            self.logger.error(f"System resources check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        # Run all health checks concurrently
        database_task = asyncio.create_task(self.check_database())
        ai_models_task = asyncio.create_task(self.check_ai_models())
        integrations_task = asyncio.create_task(self.check_external_integrations())
        resources_task = asyncio.create_task(self.check_system_resources())
        
        # Wait for all checks to complete
        database_health = await database_task
        ai_models_health = await ai_models_task
        integrations_health = await integrations_task
        resources_health = await resources_task
        
        total_time = (time.time() - start_time) * 1000
        
        # Determine overall status
        statuses = [
            database_health["status"],
            ai_models_health["status"],
            integrations_health["status"],
            resources_health["status"]
        ]
        
        if "unhealthy" in statuses or "critical" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses or "warning" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "response_time_ms": round(total_time, 2),
            "components": {
                "database": database_health,
                "ai_models": ai_models_health,
                "integrations": integrations_health,
                "system_resources": resources_health
            },
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }


# Initialize health checker
health_checker = HealthChecker()


@health_router.get("/")
async def basic_health():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}


@health_router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": time.time()}


@health_router.get("/detailed")
async def detailed_health():
    """Detailed health check with all components"""
    try:
        health_data = await health_checker.comprehensive_health_check()
        
        status_code = 200
        if health_data["status"] == "unhealthy":
            status_code = 503
        elif health_data["status"] == "degraded":
            status_code = 200  # Still operational but with issues
        
        return JSONResponse(
            content=health_data,
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            },
            status_code=503
        )


@health_router.get("/database")
async def database_health():
    """Database-specific health check"""
    health_data = await health_checker.check_database()
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return JSONResponse(content=health_data, status_code=status_code)


@health_router.get("/ai-models")
async def ai_models_health():
    """AI models health check"""
    health_data = await health_checker.check_ai_models()
    status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
    
    return JSONResponse(content=health_data, status_code=status_code)


@health_router.get("/integrations")
async def integrations_health():
    """External integrations health check"""
    health_data = await health_checker.check_external_integrations()
    status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
    
    return JSONResponse(content=health_data, status_code=status_code)


@health_router.get("/resources")
async def system_resources_health():
    """System resources health check"""
    health_data = await health_checker.check_system_resources()
    status_code = 200 if health_data["status"] in ["healthy", "warning"] else 503
    
    return JSONResponse(content=health_data, status_code=status_code)