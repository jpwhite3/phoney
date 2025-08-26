import secrets
import time

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from .apis.models import BulkTemplateRequest, BulkTemplateResponse, SimpleFakeResponse
from .apis.template_engine import TemplateEngine
from .core import auth
from .core.config import settings
from .core.security import setup_security_middleware
from .routes import views

# Create FastAPI application with metadata for documentation
app = FastAPI(
    title="Phoney - Faker API",
    description="""🚀 **The easiest way to generate fake data for testing!**
    
    Perfect for developers learning automated testing - no complex setup needed.
    
    ## 🎨 Try It Now!
    
    **Simple API** - Just specify what you want:
    - Name: `GET /fake/name` → "Sarah Johnson"
    - Email: `GET /fake/email` → "user@example.com"
    - Multiple items: `GET /fake/name?count=5` → ["John", "Jane", "Bob", ...]
    - Localized: `GET /fake/address?locale=fr_FR` → French address
    - Reproducible: `GET /fake/name?seed=42` → Always same result
    
    ## 🔧 Features
    
    * 🎯 **288+ Data Types**: Names, emails, addresses, companies, dates, text, IDs...
    * 🤖 **Smart Detection**: Ask for `phone` or `telephone` - both work!
    * 🌍 **50+ Locales**: Generate data in English, French, German, Japanese, etc.
    * 🔄 **Bulk Generation**: Get 1 to 100 items in a single request
    * ⚙️ **Reproducible**: Use seeds for consistent test data
    * ⚡ **Fast**: Optimized for high-volume test data generation
    
    ## 📚 Quick Examples
    
    ```bash
    # Basic usage
    curl /fake/name
    curl /fake/email
    curl /fake/phone
    
    # Multiple items
    curl '/fake/email?count=10'
    
    # Different languages
    curl '/fake/name?locale=ja_JP'    # Japanese names
    curl '/fake/address?locale=de_DE'  # German addresses
    
    # Reproducible (great for testing!)
    curl '/fake/name?seed=123'         # Always same name
    ```
    
    ## 🔍 Discovery
    
    - **List all generators**: `GET /generators`
    - **Full tutorial**: See README.md and TUTORIAL.md
    - **Multiple API styles**: Simple, Provider-based, and Advanced with auth
    
    💡 **Perfect for**: Unit tests, integration tests, API testing, database seeding, demos
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
        "examples": {
            "simple_api": {
                "get_name": "/fake/name",
                "get_emails": "/fake/email?count=5",
                "get_french_address": "/fake/address?locale=fr_FR",
            },
            "template_api": {
                "bulk_users": "POST /template",
                "template_examples": "/template/examples",
            },
            "list_generators": "/generators",
            "advanced_api": "/api/v1/providers",
        },
    }


# Health check endpoint for monitoring
@app.get("/health", tags=["status"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Simple routes for beginners (no prefix)
@app.get(
    "/fake/{generator}",
    summary="Generate fake data (simplified API)",
    tags=["simple"],
    response_model=SimpleFakeResponse,
)
async def simple_generate_root(
    generator: str = Path(
        ...,
        description="What kind of data you want",
        examples={
            "name": {"summary": "Person name", "value": "name"},
            "email": {"summary": "Email address", "value": "email"},
            "phone": {"summary": "Phone number", "value": "phone"},
            "address": {"summary": "Street address", "value": "address"},
            "company": {"summary": "Company name", "value": "company"},
        },
    ),
    count: int = Query(
        1,
        ge=1,
        le=100,
        description="Number of items to generate",
        examples=[1, 5, 10, 50],
    ),
    locale: str | None = Query(
        None,
        description="Language/region for localized data",
        examples=["en_US", "fr_FR", "de_DE", "ja_JP", "es_ES"],
    ),
    seed: int | None = Query(
        None,
        description="Seed for reproducible results (same seed = same data)",
        examples=[42, 123, 456],
    ),
):
    """🎯 **Generate fake data instantly!**

    Just specify what you want and get realistic fake data for testing.

    **Popular generators:**
    - `name`, `email`, `phone`, `address` - Contact info
    - `company`, `job` - Business data
    - `date`, `time`, `url` - Common data types
    - `text`, `paragraph`, `word` - Content
    - `uuid4`, `ssn`, `credit_card_number` - IDs & numbers

    **Pro tips:**
    - Use `?count=10` for multiple items
    - Use `?locale=fr_FR` for French data
    - Use `?seed=42` for reproducible results
    - Try `/generators` to see all 288+ options!
    """
    # Import here to avoid circular imports
    from .routes.views import simple_generate

    return await simple_generate(generator, count, locale, seed)


@app.get(
    "/generators",
    summary="List all available generators",
    tags=["simple"],
    response_model=list[str],
)
async def list_all_generators_root():
    """Get a simple list of all available generator names for easy discovery."""
    from .routes.views import list_all_generators

    return await list_all_generators()


@app.post(
    "/template",
    summary="Simple bulk template generation (no auth required)",
    tags=["simple", "templates"],
    response_model=BulkTemplateResponse,
)
async def simple_template_generate(
    request: BulkTemplateRequest,
) -> BulkTemplateResponse:
    """Generate bulk data using templates - perfect for beginners!

    🎨 **Easy Template Syntax:**
    - `{{name}}` - Generate names
    - `{{email}}` - Generate emails
    - `{{[name]:count=3}}` - Generate arrays
    - `{{random_int:min=1,max=100}}` - With parameters

    🚀 **Perfect for:**
    - Database seeding
    - Test data generation
    - Demo applications
    - API testing

    💡 **Examples:**
    ```json
    {
      "template": {
        "name": "{{name}}",
        "email": "{{email}}",
        "friends": "{{[name]:count=3}}"
      },
      "count": 10
    }
    ```
    """
    # Limit count for unauthenticated requests
    if request.count > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum count for simple template endpoint is 1000. Use /api/v1/template/generate with authentication for larger datasets.",
        )

    start_time = time.time()
    template_engine = TemplateEngine()

    try:
        # Validate template first
        is_valid, errors, warnings = template_engine.validate_template(request.template)

        if not is_valid:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Template validation failed",
                    "errors": [
                        {
                            "field": error.field,
                            "generator": error.generator,
                            "message": error.message,
                            "suggestions": error.suggestions,
                        }
                        for error in errors
                    ],
                    "help": "Check /template/examples for syntax help",
                },
            )

        # Process template
        results = template_engine.process_template(
            template=request.template,
            count=request.count,
            locale=request.locale,
            seed=request.seed,
            unique=request.unique,
        )

        execution_time = (time.time() - start_time) * 1000

        # Format output (simple endpoint only supports JSON)
        return BulkTemplateResponse(
            generated_count=len(results),
            requested_count=request.count,
            data=results,
            format="json",
            locale=request.locale or "en_US",
            seed=request.seed,
            execution_time_ms=execution_time,
            warnings=warnings if warnings else [],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Template processing error: {str(e)}"
        )


@app.get(
    "/template/examples",
    summary="Template examples and help",
    tags=["simple", "templates"],
)
async def simple_template_examples():
    """Get template examples for the simple template API."""
    return {
        "basic_example": {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}",
                "age": "{{random_int:min=18,max=80}}",
            },
            "count": 5,
        },
        "array_example": {
            "template": {
                "company": "{{company}}",
                "employees": "{{[name]:count=3}}",
                "products": "{{[catch_phrase]:count=2}}",
            },
            "count": 3,
        },
        "syntax_guide": {
            "simple_placeholder": "{{generator}} - Basic fake data",
            "with_parameters": "{{generator:param=value}} - Customized data",
            "arrays": "{{[generator]:count=5}} - Generate arrays",
        },
        "quick_start": "POST /template with your template structure!",
    }


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
        "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        "apiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
