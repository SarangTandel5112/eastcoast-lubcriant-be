"""Core package for the e-commerce application."""

from .config import settings
from .logging import setup_logging
from .database import get_db_session, verify_db_connection, close_db_connection, init_db_schema
from .supabase_client import get_supabase_client
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
    "get_db_session",
    "verify_db_connection",
    "close_db_connection",
    "get_supabase_client",
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
    "UserValidationError",
    "init_db_schema",
]
