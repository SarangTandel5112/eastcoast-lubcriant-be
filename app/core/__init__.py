"""Core package for the e-commerce application."""

from .config import settings
from .logging import setup_logging
from .security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, get_current_user, require_admin, oauth2_scheme
)
from .exceptions import (
    EcommerceException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    PaymentError,
    EmailError,
    ConfigurationError,
    ProductValidationError,
    OrderValidationError,
    UserValidationError
)

__all__ = [
    "settings",
    "setup_logging",
    "hash_password",
    "verify_password", 
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "require_admin",
    "oauth2_scheme",
    "EcommerceException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "PaymentError",
    "EmailError",
    "ConfigurationError",
    "ProductValidationError",
    "OrderValidationError",
    "UserValidationError"
]
