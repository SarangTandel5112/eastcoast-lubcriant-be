import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ConfigurationError,
    ConflictError,
    DatabaseError,
    EcommerceException,
    EmailError,
    ExternalServiceError,
    NotFoundError,
    PaymentError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from app.common.response import error_respond


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all unhandled exceptions."""

    request_id = getattr(request.state, "request_id", None)

    # Handle custom e-commerce exceptions
    if isinstance(exc, EcommerceException):
        return await handle_ecommerce_exception(request, exc, request_id)

    # Handle Starlette HTTPExceptions (for backward compatibility and missing routes)
    if isinstance(exc, StarletteHTTPException):
        return await http_exception_handler(request, exc)

    # Handle unexpected exceptions
    return await handle_unexpected_exception(request, exc, request_id)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Catch Starlette HTTPException into generic envelope."""
    request_id = getattr(request.state, "request_id", None)

    level = "WARNING" if exc.status_code < 500 else "ERROR"
    logger.log(level, "HTTPException | method={} path={} status_code={} detail={}", request.method, request.url.path, exc.status_code, exc.detail)

    return error_respond(
        message=str(exc.detail),
        status_code=exc.status_code,
        error_code="HTTP_EXCEPTION",
        request_id=request_id,
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Catch Pydantic/FastAPI request-validation errors into generic envelope."""
    request_id = getattr(request.state, "request_id", None)

    errors = [
        {
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        }
        for err in exc.errors()
    ]

    logger.warning("Validation error | method={} path={} errors={}", request.method, request.url.path, errors)

    return error_respond(
        message="Validation failed",
        status_code=422,
        error_code="VALIDATION_ERROR",
        errors=errors,
        request_id=request_id,
    )


async def handle_ecommerce_exception(
    request: Request,
    exc: EcommerceException,
    request_id: str
) -> JSONResponse:
    """Handle custom e-commerce exceptions using the generic error format."""

    # 4xx are warnings (client side), 5xx are errors (server side)
    level = "WARNING" if exc.status_code < 500 else "ERROR"
    
    logger.log(
        level,
        "E-commerce exception | method={} path={} status_code={} error_code={} message={}",
        request.method,
        request.url.path,
        exc.status_code,
        exc.error_code,
        exc.message
    )

    return error_respond(
        message=exc.message,
        status_code=exc.status_code,
        error_code=exc.error_code,
        details=exc.details if exc.details else None,
        request_id=request_id,
        headers=exc.headers,
    )


async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
    request_id: str
) -> JSONResponse:
    """Handle unexpected server-side exceptions."""

    logger.error(
        "Unexpected exception | method={} path={} type={} message={} traceback={}",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
        traceback.format_exc()
    )

    return error_respond(
        message="Internal server error",
        status_code=500,
        error_code="INTERNAL_ERROR",
        request_id=request_id,
    )


def add_exception_handlers(app: FastAPI) -> FastAPI:
    """Add exception handlers to FastAPI app."""

    # Starlette/FastAPI built-in exceptions — MUST be registered to override defaults
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
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
    app.add_exception_handler(BusinessRuleError, global_exception_handler)
    app.add_exception_handler(RateLimitError, global_exception_handler)
    app.add_exception_handler(DatabaseError, global_exception_handler)
    app.add_exception_handler(ExternalServiceError, global_exception_handler)
    app.add_exception_handler(PaymentError, global_exception_handler)
    app.add_exception_handler(EmailError, global_exception_handler)
    app.add_exception_handler(ServiceUnavailableError, global_exception_handler)
    app.add_exception_handler(ConfigurationError, global_exception_handler)

    logger.info("Centralized exception handlers registered successfully")
    return app
