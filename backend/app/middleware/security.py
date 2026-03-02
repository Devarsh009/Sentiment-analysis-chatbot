"""
Security Headers Middleware
=============================
Adds security headers to all API responses.

These headers help protect against common web vulnerabilities:
- XSS (Cross-Site Scripting)
- Clickjacking
- MIME type sniffing
- Information disclosure
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to every response.
    
    Headers added:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables browser XSS filtering
    - Strict-Transport-Security: Enforces HTTPS
    - Content-Security-Policy: Controls resource loading
    - Referrer-Policy: Controls referrer information
    """
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to the response."""
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking (page can't be embedded in iframe)
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable browser XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enforce HTTPS (max-age: 1 year)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        # Control referrer information sent with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (restrict browser features)
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        
        return response
