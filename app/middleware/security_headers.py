"""Security headers middleware to protect against common web vulnerabilities."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    This helps protect against common web vulnerabilities:
    - XSS (Cross-Site Scripting)
    - Clickjacking
    - MIME type sniffing
    - Information leakage
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME type sniffing
        # Tells browsers to strictly follow the Content-Type header
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking attacks
        # Prevents the page from being embedded in iframes
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable browser's XSS filter
        # Modern browsers have built-in XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security (HSTS): Force HTTPS
        # Only applies if the site is accessed via HTTPS
        if not settings.debug:  # Only in production
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Content-Security-Policy: Prevent XSS and data injection attacks
        # Defines which sources of content are allowed to be loaded
        csp_directives = [
            "default-src 'self'",  # Only allow content from same origin
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts (for Swagger)
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (for Swagger)
            "img-src 'self' data: https:",  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URIs
            "connect-src 'self'",  # Allow AJAX/WebSocket only to same origin
            "frame-ancestors 'none'",  # Disallow embedding in frames (same as X-Frame-Options)
            "base-uri 'self'",  # Restrict base tag URLs
            "form-action 'self'",  # Restrict form submission targets
        ]

        # More restrictive CSP for production
        if not settings.debug:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",  # No inline scripts in production
                "style-src 'self'",  # No inline styles in production
                "img-src 'self' data: https:",
                "font-src 'self'",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "upgrade-insecure-requests",  # Upgrade HTTP to HTTPS
            ]

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer-Policy: Control referrer information
        # Prevents leaking sensitive information in the Referer header
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        # Disable potentially dangerous features
        permissions = [
            "geolocation=()",  # Disable geolocation
            "microphone=()",  # Disable microphone
            "camera=()",  # Disable camera
            "payment=()",  # Disable payment API
            "usb=()",  # Disable USB access
            "magnetometer=()",  # Disable magnetometer
            "gyroscope=()",  # Disable gyroscope
            "accelerometer=()",  # Disable accelerometer
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # Remove server information header (don't advertise technology stack)
        if "Server" in response.headers:
            del response.headers["Server"]

        # Remove X-Powered-By header if present
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


def add_security_headers(app):
    """
    Add security headers middleware to FastAPI application.

    Usage in main.py:
        from app.middleware.security_headers import add_security_headers
        add_security_headers(app)
    """
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("Security headers middleware configured")
    return app
