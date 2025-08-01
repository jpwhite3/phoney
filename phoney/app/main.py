from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyHeader
import secrets

from .routes import views
from .core import auth
from .core.config import settings
from .core.security import setup_security_middleware

# Create FastAPI application with metadata for documentation
app = FastAPI(
    title="Phoney - Faker API",
    description="""A RESTful API for generating fake data using Python's Faker library.
    
    ## Features
    
    * Browse all available Faker providers
    * Generate fake data with any Faker generator
    * Customize generation with locale, seed, and count parameters
    * Advanced options with POST endpoint (requires authentication)
    * Rate limiting to prevent abuse
    * Comprehensive security headers
    
    ## Authentication
    
    Some endpoints require authentication using OAuth2 password flow.
    Get your token at the `/token` endpoint.
    """,
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# API key header for optional API key authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Generate a random API key if not provided in settings
API_KEY = getattr(settings, "API_KEY", secrets.token_urlsafe(32))

# Set CORS middleware with settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Add security middleware (rate limiting and security headers)
setup_security_middleware(app)

# Exception handler for clean error responses
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Don't expose details in production
    if settings.ENV_STATE == "prod":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )
    
    # In development, provide more information
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# API key verification dependency
async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    """Verify the API key if provided."""
    if api_key and api_key == API_KEY:
        return True
    return None

# Root endpoint for API information
@app.get("/", tags=["status"])
async def root():
    """Get API information and status."""
    return {
        "name": "Phoney - Faker API",
        "version": "0.2.0",
        "status": "online",
        "documentation": "/docs",
        "providers_endpoint": "/api/v1/providers"
    }

# Health check endpoint for monitoring
@app.get("/health", tags=["status"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

# Include routers
app.include_router(auth.router)
app.include_router(views.router)

# Custom OpenAPI schema with additional metadata
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add additional metadata
    openapi_schema["info"]["x-logo"] = {
        "url": "https://faker.readthedocs.io/en/master/_static/faker_logo.png"
    }
    
    # Add security schemes
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
    
app.openapi = custom_openapi
