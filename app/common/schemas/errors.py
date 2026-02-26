from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field
from app.common.schemas.base import BaseSchema


class ErrorDetail(BaseSchema):
    """Detailed error information for specific fields."""
    field: Optional[str] = Field(None, description="Field name where error occurred")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code for this specific field")
    value: Optional[Any] = Field(None, description="The invalid value that caused the error")


class ErrorResponse(BaseSchema):
    """Standard error response format."""
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field(..., description="Human-readable error message")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    request_id: Optional[str] = Field(None, description="Unique request identifier for tracing")
    timestamp: datetime = Field(..., description="When the error occurred")
    validation_errors: Optional[List[ErrorDetail]] = Field(None, description="Field-specific validation errors")


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation failures."""
    validation_errors: List[ErrorDetail] = Field(..., description="List of validation errors")


class DatabaseErrorResponse(ErrorResponse):
    """Specialized error response for database issues."""
    operation: Optional[str] = Field(None, description="Database operation that failed")
    original_error: Optional[str] = Field(None, description="Original database error message")


class ExternalServiceErrorResponse(ErrorResponse):
    """Specialized error response for external service failures."""
    service: Optional[str] = Field(None, description="Name of the external service")
    service_status: Optional[int] = Field(None, description="HTTP status from external service")


# Success response schemas for consistency
class SuccessResponse(BaseSchema):
    """Standard success response wrapper."""
    success: bool = Field(True, description="Indicates this is a success response")
    message: Optional[str] = Field(None, description="Optional success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    request_id: Optional[str] = Field(None, description="Unique request identifier for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the response was generated")


class PaginatedResponse(BaseSchema):
    """Standard paginated response format."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_prev: bool = Field(..., description="Whether there's a previous page")
