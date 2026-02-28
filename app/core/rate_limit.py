"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings


# Initialize limiter with Redis backend if available, otherwise use in-memory
def get_limiter_key(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses IP address, but can be extended to use user ID for authenticated requests.
    """
    # For authenticated requests, prefer user ID over IP
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    # Fall back to IP address
    return get_remote_address(request)


# Configure limiter
if settings.redis_url:
    # Use Redis for distributed rate limiting (recommended for production)
    storage_uri = settings.redis_url
    logger.info("Rate limiting configured with Redis backend")
else:
    # Use in-memory storage (single-instance only)
    storage_uri = "memory://"
    logger.warning(
        "Rate limiting using in-memory storage. "
        "For production with multiple workers, configure Redis via REDIS_URL"
    )

limiter = Limiter(
    key_func=get_limiter_key,
    default_limits=["200/minute", "5000/hour"],  # Global limits
    storage_uri=storage_uri,
    strategy="fixed-window",  # or "moving-window" for more accuracy
    headers_enabled=True,  # Add rate limit headers to responses
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    Returns consistent error format matching the application's error response structure.
    """
    from app.common.response import error_respond

    logger.warning(
        "Rate limit exceeded | path={} ip={} limit={}",
        request.url.path,
        get_remote_address(request),
        exc.detail
    )

    return error_respond(
        message="Too many requests. Please try again later.",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED",
        details={
            "limit": exc.detail,
            "retryAfter": "60 seconds"
        }
    )


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application.

    Usage in main.py:
        from app.core.rate_limit import setup_rate_limiting
        setup_rate_limiting(app)
    """
    # Add limiter to app state
    app.state.limiter = limiter

    # Add custom exception handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    logger.info("Rate limiting middleware configured")
    return app


# Predefined rate limit decorators for common use cases
class RateLimits:
    """Predefined rate limits for different endpoint types."""

    # Authentication endpoints - stricter limits to prevent brute force
    AUTH_LOGIN = "5/minute"  # Restored
    AUTH_REGISTER = "3/minute"  # Restored
    AUTH_REFRESH = "10/minute"  # 10 token refreshes per minute
    AUTH_PASSWORD_RESET = "3/hour"  # 3 password reset requests per hour

    # API endpoints - moderate limits
    API_READ = "60/minute"  # Read operations
    API_WRITE = "30/minute"  # Create/Update operations
    API_DELETE = "10/minute"  # Delete operations

    # Public endpoints - more permissive
    PUBLIC = "100/minute"

    # Admin endpoints - higher limits
    ADMIN = "200/minute"

    # Search/Query endpoints - moderate to prevent scraping
    SEARCH = "20/minute"
