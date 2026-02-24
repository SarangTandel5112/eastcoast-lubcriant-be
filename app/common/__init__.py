"""Common shared utilities — response wrapper, error schemas, HTTP clients, etc."""

from app.common.response import respond, error_respond
from app.common.base_dco import BaseDCO
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
    "respond",
    "error_respond",
    "BaseDCO",
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
