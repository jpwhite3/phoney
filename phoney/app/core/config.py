from typing import Literal, ClassVar, Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic v2 syntax."""
    # Environment configuration
    ENV_STATE: Literal["dev", "test", "prod"] = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API credentials
    API_USERNAME: str
    API_PASSWORD_HASH: str
    API_KEY: Optional[str] = None  # Optional API key for authentication
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days by default
    ALGORITHM: str = "HS256"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60  # Default: 60 requests per minute
    RATE_LIMIT_BURST: int = 10       # Allow bursts of 10 requests
    
    # Security headers
    SECURITY_HEADERS_ENABLED: bool = True
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    
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
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Ensure CORS origins are properly formatted."""
        # In production, don't allow overly permissive CORS
        if "*" in v and cls.ENV_STATE == "prod":
            raise ValueError(
                "Wildcard CORS origin '*' is not allowed in production. "
                "Specify exact origins instead."
            )
        return v


# Create settings instance
settings = Settings()
