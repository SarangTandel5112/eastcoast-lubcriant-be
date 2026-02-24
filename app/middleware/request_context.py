import time
import uuid
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match


def _format_size(size_bytes: int) -> str:
    """Format byte size into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    return f"{size_bytes / (1024 * 1024):.1f}MB"


def _resolve_route_name(request: Request) -> str | None:
    """Resolve the endpoint function name from the app router."""
    app = request.app
    for route in app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return getattr(route, "name", None)
    return None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to log every API call with rich context for debugging & monitoring."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ── Generate unique short request ID ──
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # ── Query params ──
        query_string = str(request.url.query) if request.url.query else ""
        full_path = f"{path}?{query_string}" if query_string else path

        # ── Route / endpoint name ──
        route_name = _resolve_route_name(request)
        route_label = f" ({route_name})" if route_name else ""

        # ── Log: Request started ──
        logger.info(
            "[{}] {} | \u27a1 {} {}{}",
            request_id, client_ip, method, full_path, route_label
        )

        # ── Process request with timing ──
        start = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            response.headers["X-Request-ID"] = request_id

            # ── Response size ──
            content_length = response.headers.get("content-length")
            size_str = _format_size(int(content_length)) if content_length else ""
            size_part = f" | {size_str}" if size_str else ""

            # ── Log: Request completed ──
            logger.info(
                "[{}] {} | \u2705 {} | {}ms{}",
                request_id, client_ip, response.status_code, duration_ms, size_part
            )

            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)

            # ── Log: Request failed ──
            logger.error(
                "[{}] {} | \u274c {} {}{} | {}ms | {}",
                request_id, client_ip, method, full_path, route_label,
                duration_ms, str(exc)
            )
            raise


def add_request_context(app):
    """Add request context middleware to FastAPI app."""
    app.add_middleware(RequestContextMiddleware)
    return app
