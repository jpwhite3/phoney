"""Test suite for security middleware and utilities."""
import time
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from phoney.app.core.security import (
    RateLimiter,
    SecurityMiddleware,
    _get_client_ip,
    setup_security_middleware,
)


class TestRateLimiter:
    """Test the RateLimiter class."""

    def test_init(self):
        """Test initialization with custom parameters."""
        limiter = RateLimiter(limit=100, window=30)
        assert limiter.limit == 100
        assert limiter.window == 30
        assert limiter._requests == {}

    def test_is_rate_limited_first_request(self):
        """Test that first request is not rate limited."""
        limiter = RateLimiter(limit=5, window=10)
        is_limited, remaining, retry_after = limiter.is_rate_limited("test_ip")

        assert is_limited is False
        assert remaining == 4
        assert retry_after == 0
        assert len(limiter._requests["test_ip"]) == 1

    def test_is_rate_limited_under_limit(self):
        """Test requests under the limit are allowed."""
        limiter = RateLimiter(limit=5, window=10)

        # Make 3 requests
        for _ in range(3):
            is_limited, remaining, retry_after = limiter.is_rate_limited("test_ip")
            assert is_limited is False

        # Should have 2 remaining
        assert remaining == 2
        assert len(limiter._requests["test_ip"]) == 3

    def test_is_rate_limited_at_limit(self):
        """Test that requests at the limit are rate limited."""
        limiter = RateLimiter(limit=3, window=10)

        # Make 3 requests (reaching the limit)
        for _ in range(3):
            limiter.is_rate_limited("test_ip")

        # Next request should be limited
        is_limited, remaining, retry_after = limiter.is_rate_limited("test_ip")
        assert is_limited is True
        assert remaining == 0
        assert retry_after > 0

    def test_clean_old_data(self):
        """Test cleaning of old data."""
        limiter = RateLimiter(limit=10, window=1)

        # Add requests for multiple IPs
        limiter.is_rate_limited("ip1")
        limiter.is_rate_limited("ip2")
        limiter.is_rate_limited("ip3")

        assert len(limiter._requests) == 3

        # Wait for window to expire
        time.sleep(1.1)

        # Clean old data
        limiter.clean_old_data()

        # All data should be removed as it's older than the window
        assert limiter._requests == {}

    def test_clean_old_data_max_items(self):
        """Test cleaning when too many items are present."""
        limiter = RateLimiter(limit=10, window=60)

        # Add requests for multiple IPs
        for i in range(10):
            limiter.is_rate_limited(f"ip{i}")

        # Add a much newer request for one IP
        limiter._requests["newest_ip"] = [time.time()]

        # Clean with max_items=5
        limiter.clean_old_data(max_items=5)

        # Should keep only 5 items including the newest one
        assert len(limiter._requests) <= 5
        assert "newest_ip" in limiter._requests


class TestSecurityMiddleware:
    """Test the SecurityMiddleware class."""

    @pytest.fixture
    def app(self):
        """Create a test FastAPI application."""
        return FastAPI()

    @pytest.fixture
    def middleware(self, app):
        """Create a SecurityMiddleware instance."""
        return SecurityMiddleware(
            app, rate_limit_per_minute=10, excluded_paths={"/test/excluded"}
        )

    @pytest.mark.asyncio
    async def test_excluded_path(self, middleware):
        """Test that excluded paths bypass rate limiting."""
        request = Mock(spec=Request)
        request.url.path = "/test/excluded"

        # Mock call_next
        async def mock_call_next(request):
            return Response()

        # Call dispatch
        response = await middleware.dispatch(request, mock_call_next)

        # Should bypass rate limiting and add security headers
        assert isinstance(response, Response)
        assert response.headers.get("Content-Security-Policy") is not None
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    @pytest.mark.asyncio
    async def test_rate_limited_request(self, middleware):
        """Test that requests are rate limited after exceeding the limit."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.client.host = "192.168.1.1"

        # Mock call_next
        async def mock_call_next(request):
            return Response()

        # Make requests up to the limit
        for _ in range(10):
            response = await middleware.dispatch(request, mock_call_next)
            assert not isinstance(response, JSONResponse)

        # Next request should be rate limited
        response = await middleware.dispatch(request, mock_call_next)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.body.decode()
        assert "Retry-After" in response.headers

    @pytest.mark.asyncio
    async def test_add_security_headers(self, middleware):
        """Test that security headers are added to the response."""
        request = Mock(spec=Request)

        # Create a mock response
        mock_response = Response()

        # Mock call_next to return the mock response
        async def mock_call_next(request):
            return mock_response

        # Call _add_security_headers
        response = await middleware._add_security_headers(mock_call_next, request)

        # Check that security headers are added
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers


def test_get_client_ip_from_forwarded():
    """Test extracting client IP from X-Forwarded-For header."""
    request = Mock(spec=Request)
    request.headers = Headers({"X-Forwarded-For": "192.168.1.2, 10.0.0.1"})

    ip = _get_client_ip(request)
    assert ip == "192.168.1.2"


def test_get_client_ip_direct():
    """Test extracting client IP from direct connection."""
    request = Mock(spec=Request)
    request.headers = Headers({})
    request.client.host = "192.168.1.3"

    ip = _get_client_ip(request)
    assert ip == "192.168.1.3"


def test_get_client_ip_fallback():
    """Test fallback when no client IP is available."""
    request = Mock(spec=Request)
    request.headers = Headers({})
    request.client = None

    ip = _get_client_ip(request)
    assert ip == "unknown"


def test_setup_security_middleware(mocker):
    """Test adding security middleware to a FastAPI application."""
    mock_app = Mock(spec=FastAPI)
    mock_add_middleware = mocker.patch.object(mock_app, "add_middleware")

    setup_security_middleware(mock_app)

    mock_add_middleware.assert_called_once_with(
        SecurityMiddleware,
        rate_limit_per_minute=60,  # Default value
    )
