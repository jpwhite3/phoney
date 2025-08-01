"""Test suite for configuration settings."""
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from phoney.app.core.config import Settings


class TestSettings:
    """Test the Settings class configuration."""

    def test_default_values(self, mock_env_vars):
        """Test default values are properly set."""
        settings = Settings()
        
        # Check default environment settings
        assert settings.ENV_STATE == "test"
        assert settings.HOST == "localhost"
        assert settings.PORT == 8000
        
        # Check security defaults
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert settings.RATE_LIMIT_PER_MINUTE == 100
        assert settings.SECURITY_HEADERS_ENABLED is True

    def test_validate_secret_key_valid(self):
        """Test that a valid secret key passes validation."""
        valid_key = "a" * 32  # 32 character key
        settings = Settings(SECRET_KEY=valid_key)
        assert settings.SECRET_KEY == valid_key

    def test_validate_secret_key_invalid(self):
        """Test that an invalid secret key fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY="tooshort")
        
        # Check error message
        errors = exc_info.value.errors()
        assert any("SECRET_KEY must be set" in error["msg"] for error in errors)

    def test_validate_cors_origins_dev(self):
        """Test that wildcard CORS origins are allowed in development."""
        settings = Settings(
            ENV_STATE="dev",
            CORS_ORIGINS=["*"],
            SECRET_KEY="a" * 32,
            API_USERNAME="test",
            API_PASSWORD_HASH="test"
        )
        assert settings.CORS_ORIGINS == ["*"]

    def test_validate_cors_origins_prod_specific(self):
        """Test that specific CORS origins are allowed in production."""
        settings = Settings(
            ENV_STATE="prod",
            CORS_ORIGINS=["https://example.com", "https://api.example.com"],
            SECRET_KEY="a" * 32,
            API_USERNAME="test",
            API_PASSWORD_HASH="test"
        )
        assert settings.CORS_ORIGINS == ["https://example.com", "https://api.example.com"]

    def test_validate_cors_origins_prod_wildcard(self):
        """Test that wildcard CORS origins are rejected in production."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                ENV_STATE="prod",
                CORS_ORIGINS=["*"],
                SECRET_KEY="a" * 32,
                API_USERNAME="test",
                API_PASSWORD_HASH="test"
            )
        
        # Check error message
        errors = exc_info.value.errors()
        assert any("Wildcard CORS origin '*' is not allowed in production" in error["msg"] for error in errors)

    def test_log_level_validation(self):
        """Test that log level is validated correctly."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            settings = Settings(
                LOG_LEVEL=level,
                SECRET_KEY="a" * 32,
                API_USERNAME="test",
                API_PASSWORD_HASH="test"
            )
            assert settings.LOG_LEVEL == level
        
        # Invalid log level
        with pytest.raises(ValidationError):
            Settings(
                LOG_LEVEL="INVALID",
                SECRET_KEY="a" * 32,
                API_USERNAME="test",
                API_PASSWORD_HASH="test"
            )

    def test_settings_from_env_file(self, tmp_path):
        """Test loading settings from an environment file."""
        env_file = tmp_path / ".env"
        env_content = """
        ENV_STATE=test
        HOST=127.0.0.1
        PORT=9000
        API_USERNAME=env_user
        API_PASSWORD_HASH=env_hash
        SECRET_KEY=abcdefghijklmnopqrstuvwxyz123456
        RATE_LIMIT_PER_MINUTE=50
        """
        env_file.write_text(env_content)
        
        with patch.object(Settings.model_config, "env_file", str(env_file)):
            settings = Settings()
            assert settings.ENV_STATE == "test"
            assert settings.HOST == "127.0.0.1"
            assert settings.PORT == 9000
            assert settings.API_USERNAME == "env_user"
            assert settings.API_PASSWORD_HASH == "env_hash"
            assert settings.SECRET_KEY == "abcdefghijklmnopqrstuvwxyz123456"
            assert settings.RATE_LIMIT_PER_MINUTE == 50
