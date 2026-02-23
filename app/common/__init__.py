"""Common shared utilities — error schemas, HTTP clients, etc."""

from app.common.schemas.errors import (
    ErrorDetail,
    ErrorResponse,
    ValidationErrorResponse,
    DatabaseErrorResponse,
    ExternalServiceErrorResponse,
    SuccessResponse,
    PaginatedResponse,
)
from app.common.services.http_client import HTTPClient, ShippingClient

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "ValidationErrorResponse",
    "DatabaseErrorResponse",
    "ExternalServiceErrorResponse",
    "SuccessResponse",
    "PaginatedResponse",
    "HTTPClient",
    "ShippingClient",
]
