"""
Simplified Configuration for Azure Deployment
"""
import os
from typing import Dict, Any


class SimpleSettings:
    """Simplified settings for Azure deployment"""
    
    def __init__(self):
        # Azure OpenAI Configuration
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://nubeweb.openai.azure.com/")
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2024-10-21")
        
        # Model Deployments
        self.AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o-mini")
        self.AZURE_VISION_DEPLOYMENT = os.getenv("AZURE_VISION_DEPLOYMENT", "gpt-4o-mini")
        self.AZURE_AUDIO_DEPLOYMENT = os.getenv("AZURE_AUDIO_DEPLOYMENT", "gpt-4o-mini-audio-preview")
        self.AZURE_REASONING_DEPLOYMENT = os.getenv("AZURE_REASONING_DEPLOYMENT", "o1")
        self.AZURE_FAST_REASONING_DEPLOYMENT = os.getenv("AZURE_FAST_REASONING_DEPLOYMENT", "o3-mini")
        self.AZURE_EMBEDDINGS_DEPLOYMENT = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT", "text-embedding-3-small")
        
        # Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.USE_MANAGED_IDENTITY = os.getenv("USE_MANAGED_IDENTITY", "true").lower() == "true"
    
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
    
    def has_azure_openai(self) -> bool:
        """Check if Azure OpenAI is configured"""
        return bool(self.AZURE_OPENAI_ENDPOINT and 
                   (self.AZURE_OPENAI_API_KEY or self.USE_MANAGED_IDENTITY))


# Global instance
settings = SimpleSettings()