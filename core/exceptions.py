"""
Core Exceptions Module
Custom exceptions for the Advanced AI Agent
"""

from typing import Any, Dict, Optional


class BaseAIAgentException(Exception):
    """Base exception for AI Agent"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ModelInitializationError(BaseAIAgentException):
    """Raised when model initialization fails"""
    def __init__(self, model_name: str, error_message: str):
        super().__init__(
            f"Failed to initialize model '{model_name}': {error_message}",
            {"model_name": model_name, "error": error_message}
        )


class ModelInferenceError(BaseAIAgentException):
    """Raised when model inference fails"""
    def __init__(self, model_name: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Model '{model_name}' inference failed: {error_message}",
            {"model_name": model_name, "error": error_message, "context": context}
        )


class TokenLimitExceededError(BaseAIAgentException):
    """Raised when token limit is exceeded"""
    def __init__(self, model_name: str, token_count: int, max_tokens: int):
        super().__init__(
            f"Token limit exceeded for model '{model_name}': {token_count} > {max_tokens}",
            {"model_name": model_name, "token_count": token_count, "max_tokens": max_tokens}
        )


class RateLimitExceededError(BaseAIAgentException):
    """Raised when API rate limit is exceeded"""
    def __init__(self, service_name: str):
        super().__init__(
            f"Rate limit exceeded for service '{service_name}'",
            {"service": service_name}
        )