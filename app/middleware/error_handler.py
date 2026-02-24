import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
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
from app.common.response import error_respond


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


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Catch FastAPI HTTPException (e.g. 'Not authenticated') into generic envelope."""
    logger.warning("HTTPException | status_code={} detail={}", exc.status_code, exc.detail)
    return error_respond(
        message=str(exc.detail),
        status_code=exc.status_code,
        error_code="HTTP_EXCEPTION",
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Catch Pydantic/FastAPI request-validation errors into generic envelope."""
    errors = [
        {
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        }
        for err in exc.errors()
    ]
    logger.warning("Validation error | errors={}", errors)
    return error_respond(
        message="Validation failed",
        status_code=422,
        error_code="VALIDATION_ERROR",
        errors=errors,
    )


async def handle_ecommerce_exception(
    request: Request,
    exc: EcommerceException,
    request_id: str
) -> JSONResponse:
    """Handle custom e-commerce exceptions using the generic error format."""

    logger.error(
        "E-commerce exception | error_code={} message={} details={}",
        exc.error_code,
        exc.message,
        exc.details
    )

    return error_respond(
        message=exc.message,
        status_code=exc.status_code,
        error_code=exc.error_code,
        details=exc.details if exc.details else None,
    )


async def handle_http_exception(
    request: Request,
    exc: Exception,
    request_id: str
) -> JSONResponse:
    """Handle FastAPI HTTPExceptions for backward compatibility."""

    status_code = getattr(exc, 'status_code', 500)
    detail = getattr(exc, 'detail', 'Unknown error')

    logger.warning(
        "HTTPException | status_code={} detail={}",
        status_code,
        detail,
    )

    return error_respond(
        message=str(detail),
        status_code=status_code,
        error_code="HTTP_EXCEPTION",
    )


async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
    request_id: str
) -> JSONResponse:
    """Handle unexpected exceptions."""

    logger.error(
        "Unexpected exception | type={} message={} traceback={}",
        type(exc).__name__,
        str(exc),
        traceback.format_exc()
    )

    return error_respond(
        message="Internal server error",
        status_code=500,
        error_code="INTERNAL_ERROR",
    )


def add_exception_handlers(app: FastAPI) -> FastAPI:
    """Add exception handlers to FastAPI app."""

    # FastAPI built-in exceptions — MUST be registered to override defaults
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Add global exception handler for all exceptions
    app.add_exception_handler(Exception, global_exception_handler)

    # Add specific handlers for custom exceptions
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
