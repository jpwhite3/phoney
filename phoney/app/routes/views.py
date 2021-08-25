from typing import Dict

from fastapi import APIRouter, Depends

from ..apis.models import FakeDataProvider
from ..apis.provider import get_provider_url_map, get_provider, get_generator_list
from ..core.auth import get_current_user
from faker.factory import Factory

router = APIRouter()


@router.get("/api_a/{num}", tags=["v1"])
async def view_a(num: int, auth=Depends(get_current_user)) -> Dict[str, int]:
    return {"received": num}


@router.get("/providers/", tags=["v1"])
async def list_providers() -> Dict[str, str]:
    return get_provider_url_map()


@router.get("/provider/{provider_name}", tags=["v1"])
async def list_generators(provider_name: FakeDataProvider) -> Dict[str, str]:
    provider = get_provider(provider_name)
    generators = get_generator_list(provider)
    return {"provider": provider_name, "generators": generators}


@router.get("/provider/{provider_name}/{generator_name}", tags=["v1"])
async def generate_data(provider_name: FakeDataProvider, generator_name: str) -> Dict[str, str]:
    fake = Factory.create()
    generator = getattr(fake, generator_name)
    return {"provider": provider_name, "generator": generator_name, "data": generator()}
