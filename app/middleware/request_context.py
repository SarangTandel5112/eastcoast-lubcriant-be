import uuid
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context for tracing and logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request context to logger
        with logger.contextualize(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        ):
            # Log request start
            logger.info("Request started | method={} path={}", request.method, request.url.path)
            
            try:
                response = await call_next(request)
                
                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                
                # Log request completion
                logger.info(
                    "Request completed | status_code={} duration_ms={}",
                    response.status_code,
                    getattr(request.state, 'duration_ms', None)
                )
                
                return response
                
            except Exception as exc:
                # Log request failure
                logger.error("Request failed | error={}", str(exc))
                raise


def add_request_context(app):
    """Add request context middleware to FastAPI app."""
    app.add_middleware(RequestContextMiddleware)
    return app
