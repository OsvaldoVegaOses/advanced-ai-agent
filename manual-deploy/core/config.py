"""
Core Configuration Module
Centralized configuration management for the Advanced AI Agent
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from pydantic import BaseSettings, validator, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings with validation"""
    
    # =============================================================================
    # BASIC APPLICATION SETTINGS
    # =============================================================================
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    DATABASE_URL: str = Field(env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # =============================================================================
    # AZURE OPENAI CONFIGURATION
    # =============================================================================
    AZURE_OPENAI_ENDPOINT: str = Field(env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = Field(env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_VERSION: str = Field(default="2024-10-21", env="AZURE_OPENAI_VERSION")
    
    # Model Deployments
    AZURE_CHAT_DEPLOYMENT: str = Field(default="gpt-4o-mini", env="AZURE_CHAT_DEPLOYMENT")
    AZURE_VISION_DEPLOYMENT: str = Field(default="gpt-4o-mini", env="AZURE_VISION_DEPLOYMENT")
    AZURE_AUDIO_DEPLOYMENT: str = Field(default="gpt-4o-mini-audio-preview", env="AZURE_AUDIO_DEPLOYMENT")
    AZURE_REASONING_DEPLOYMENT: str = Field(default="o1", env="AZURE_REASONING_DEPLOYMENT")
    AZURE_FAST_REASONING_DEPLOYMENT: str = Field(default="o3-mini", env="AZURE_FAST_REASONING_DEPLOYMENT")
    AZURE_EMBEDDINGS_DEPLOYMENT: str = Field(default="text-embedding-3-small", env="AZURE_EMBEDDINGS_DEPLOYMENT")
    
    # =============================================================================
    # VECTOR DATABASE
    # =============================================================================
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="ai-agent-memory", env="PINECONE_INDEX_NAME")
    
    # =============================================================================
    # COMMUNICATION SERVICES
    # =============================================================================
    
    # SendGrid
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    FROM_EMAIL: str = Field(default="noreply@example.com", env="FROM_EMAIL")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    TWILIO_WHATSAPP_NUMBER: Optional[str] = Field(default=None, env="TWILIO_WHATSAPP_NUMBER")
    
    # Slack
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: Optional[str] = Field(default=None, env="SLACK_SIGNING_SECRET")
    
    # =============================================================================
    # CRM INTEGRATIONS
    # =============================================================================
    
    # HubSpot
    HUBSPOT_API_KEY: Optional[str] = Field(default=None, env="HUBSPOT_API_KEY")
    HUBSPOT_PORTAL_ID: Optional[str] = Field(default=None, env="HUBSPOT_PORTAL_ID")
    
    # Salesforce
    SALESFORCE_CLIENT_ID: Optional[str] = Field(default=None, env="SALESFORCE_CLIENT_ID")
    SALESFORCE_CLIENT_SECRET: Optional[str] = Field(default=None, env="SALESFORCE_CLIENT_SECRET")
    SALESFORCE_USERNAME: Optional[str] = Field(default=None, env="SALESFORCE_USERNAME")
    SALESFORCE_PASSWORD: Optional[str] = Field(default=None, env="SALESFORCE_PASSWORD")
    SALESFORCE_SECURITY_TOKEN: Optional[str] = Field(default=None, env="SALESFORCE_SECURITY_TOKEN")
    
    # =============================================================================
    # CALENDAR INTEGRATIONS
    # =============================================================================
    GOOGLE_CALENDAR_CREDENTIALS_PATH: Optional[str] = Field(default=None, env="GOOGLE_CALENDAR_CREDENTIALS_PATH")
    GOOGLE_CALENDAR_ID: Optional[str] = Field(default=None, env="GOOGLE_CALENDAR_ID")
    CALENDLY_API_KEY: Optional[str] = Field(default=None, env="CALENDLY_API_KEY")
    CALENDLY_USER_URI: Optional[str] = Field(default=None, env="CALENDLY_USER_URI")
    
    # =============================================================================
    # PAYMENT PROCESSING
    # =============================================================================
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # =============================================================================
    # SECURITY & RATE LIMITING
    # =============================================================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # =============================================================================
    # MONITORING
    # =============================================================================
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    GA_TRACKING_ID: Optional[str] = Field(default=None, env="GA_TRACKING_ID")
    
    # =============================================================================
    # LOGGING
    # =============================================================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # =============================================================================
    # CELERY
    # =============================================================================
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # =============================================================================
    # AI MODEL CONFIGURATION
    # =============================================================================
    
    # Model Selection Strategy
    MODEL_SELECTION_STRATEGY: str = Field(default="cost_optimized", env="MODEL_SELECTION_STRATEGY")
    
    # Performance Thresholds
    RESPONSE_TIME_THRESHOLD: float = Field(default=2.0, env="RESPONSE_TIME_THRESHOLD")
    CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    
    # Conversation Memory
    MAX_CONVERSATION_HISTORY: int = Field(default=20, env="MAX_CONVERSATION_HISTORY")
    CONVERSATION_TIMEOUT_MINUTES: int = Field(default=30, env="CONVERSATION_TIMEOUT_MINUTES")
    
    # Vector Search
    VECTOR_SEARCH_TOP_K: int = Field(default=5, env="VECTOR_SEARCH_TOP_K")
    VECTOR_SIMILARITY_THRESHOLD: float = Field(default=0.8, env="VECTOR_SIMILARITY_THRESHOLD")
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    EMBEDDING_CACHE_SIZE: int = Field(default=10000, env="EMBEDDING_CACHE_SIZE")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse ALLOWED_HOSTS from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DEBUG,
            "pool_size": 20 if self.is_production else 5,
            "max_overflow": 30 if self.is_production else 10,
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
        }
    
    @property
    def openai_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI configuration"""
        return {
            "endpoint": self.AZURE_OPENAI_ENDPOINT,
            "api_key": self.AZURE_OPENAI_API_KEY,
            "api_version": self.AZURE_OPENAI_VERSION,
            "models": {
                "chat": self.AZURE_CHAT_DEPLOYMENT,
                "vision": self.AZURE_VISION_DEPLOYMENT,
                "audio": self.AZURE_AUDIO_DEPLOYMENT,
                "reasoning": self.AZURE_REASONING_DEPLOYMENT,
                "fast_reasoning": self.AZURE_FAST_REASONING_DEPLOYMENT,
                "embeddings": self.AZURE_EMBEDDINGS_DEPLOYMENT,
            }
        }
    
    @property
    def integrations_enabled(self) -> Dict[str, bool]:
        """Check which integrations are enabled"""
        return {
            "sendgrid": bool(self.SENDGRID_API_KEY),
            "twilio": bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN),
            "slack": bool(self.SLACK_BOT_TOKEN),
            "hubspot": bool(self.HUBSPOT_API_KEY),
            "salesforce": bool(self.SALESFORCE_CLIENT_ID and self.SALESFORCE_CLIENT_SECRET),
            "google_calendar": bool(self.GOOGLE_CALENDAR_CREDENTIALS_PATH),
            "calendly": bool(self.CALENDLY_API_KEY),
            "stripe": bool(self.STRIPE_SECRET_KEY),
            "pinecone": bool(self.PINECONE_API_KEY),
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Business logic configuration
class BusinessConfig:
    """Business-specific configuration and rules"""
    
    # Service categories and pricing
    SERVICE_CATEGORIES = {
        "web_development": {
            "name": "Desarrollo Web",
            "base_price": 2000,
            "complexity_multipliers": {"basic": 1.0, "intermediate": 1.5, "advanced": 2.5},
            "typical_timeline_weeks": {"basic": 2, "intermediate": 4, "advanced": 8}
        },
        "ecommerce": {
            "name": "E-commerce",
            "base_price": 3500,
            "complexity_multipliers": {"basic": 1.0, "intermediate": 1.8, "advanced": 3.0},
            "typical_timeline_weeks": {"basic": 3, "intermediate": 6, "advanced": 12}
        },
        "mobile_app": {
            "name": "Aplicación Móvil",
            "base_price": 5000,
            "complexity_multipliers": {"basic": 1.0, "intermediate": 2.0, "advanced": 4.0},
            "typical_timeline_weeks": {"basic": 6, "intermediate": 12, "advanced": 20}
        },
        "digital_marketing": {
            "name": "Marketing Digital",
            "base_price": 800,
            "complexity_multipliers": {"basic": 1.0, "intermediate": 1.5, "advanced": 2.0},
            "typical_timeline_weeks": {"basic": 2, "intermediate": 4, "advanced": 8}
        },
        "consulting": {
            "name": "Consultoría",
            "base_price": 150,  # per hour
            "complexity_multipliers": {"basic": 1.0, "intermediate": 1.3, "advanced": 1.8},
            "typical_timeline_weeks": {"basic": 1, "intermediate": 2, "advanced": 4}
        }
    }
    
    # Lead scoring criteria
    LEAD_SCORING_CRITERIA = {
        "budget_ranges": {
            "under_1k": {"score": 2, "label": "Micro"},
            "1k_5k": {"score": 5, "label": "Small"},
            "5k_15k": {"score": 8, "label": "Medium"},
            "15k_50k": {"score": 10, "label": "Large"},
            "over_50k": {"score": 10, "label": "Enterprise"}
        },
        "urgency_levels": {
            "not_urgent": {"score": 2, "weeks": 12},
            "moderate": {"score": 5, "weeks": 6},
            "urgent": {"score": 8, "weeks": 2},
            "immediate": {"score": 10, "weeks": 1}
        },
        "company_size": {
            "freelancer": {"score": 3},
            "startup": {"score": 6},
            "small_business": {"score": 7},
            "medium_business": {"score": 9},
            "enterprise": {"score": 10}
        }
    }
    
    # Conversation flow configuration
    CONVERSATION_STATES = {
        "greeting": {"max_duration_minutes": 5, "required_info": []},
        "discovery": {"max_duration_minutes": 15, "required_info": ["service_type", "basic_requirements"]},
        "needs_analysis": {"max_duration_minutes": 20, "required_info": ["detailed_requirements", "timeline", "budget_range"]},
        "solution_presentation": {"max_duration_minutes": 15, "required_info": ["proposed_solution"]},
        "quotation": {"max_duration_minutes": 10, "required_info": ["pricing", "timeline"]},
        "contact_collection": {"max_duration_minutes": 5, "required_info": ["name", "email", "phone"]},
        "closing": {"max_duration_minutes": 5, "required_info": ["next_steps"]}
    }


# Initialize business config
business_config = BusinessConfig()