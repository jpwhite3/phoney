from typing import Dict, List, Optional, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from faker import Faker
from pydantic import ValidationError

from ..apis.models import (
    FakeDataProvider, FakerRequest, FakerResponse, 
    ProviderInfo, ProviderDetail, GeneratorInfo
)
from ..apis.provider import (
    get_provider_url_map, get_provider, get_generator_list,
    get_provider_metadata, get_provider_list
)
from ..core.auth import get_current_active_user, User

# Create API router with versioning tags and optional authentication
router = APIRouter(
    prefix="/api/v1",
    tags=["faker"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/providers", 
    summary="List all available Faker providers",
    response_model=List[ProviderInfo],
    response_model_exclude_none=True
)
async def list_providers() -> List[ProviderInfo]:
    """List all available Faker providers with their metadata."""
    providers = []
    url_map = get_provider_url_map()
    
    for provider_name in get_provider_list():
        try:
            provider_class = get_provider(provider_name)
            generators = get_generator_list(provider_class)
            providers.append(ProviderInfo(
                name=provider_name,
                url=f"/api/v1/provider/{provider_name}",
                generator_count=len(generators)
            ))
        except Exception:
            continue
            
    return providers


@router.get(
    "/provider/{provider_name}", 
    summary="Get details about a specific provider",
    response_model=ProviderDetail
)
async def list_generators(
    provider_name: FakeDataProvider = Path(..., description="Name of the Faker provider")
) -> ProviderDetail:
    """Get details about a specific provider including all available generators."""
    try:
        provider_class = get_provider(provider_name)
        generators = get_generator_list(provider_class)
        generator_urls = {
            gen: f"/api/v1/provider/{provider_name}/{gen}" 
            for gen in generators
        }
        
        return ProviderDetail(
            provider=str(provider_name.value),
            generators=generators,
            generator_urls=generator_urls
        )
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Provider '{provider_name}' not found or error: {str(e)}"
        )


@router.get(
    "/provider/{provider_name}/{generator_name}", 
    summary="Generate fake data using a specific generator",
    response_model=FakerResponse
)
async def generate_data(
    provider_name: FakeDataProvider = Path(..., description="Name of the Faker provider"),
    generator_name: str = Path(..., description="Name of the generator method"),
    locale: Optional[str] = Query(None, description="Optional locale for the Faker instance"),
    seed: Optional[int] = Query(None, description="Optional seed for reproducible results"),
    count: int = Query(1, ge=1, le=100, description="Number of items to generate")
) -> FakerResponse:
    """Generate fake data using a specific Faker provider and generator."""
    try:
        # Create Faker instance with requested locale
        fake = Faker(locale=locale) if locale else Faker()
        
        # Set seed if provided
        if seed is not None:
            fake.seed_instance(seed)
        
        # Verify generator exists
        if not hasattr(fake, generator_name):
            raise HTTPException(
                status_code=404,
                detail=f"Generator '{generator_name}' not found in provider '{provider_name}'"
            )
            
        generator = getattr(fake, generator_name)
        
        # Generate requested number of items
        if count == 1:
            data = generator()
        else:
            data = [generator() for _ in range(count)]
            
        return FakerResponse(
            provider=str(provider_name.value),
            generator=generator_name,
            data=data,
            count=count
        )
        
    except AttributeError:
        raise HTTPException(
            status_code=404,
            detail=f"Generator '{generator_name}' not found in provider '{provider_name}'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating data: {str(e)}"
        )


@router.post(
    "/generate",
    summary="Advanced fake data generation with parameters",
    response_model=FakerResponse
)
async def advanced_generate(
    request: FakerRequest,
    current_user: User = Depends(get_current_active_user)
) -> FakerResponse:
    """Generate fake data with advanced options and parameters."""
    try:
        # Create Faker instance with requested locale
        fake = Faker(locale=request.locale) if request.locale else Faker()
        
        # Set seed if provided
        if request.seed is not None:
            fake.seed_instance(request.seed)
            
        # Enable unique mode if requested
        if request.unique:
            fake.unique.enable()
            
        provider_name = request.provider.value
        generator_name = request.generator
        
        # Verify generator exists
        if not hasattr(fake, generator_name):
            raise HTTPException(
                status_code=404,
                detail=f"Generator '{generator_name}' not found in provider '{provider_name}'"
            )
            
        generator = getattr(fake, generator_name)
        
        # Extract parameters
        args = []
        kwargs = {}
        if request.params:
            args = request.params.args
            kwargs = request.params.kwargs
            
        # Generate requested number of items
        if request.count == 1:
            data = generator(*args, **kwargs)
        else:
            data = [generator(*args, **kwargs) for _ in range(request.count)]
            
        # Disable unique mode if it was enabled
        if request.unique:
            fake.unique.disable()
            
        return FakerResponse(
            provider=provider_name,
            generator=generator_name,
            data=data,
            count=request.count
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content={"detail": e.errors()}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating data: {str(e)}"
        )
