import traceback
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import (
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
    ConfigurationError
)
from app.schemas.errors import (
    ErrorResponse,
    ValidationErrorResponse,
    DatabaseErrorResponse,
    ExternalServiceErrorResponse
)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all unhandled exceptions."""
    
    request_id = getattr(request.state, 'request_id', None)
    
    # Handle custom e-commerce exceptions
    if isinstance(exc, EcommerceException):
        return await handle_ecommerce_exception(request, exc, request_id)
    
    # Handle FastAPI HTTPExceptions (for backward compatibility)
    if hasattr(exc, 'status_code') and hasattr(exc, 'detail'):
        return await handle_http_exception(request, exc, request_id)
    
    # Handle unexpected exceptions
    return await handle_unexpected_exception(request, exc, request_id)


async def handle_ecommerce_exception(
    request: Request, 
    exc: EcommerceException, 
    request_id: str
) -> JSONResponse:
    """Handle custom e-commerce exceptions."""
    
    # Log the error with context
    logger.error(
        "E-commerce exception | error_code={} message={} details={}",
        exc.error_code,
        exc.message,
        exc.details
    )
    
    # Create appropriate error response based on exception type
    if isinstance(exc, ValidationError):
        error_response = ValidationErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            validation_errors=exc.details.get("validation_errors", [])
        )
    
    elif isinstance(exc, DatabaseError):
        error_response = DatabaseErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            operation=exc.details.get("operation"),
            original_error=exc.details.get("original_error")
        )
    
    elif isinstance(exc, ExternalServiceError):
        error_response = ExternalServiceErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            service=exc.details.get("service")
        )
    
    else:
        # Generic e-commerce exception
        error_response = ErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc)
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(exclude_none=True)
    )


async def handle_http_exception(
    request: Request, 
    exc: Exception, 
    request_id: str
) -> JSONResponse:
    """Handle FastAPI HTTPExceptions for backward compatibility."""
    
    logger.warning(
        "HTTPException | status_code={} detail={}",
        getattr(exc, 'status_code', 500),
        getattr(exc, 'detail', 'Unknown error')
    )
    
    error_response = ErrorResponse(
        message=str(getattr(exc, 'detail', 'HTTP Error')),
        error_code="HTTP_EXCEPTION",
        details={"status_code": getattr(exc, 'status_code', 500)},
        request_id=request_id,
        timestamp=datetime.now(timezone.utc)
    )
    
    return JSONResponse(
        status_code=getattr(exc, 'status_code', 500),
        content=error_response.dict(exclude_none=True)
    )


async def handle_unexpected_exception(
    request: Request, 
    exc: Exception, 
    request_id: str
) -> JSONResponse:
    """Handle unexpected exceptions."""
    
    # Log the full traceback for debugging
    logger.error(
        "Unexpected exception | type={} message={} traceback={}",
        type(exc).__name__,
        str(exc),
        traceback.format_exc()
    )
    
    # Don't expose internal error details in production
    error_response = ErrorResponse(
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        details={"type": type(exc).__name__} if logger.level == "DEBUG" else None,
        request_id=request_id,
        timestamp=datetime.now(timezone.utc)
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict(exclude_none=True)
    )


def add_exception_handlers(app: FastAPI) -> FastAPI:
    """Add exception handlers to FastAPI app."""
    
    # Add global exception handler for all exceptions
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Add specific handlers for custom exceptions (optional, but provides better routing)
    app.add_exception_handler(EcommerceException, global_exception_handler)
    app.add_exception_handler(NotFoundError, global_exception_handler)
    app.add_exception_handler(ValidationError, global_exception_handler)
    app.add_exception_handler(AuthenticationError, global_exception_handler)
    app.add_exception_handler(AuthorizationError, global_exception_handler)
    app.add_exception_handler(ConflictError, global_exception_handler)
    app.add_exception_handler(DatabaseError, global_exception_handler)
    app.add_exception_handler(ExternalServiceError, global_exception_handler)
    app.add_exception_handler(PaymentError, global_exception_handler)
    app.add_exception_handler(EmailError, global_exception_handler)
    app.add_exception_handler(ConfigurationError, global_exception_handler)
    
    logger.info("Exception handlers registered")
    return app
