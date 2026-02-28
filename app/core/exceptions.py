from typing import Any, Dict, Optional


class EcommerceException(Exception):
    """Base exception class for all e-commerce application errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.error_code = error_code or "GENERIC_ERROR"
        self.details = details or {}
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


class NotFoundError(EcommerceException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: str = None):
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            details={"resource": resource, "id": identifier},
            status_code=404
        )


class ValidationError(EcommerceException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = value
            
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
            status_code=422
        )


class AuthenticationError(EcommerceException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(EcommerceException):
    """Raised when user lacks permission for an action."""
    
    def __init__(self, message: str = "Access denied", required_role: str = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details={"required_role": required_role} if required_role else {},
            status_code=403
        )


class ConflictError(EcommerceException):
    """Raised when a resource conflicts with existing data."""
    
    def __init__(self, message: str, resource: str = None, field: str = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details={"resource": resource, "field": field} if resource or field else {},
            status_code=409
        )


class DatabaseError(EcommerceException):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, original_error: str = None):
        super().__init__(
            message=f"Database operation failed: {operation}",
            error_code="DATABASE_ERROR",
            details={
                "operation": operation,
                "original_error": original_error
            } if original_error else {"operation": operation},
            status_code=500
        )


class ExternalServiceError(EcommerceException):
    """Raised when external API calls fail."""
    
    def __init__(self, service: str, message: str = None, status_code: int = 502):
        super().__init__(
            message=message or f"External service {service} unavailable",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
            status_code=status_code
        )


class PaymentError(EcommerceException):
    """Raised when payment processing fails."""
    
    def __init__(self, message: str, payment_intent_id: str = None):
        super().__init__(
            message=message,
            error_code="PAYMENT_ERROR",
            details={"payment_intent_id": payment_intent_id} if payment_intent_id else {},
            status_code=402  # Payment Required
        )


class BusinessRuleError(EcommerceException):
    """
    Raised when a request is syntactically correct but violates a business rule.
    Example: 'Cannot cancel an order that has already been shipped.'
    """
    
    def __init__(self, message: str, rule_name: str = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule_name": rule_name} if rule_name else {},
            status_code=422
        )


class RateLimitError(EcommerceException):
    """Raised when the user has sent too many requests in a given amount of time."""
    
    def __init__(self, message: str = "Too many requests", retry_after: str = "60 seconds"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
            status_code=429
        )


class ServiceUnavailableError(EcommerceException):
    """Raised when the server is temporarily unable to handle the request (e.g. maintenance)."""
    
    def __init__(self, message: str = "Service temporarily unavailable", service_name: str = None):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            details={"service_name": service_name} if service_name else {},
            status_code=503
        )


class EmailError(EcommerceException):
    """Raised when email sending fails."""
    
    def __init__(self, message: str, recipient: str = None):
        super().__init__(
            message=message,
            error_code="EMAIL_ERROR",
            details={"recipient": recipient} if recipient else {},
            status_code=500
        )


class ConfigurationError(EcommerceException):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, setting: str = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={"setting": setting} if setting else {},
            status_code=500
        )


# Specific validation errors for common scenarios
class ProductValidationError(ValidationError):
    """Product-specific validation errors."""
    
    def __init__(self, field: str, value: Any, constraint: str):
        message = f"Invalid {field}: '{value}'. {constraint}"
        super().__init__(message=message, field=field, value=value)


class OrderValidationError(ValidationError):
    """Order-specific validation errors."""
    
    def __init__(self, message: str, order_id: str = None, item_index: int = None):
        details = {}
        if order_id:
            details["order_id"] = order_id
        if item_index is not None:
            details["item_index"] = item_index
        
        super().__init__(message=message, details=details)


class UserValidationError(ValidationError):
    """User-specific validation errors."""
    
    def __init__(self, field: str, value: Any, constraint: str):
        message = f"Invalid {field}: '{value}'. {constraint}"
        super().__init__(message=message, field=field, value=value)
