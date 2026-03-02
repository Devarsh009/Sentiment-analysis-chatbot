"""
Rate Limiting Middleware
=========================
Implements a sliding window rate limiter to prevent API abuse.

How it works:
- Tracks requests per client IP address
- Allows max N requests per time window
- Returns 429 Too Many Requests when limit is exceeded
- Automatically cleans up expired entries
"""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter middleware.
    
    Attributes:
        max_requests: Maximum requests allowed per window
        window_seconds: Time window in seconds
        requests: Dictionary tracking request timestamps per IP
    """
    
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            app: The ASGI application
            max_requests: Max requests per window (default: 60)
            window_seconds: Window duration in seconds (default: 60)
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # {ip_address: [timestamp1, timestamp2, ...]}
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request through the rate limiter.
        
        Steps:
        1. Get client IP
        2. Clean up expired timestamps
        3. Check if under the limit
        4. Allow or deny the request
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/"]:
            return await call_next(request)
        
        # Get client IP address
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Remove expired timestamps (outside the window)
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if current_time - ts < self.window_seconds
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            # Calculate retry-after time
            oldest_request = min(self.requests[client_ip])
            retry_after = int(self.window_seconds - (current_time - oldest_request))
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit exceeded. Max {self.max_requests} "
                             f"requests per {self.window_seconds} seconds.",
                    "retry_after": max(retry_after, 1),
                },
                headers={
                    "Retry-After": str(max(retry_after, 1)),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        # Record this request
        self.requests[client_ip].append(current_time)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract the client IP address from the request.
        Handles proxied requests (X-Forwarded-For header).
        """
        # Check for proxy headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
