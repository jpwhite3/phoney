"""Common test fixtures and utilities for the Phoney test suite."""
import asyncio
import os
from typing import Dict, Generator, Any, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture

from phoney.app.main import app
from phoney.app.core import auth
from phoney.app.core.config import settings
from phoney.app.apis.provider import get_provider_list


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_env_vars(monkeypatch) -> None:
    """Mock environment variables for testing."""
    env_vars = {
        "ENV_STATE": "test",
        "HOST": "localhost",
        "PORT": "8000",
        "API_USERNAME": "test_user",
        "API_PASSWORD_HASH": "$2b$12$tufn64/0gSIHZMPLEHASH",
        "SECRET_KEY": "01234567890123456789012345678901",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "ALGORITHM": "HS256",
        "RATE_LIMIT_PER_MINUTE": "100",
        "SECURITY_HEADERS_ENABLED": "true"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def mock_user_db() -> Dict[str, Dict[str, Any]]:
    """Create a test user database for authentication."""
    password = "test_password"
    password_hash = auth.get_password_hash(password)
    return {
        "api_user": {
            "username": "api_user",
            "hashed_password": password_hash,
            "disabled": False
        }
    }


@pytest.fixture
def auth_headers(client: TestClient, mocker: MockFixture, mock_user_db: Dict) -> Dict[str, str]:
    """Get authentication headers for testing protected routes."""
    mocker.patch.object(auth, "users_db", mock_user_db)
    mocker.patch.object(auth, "authenticate_user", return_value=auth.UserInDB(**mock_user_db["api_user"]))
    
    response = client.post(
        "/token",
        data={"username": "api_user", "password": "test_password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers() -> Dict[str, str]:
    """Get API key headers for testing."""
    return {"X-API-Key": "test_api_key"}


@pytest.fixture
def mock_settings(monkeypatch) -> None:
    """Mock settings for testing."""
    monkeypatch.setattr(settings, "API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "ENV_STATE", "test")
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_MINUTE", 100)


@pytest.fixture
def faker_providers() -> list:
    """Get a list of available Faker providers for testing."""
    return get_provider_list()[:5]  # Limit to first 5 for faster tests


@pytest.fixture
def event_loop():
    """Create an event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[TestClient, None]:
    """Create an async test client for the FastAPI application."""
    async with TestClient(app) as test_client:
        yield test_client
