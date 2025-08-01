"""Security middleware and utilities for the Phoney API."""
import time
from typing import Callable, Dict, List, Optional, Set, Tuple

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from .config import settings


class RateLimiter:
    """Rate limiter implementation to prevent abuse."""
    
    def __init__(self, limit: int = 60, window: int = 60):
        """Initialize with request limit per time window (in seconds)."""
        self.limit = limit
        self.window = window
        self._requests: Dict[str, List[float]] = {}
    
    def is_rate_limited(self, key: str) -> Tuple[bool, int, int]:
        """Check if a key is rate limited.
        
        Args:
            key: Identifier for the client (IP address)
            
        Returns:
            Tuple of (is_limited, requests_remaining, retry_after)
        """
        now = time.time()
        
        # Initialize if key not seen before
        if key not in self._requests:
            self._requests[key] = []
            
        # Remove requests outside the current window
        self._requests[key] = [t for t in self._requests[key] if now - t < self.window]
        
        # Check if under limit
        if len(self._requests[key]) < self.limit:
            self._requests[key].append(now)
            remaining = self.limit - len(self._requests[key])
            return False, remaining, 0
        
        # Calculate when the client can retry
        oldest = min(self._requests[key]) if self._requests[key] else now
        retry_after = max(0, int(self.window - (now - oldest)))
        return True, 0, retry_after
        
    def clean_old_data(self, max_items: int = 1000) -> None:
        """Periodically clean up old data to prevent memory leaks."""
        now = time.time()
        # Remove old entries
        for key in list(self._requests.keys()):
            self._requests[key] = [t for t in self._requests[key] if now - t < self.window]
            if not self._requests[key]:
                del self._requests[key]
                
        # If still too many items, remove oldest keys
        if len(self._requests) > max_items:
            # Sort keys by timestamp of last request
            sorted_keys = sorted(
                self._requests.keys(),
                key=lambda k: max(self._requests[k]) if self._requests[k] else 0
            )
            # Remove oldest entries
            for key in sorted_keys[:len(self._requests) - max_items]:
                del self._requests[key]


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for implementing security features."""
    
    def __init__(
        self, 
        app: FastAPI,
        rate_limit_per_minute: int = 60,
        excluded_paths: Optional[Set[str]] = None,
    ):
        """Initialize security middleware.
        
        Args:
            app: FastAPI application
            rate_limit_per_minute: Number of requests allowed per minute per IP
            excluded_paths: Paths excluded from rate limiting (e.g., health checks)
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(limit=rate_limit_per_minute, window=60)
        self.excluded_paths = excluded_paths or {"/", "/docs", "/redoc", "/openapi.json"}
        self._cleanup_counter = 0
        
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process each request through security checks."""
        # Occasionally clean up old rate limiter data
        self._cleanup_counter += 1
        if self._cleanup_counter > 1000:  # Clean up every 1000 requests
            self.rate_limiter.clean_old_data()
            self._cleanup_counter = 0
        
        # Skip rate limiting for excluded paths
        path = request.url.path
        if path in self.excluded_paths:
            return await self._add_security_headers(call_next, request)
        
        # Apply rate limiting based on client IP
        client_ip = _get_client_ip(request)
        is_limited, remaining, retry_after = self.rate_limiter.is_rate_limited(client_ip)
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                }
            )
        
        # Add rate limit headers to response
        response = await self._add_security_headers(call_next, request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    async def _add_security_headers(
        self, call_next: Callable, request: Request
    ) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)
        
        # Add security headers
        headers = response.headers
        
        # Content Security Policy
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        
        # Other security headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["X-XSS-Protection"] = "1; mode=block"
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        return response


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    headers = request.headers
    
    # Check for X-Forwarded-For header (common with proxies)
    if "X-Forwarded-For" in headers:
        # Get the first IP in the chain (the original client)
        return headers["X-Forwarded-For"].split(",")[0].strip()
    
    # Fall back to direct connection
    if request.client and request.client.host:
        return request.client.host
    
    # Last resort if nothing else works
    return "unknown"


def setup_security_middleware(app: FastAPI) -> None:
    """Add security middleware to the FastAPI application."""
    # Add the security middleware
    app.add_middleware(
        SecurityMiddleware,
        rate_limit_per_minute=settings.RATE_LIMIT_PER_MINUTE if hasattr(settings, 'RATE_LIMIT_PER_MINUTE') else 60,
    )
