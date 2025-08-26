from functools import lru_cache
import json
import os
from typing import Any, ClassVar, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic v2 syntax."""

    # Environment configuration
    ENV_STATE: Literal["dev", "test", "prod"] = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API credentials
    API_USERNAME: str = "default_user"  # Default for testing
    API_PASSWORD_HASH: str = "$2b$12$tufn64/0gSIHZMPLEHASH"  # Default for testing
    API_KEY: str | None = None  # Optional API key for authentication

    # Security
    SECRET_KEY: str = "01234567890123456789012345678901"  # Default for testing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days by default
    ALGORITHM: str = "HS256"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60  # Default: 60 requests per minute
    RATE_LIMIT_BURST: int = 10  # Allow bursts of 10 requests

    # Security headers
    SECURITY_HEADERS_ENABLED: bool = True

    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Set different env file prefixes based on environment
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is set and has sufficient length."""
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be set and at least 32 characters long")
        return v

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: list[str], info: Any) -> list[str]:
        """Ensure CORS origins are properly formatted."""
        # In production, don't allow overly permissive CORS
        # Get current values from model_data in Pydantic v2
        env_state = info.data.get("ENV_STATE", "dev")
        if "*" in v and env_state == "prod":
            raise ValueError(
                "Wildcard CORS origin '*' is not allowed in production. "
                "Specify exact origins instead."
            )
        return v

    # Support for deserializing JSON strings from environment variables
    @field_validator("CORS_ORIGINS", "CORS_HEADERS", "CORS_METHODS", mode="before")
    @classmethod
    def parse_json_string(cls, v: Any) -> Any:
        """Parse JSON string values from environment variables."""
        if isinstance(v, str) and v.startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return v

    # Fix case sensitivity for LOG_LEVEL
    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def uppercase_log_level(cls, v: Any) -> Any:
        """Convert log level to uppercase for case-insensitive matching."""
        if isinstance(v, str):
            return v.upper()
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance with environment-specific configuration."""
    # Check if we're in a test environment
    if (
        os.environ.get("TESTING", "").lower() == "true"
        or os.environ.get("ENV_STATE", "").lower() == "test"
    ):
        # Use test-specific settings
        env_file = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "tests",
            ".env.test",
        )
        if os.path.exists(env_file):
            # Create settings with env file for Pydantic v2
            settings = Settings()
            settings.model_config = settings.model_config.copy()  # type: ignore
            return settings

    # Regular settings
    return Settings()


# Create settings instance - use this throughout the application
settings = get_settings()
