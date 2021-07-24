from typing import Dict

from fastapi import APIRouter, Depends

from ..apis.models import FakeDataProvider
from ..apis.provider import get_provider_url_map, get_provider
from ..core.auth import get_current_user

router = APIRouter()


@router.get("/api_a/{num}", tags=["v1"])
async def view_a(num: int, auth=Depends(get_current_user)) -> Dict[str, int]:
    return {'received': num}


@router.get("/providers/", tags=["v1"])
async def list_providers() -> Dict[str, str]:
    return get_provider_url_map()


@router.get("/provider/{provider_name}", tags=["v1"])
async def list_generators(provider_name: FakeDataProvider):
    provider = get_provider(provider_name)
    return {"provider_name": provider_name, "message": "Deep Learning FTW!"}

