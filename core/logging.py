"""
Advanced Logging Configuration for AI Agent
Structured logging with multiple outputs and monitoring integration
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from structlog.stdlib import LoggerFactory

from core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Standard logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s [%(pathname)s]"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file_general": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/general.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            },
            "file_conversation": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/conversation.log",
                "maxBytes": 52428800,  # 50MB
                "backupCount": 20,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            },
            "file_business": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/business.log",
                "maxBytes": 20971520,  # 20MB
                "backupCount": 10,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            },
            "file_integration": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/integration.log",
                "maxBytes": 20971520,  # 20MB
                "backupCount": 10,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            },
            "file_performance": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/performance.log",
                "maxBytes": 20971520,  # 20MB
                "backupCount": 15,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "detailed"
            }
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": ["console", "file_general"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            # Application loggers
            "core": {
                "handlers": ["console", "file_general", "file_error"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "agents": {
                "handlers": ["console", "file_general", "file_conversation"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "conversation": {
                "handlers": ["file_conversation"],
                "level": "INFO",
                "propagate": False
            },
            "business": {
                "handlers": ["console", "file_business"],
                "level": "INFO",
                "propagate": False
            },
            "integrations": {
                "handlers": ["console", "file_integration", "file_error"],
                "level": "INFO",
                "propagate": False
            },
            "performance": {
                "handlers": ["file_performance"],
                "level": "INFO",
                "propagate": False
            },
            # External library loggers
            "openai": {
                "handlers": ["file_general"],
                "level": "WARNING",
                "propagate": False
            },
            "azure": {
                "handlers": ["file_general"],
                "level": "WARNING",
                "propagate": False
            },
            "httpx": {
                "handlers": ["file_general"],
                "level": "WARNING",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "celery": {
                "handlers": ["console", "file_general"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Configure Sentry if available
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors and above as events
        )
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[
                sentry_logging,
                SqlalchemyIntegration(),
                FastApiIntegration(auto_enable=True),
                CeleryIntegration()
            ],
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            send_default_pii=False,
            before_send=filter_sensitive_data
        )


def filter_sensitive_data(event: Dict[str, Any], hint: Dict[str, Any]) -> Dict[str, Any]:
    """Filter sensitive information from Sentry events"""
    
    # List of sensitive keys to remove or mask
    sensitive_keys = [
        'password', 'token', 'key', 'secret', 'authorization',
        'api_key', 'auth_token', 'access_token', 'refresh_token',
        'credit_card', 'ssn', 'social_security', 'email', 'phone'
    ]
    
    def clean_dict(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    data[key] = "[FILTERED]"
                elif isinstance(value, (dict, list)):
                    clean_dict(value)
        elif isinstance(data, list):
            for item in data:
                clean_dict(item)
    
    clean_dict(event)
    return event


class ConversationLogger:
    """Specialized logger for conversation tracking"""
    
    def __init__(self):
        self.logger = structlog.get_logger("conversation")
    
    def log_user_message(self, session_id: str, user_id: str, message: str, metadata: Dict[str, Any] = None):
        """Log user message with context"""
        self.logger.info(
            "user_message",
            session_id=session_id,
            user_id=user_id,
            message=message,
            metadata=metadata or {}
        )
    
    def log_agent_response(self, session_id: str, agent_type: str, response: str, 
                          processing_time: float, metadata: Dict[str, Any] = None):
        """Log agent response with performance metrics"""
        self.logger.info(
            "agent_response",
            session_id=session_id,
            agent_type=agent_type,
            response=response,
            processing_time_ms=processing_time * 1000,
            metadata=metadata or {}
        )
    
    def log_state_transition(self, session_id: str, from_state: str, to_state: str, 
                           trigger: str, metadata: Dict[str, Any] = None):
        """Log conversation state transitions"""
        self.logger.info(
            "state_transition",
            session_id=session_id,
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            metadata=metadata or {}
        )
    
    def log_intent_detection(self, session_id: str, detected_intent: str, confidence: float,
                           alternatives: list = None, metadata: Dict[str, Any] = None):
        """Log intent detection results"""
        self.logger.info(
            "intent_detection",
            session_id=session_id,
            detected_intent=detected_intent,
            confidence=confidence,
            alternatives=alternatives or [],
            metadata=metadata or {}
        )
    
    def log_error(self, session_id: str, error_type: str, error_message: str, 
                  context: Dict[str, Any] = None):
        """Log conversation errors"""
        self.logger.error(
            "conversation_error",
            session_id=session_id,
            error_type=error_type,
            error_message=error_message,
            context=context or {}
        )


class BusinessLogger:
    """Specialized logger for business events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_lead_generated(self, lead_id: str, source: str, quality_score: float,
                          lead_data: Dict[str, Any]):
        """Log new lead generation"""
        self.logger.info(
            "lead_generated",
            lead_id=lead_id,
            source=source,
            quality_score=quality_score,
            lead_data=lead_data
        )
    
    def log_quotation_generated(self, quote_id: str, service_type: str, amount: float,
                              client_data: Dict[str, Any], requirements: Dict[str, Any]):
        """Log quotation generation"""
        self.logger.info(
            "quotation_generated",
            quote_id=quote_id,
            service_type=service_type,
            amount=amount,
            client_data=client_data,
            requirements=requirements
        )
    
    def log_conversion(self, session_id: str, conversion_type: str, value: float,
                      conversion_data: Dict[str, Any]):
        """Log business conversion events"""
        self.logger.info(
            "conversion",
            session_id=session_id,
            conversion_type=conversion_type,
            value=value,
            conversion_data=conversion_data
        )
    
    def log_integration_event(self, integration: str, event_type: str, success: bool,
                             data: Dict[str, Any] = None, error: str = None):
        """Log integration events"""
        self.logger.info(
            "integration_event",
            integration=integration,
            event_type=event_type,
            success=success,
            data=data or {},
            error=error
        )


class PerformanceLogger:
    """Specialized logger for performance monitoring"""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_api_call(self, endpoint: str, method: str, response_time: float,
                    status_code: int, user_id: str = None):
        """Log API call performance"""
        self.logger.info(
            "api_call",
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time * 1000,
            status_code=status_code,
            user_id=user_id
        )
    
    def log_model_inference(self, model_name: str, operation: str, input_tokens: int,
                           output_tokens: int, processing_time: float, cost: float = None):
        """Log AI model inference performance"""
        self.logger.info(
            "model_inference",
            model_name=model_name,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            processing_time_ms=processing_time * 1000,
            cost=cost
        )
    
    def log_database_query(self, query_type: str, table: str, execution_time: float,
                          records_affected: int = None):
        """Log database query performance"""
        self.logger.info(
            "database_query",
            query_type=query_type,
            table=table,
            execution_time_ms=execution_time * 1000,
            records_affected=records_affected
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, 
                           execution_time: float):
        """Log cache operation performance"""
        self.logger.info(
            "cache_operation",
            operation=operation,
            key=key,
            hit=hit,
            execution_time_ms=execution_time * 1000
        )


# Initialize specialized loggers
conversation_logger = ConversationLogger()
business_logger = BusinessLogger()
performance_logger = PerformanceLogger()


# Utility functions
def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def log_function_call(logger_name: str = None):
    """Decorator to log function calls with timing"""
    def decorator(func):
        import time
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    "function_call",
                    function=func.__name__,
                    execution_time_ms=execution_time * 1000,
                    success=True
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    "function_call",
                    function=func.__name__,
                    execution_time_ms=execution_time * 1000,
                    success=False,
                    error=str(e)
                )
                
                raise
        
        return wrapper
    return decorator