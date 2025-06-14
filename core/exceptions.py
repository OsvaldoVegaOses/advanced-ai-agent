"""
Custom Exception Classes for Advanced AI Agent
Comprehensive error handling for business automation platform
"""

from typing import Optional, Dict, Any


class AgentException(Exception):
    """Base exception class for AI Agent errors"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: str = "AGENT_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.context = context or {}
        super().__init__(detail)


# =============================================================================
# AI MODEL EXCEPTIONS
# =============================================================================

class ModelException(AgentException):
    """Base exception for AI model errors"""
    pass


class ModelInitializationError(ModelException):
    """Raised when AI model fails to initialize"""
    
    def __init__(self, model_name: str, detail: str):
        super().__init__(
            detail=f"Failed to initialize model '{model_name}': {detail}",
            status_code=500,
            error_code="MODEL_INIT_ERROR",
            context={"model_name": model_name}
        )


class ModelInferenceError(ModelException):
    """Raised when AI model inference fails"""
    
    def __init__(self, model_name: str, detail: str, input_data: Optional[Dict] = None):
        super().__init__(
            detail=f"Model '{model_name}' inference failed: {detail}",
            status_code=500,
            error_code="MODEL_INFERENCE_ERROR",
            context={"model_name": model_name, "input_data": input_data}
        )


class TokenLimitExceededError(ModelException):
    """Raised when input exceeds model token limits"""
    
    def __init__(self, model_name: str, token_count: int, max_tokens: int):
        super().__init__(
            detail=f"Input token count ({token_count}) exceeds {model_name} limit ({max_tokens})",
            status_code=400,
            error_code="TOKEN_LIMIT_EXCEEDED",
            context={"model_name": model_name, "token_count": token_count, "max_tokens": max_tokens}
        )


class RateLimitExceededError(ModelException):
    """Raised when API rate limits are exceeded"""
    
    def __init__(self, service: str, retry_after: Optional[int] = None):
        super().__init__(
            detail=f"Rate limit exceeded for {service}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            context={"service": service, "retry_after": retry_after}
        )


# =============================================================================
# CONVERSATION EXCEPTIONS
# =============================================================================

class ConversationException(AgentException):
    """Base exception for conversation errors"""
    pass


class InvalidConversationStateError(ConversationException):
    """Raised when conversation state is invalid"""
    
    def __init__(self, current_state: str, attempted_action: str):
        super().__init__(
            detail=f"Cannot perform '{attempted_action}' in state '{current_state}'",
            status_code=400,
            error_code="INVALID_CONVERSATION_STATE",
            context={"current_state": current_state, "attempted_action": attempted_action}
        )


class ConversationTimeoutError(ConversationException):
    """Raised when conversation times out"""
    
    def __init__(self, session_id: str, timeout_minutes: int):
        super().__init__(
            detail=f"Conversation timed out after {timeout_minutes} minutes",
            status_code=408,
            error_code="CONVERSATION_TIMEOUT",
            context={"session_id": session_id, "timeout_minutes": timeout_minutes}
        )


class MemoryStoreError(ConversationException):
    """Raised when memory operations fail"""
    
    def __init__(self, operation: str, detail: str):
        super().__init__(
            detail=f"Memory {operation} failed: {detail}",
            status_code=500,
            error_code="MEMORY_STORE_ERROR",
            context={"operation": operation}
        )


# =============================================================================
# BUSINESS LOGIC EXCEPTIONS
# =============================================================================

class BusinessLogicException(AgentException):
    """Base exception for business logic errors"""
    pass


class InvalidLeadDataError(BusinessLogicException):
    """Raised when lead data is invalid or incomplete"""
    
    def __init__(self, missing_fields: list, provided_data: Optional[Dict] = None):
        super().__init__(
            detail=f"Invalid lead data. Missing required fields: {', '.join(missing_fields)}",
            status_code=400,
            error_code="INVALID_LEAD_DATA",
            context={"missing_fields": missing_fields, "provided_data": provided_data}
        )


class QuotationGenerationError(BusinessLogicException):
    """Raised when quotation generation fails"""
    
    def __init__(self, reason: str, requirements: Optional[Dict] = None):
        super().__init__(
            detail=f"Cannot generate quotation: {reason}",
            status_code=400,
            error_code="QUOTATION_GENERATION_ERROR",
            context={"reason": reason, "requirements": requirements}
        )


class ServiceConfigurationError(BusinessLogicException):
    """Raised when service configuration is invalid"""
    
    def __init__(self, service_type: str, detail: str):
        super().__init__(
            detail=f"Invalid configuration for service '{service_type}': {detail}",
            status_code=400,
            error_code="SERVICE_CONFIG_ERROR",
            context={"service_type": service_type}
        )


# =============================================================================
# INTEGRATION EXCEPTIONS
# =============================================================================

class IntegrationException(AgentException):
    """Base exception for external integration errors"""
    pass


class CRMIntegrationError(IntegrationException):
    """Raised when CRM integration fails"""
    
    def __init__(self, crm_system: str, operation: str, detail: str):
        super().__init__(
            detail=f"CRM {operation} failed for {crm_system}: {detail}",
            status_code=502,
            error_code="CRM_INTEGRATION_ERROR",
            context={"crm_system": crm_system, "operation": operation}
        )


class EmailServiceError(IntegrationException):
    """Raised when email service fails"""
    
    def __init__(self, provider: str, operation: str, detail: str):
        super().__init__(
            detail=f"Email {operation} failed with {provider}: {detail}",
            status_code=502,
            error_code="EMAIL_SERVICE_ERROR",
            context={"provider": provider, "operation": operation}
        )


class CalendarIntegrationError(IntegrationException):
    """Raised when calendar integration fails"""
    
    def __init__(self, provider: str, operation: str, detail: str):
        super().__init__(
            detail=f"Calendar {operation} failed with {provider}: {detail}",
            status_code=502,
            error_code="CALENDAR_INTEGRATION_ERROR",
            context={"provider": provider, "operation": operation}
        )


class PaymentProcessingError(IntegrationException):
    """Raised when payment processing fails"""
    
    def __init__(self, provider: str, operation: str, detail: str, transaction_id: Optional[str] = None):
        super().__init__(
            detail=f"Payment {operation} failed with {provider}: {detail}",
            status_code=502,
            error_code="PAYMENT_PROCESSING_ERROR",
            context={"provider": provider, "operation": operation, "transaction_id": transaction_id}
        )


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationException(AgentException):
    """Base exception for validation errors"""
    pass


class InvalidInputError(ValidationException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, value: Any, expected_format: str):
        super().__init__(
            detail=f"Invalid {field}: '{value}'. Expected format: {expected_format}",
            status_code=400,
            error_code="INVALID_INPUT",
            context={"field": field, "value": str(value), "expected_format": expected_format}
        )


class AuthenticationError(ValidationException):
    """Raised when authentication fails"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(ValidationException):
    """Raised when authorization fails"""
    
    def __init__(self, resource: str, action: str):
        super().__init__(
            detail=f"Insufficient permissions to {action} {resource}",
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            context={"resource": resource, "action": action}
        )


# =============================================================================
# MULTIMODAL PROCESSING EXCEPTIONS
# =============================================================================

class MultimodalException(AgentException):
    """Base exception for multimodal processing errors"""
    pass


class ImageProcessingError(MultimodalException):
    """Raised when image processing fails"""
    
    def __init__(self, operation: str, detail: str, image_metadata: Optional[Dict] = None):
        super().__init__(
            detail=f"Image {operation} failed: {detail}",
            status_code=400,
            error_code="IMAGE_PROCESSING_ERROR",
            context={"operation": operation, "image_metadata": image_metadata}
        )


class AudioProcessingError(MultimodalException):
    """Raised when audio processing fails"""
    
    def __init__(self, operation: str, detail: str, audio_metadata: Optional[Dict] = None):
        super().__init__(
            detail=f"Audio {operation} failed: {detail}",
            status_code=400,
            error_code="AUDIO_PROCESSING_ERROR",
            context={"operation": operation, "audio_metadata": audio_metadata}
        )


class DocumentProcessingError(MultimodalException):
    """Raised when document processing fails"""
    
    def __init__(self, operation: str, detail: str, document_metadata: Optional[Dict] = None):
        super().__init__(
            detail=f"Document {operation} failed: {detail}",
            status_code=400,
            error_code="DOCUMENT_PROCESSING_ERROR",
            context={"operation": operation, "document_metadata": document_metadata}
        )


# =============================================================================
# SYSTEM EXCEPTIONS
# =============================================================================

class SystemException(AgentException):
    """Base exception for system-level errors"""
    pass


class DatabaseConnectionError(SystemException):
    """Raised when database connection fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Database connection failed: {detail}",
            status_code=503,
            error_code="DATABASE_CONNECTION_ERROR"
        )


class CacheError(SystemException):
    """Raised when cache operations fail"""
    
    def __init__(self, operation: str, detail: str):
        super().__init__(
            detail=f"Cache {operation} failed: {detail}",
            status_code=503,
            error_code="CACHE_ERROR",
            context={"operation": operation}
        )


class ConfigurationError(SystemException):
    """Raised when system configuration is invalid"""
    
    def __init__(self, component: str, detail: str):
        super().__init__(
            detail=f"Configuration error in {component}: {detail}",
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            context={"component": component}
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def handle_external_api_error(service: str, operation: str, error: Exception) -> AgentException:
    """Convert external API errors to appropriate AgentException"""
    
    error_message = str(error)
    
    # Rate limiting
    if "rate limit" in error_message.lower() or "429" in error_message:
        return RateLimitExceededError(service)
    
    # Authentication errors
    if any(term in error_message.lower() for term in ["unauthorized", "401", "invalid key", "authentication"]):
        return AuthenticationError(f"Authentication failed for {service}")
    
    # Payment specific errors
    if service.lower() in ["stripe", "paypal", "payment"]:
        return PaymentProcessingError(service, operation, error_message)
    
    # CRM specific errors
    if service.lower() in ["hubspot", "salesforce", "pipedrive", "crm"]:
        return CRMIntegrationError(service, operation, error_message)
    
    # Email specific errors
    if service.lower() in ["sendgrid", "mailchimp", "email"]:
        return EmailServiceError(service, operation, error_message)
    
    # Calendar specific errors
    if service.lower() in ["google", "outlook", "calendly", "calendar"]:
        return CalendarIntegrationError(service, operation, error_message)
    
    # Generic integration error
    return IntegrationException(
        detail=f"External service error in {service}: {error_message}",
        status_code=502,
        error_code="EXTERNAL_SERVICE_ERROR",
        context={"service": service, "operation": operation}
    )


def create_validation_error(validation_errors: Dict[str, list]) -> ValidationException:
    """Create a validation error from multiple field errors"""
    error_details = []
    for field, errors in validation_errors.items():
        error_details.append(f"{field}: {', '.join(errors)}")
    
    return ValidationException(
        detail=f"Validation failed: {'; '.join(error_details)}",
        status_code=400,
        error_code="VALIDATION_FAILED",
        context={"validation_errors": validation_errors}
    )