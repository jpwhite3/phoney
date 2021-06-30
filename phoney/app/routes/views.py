from typing import Dict

from fastapi import APIRouter, Depends

from ..apis.api_a.mainmod import main_func as main_func_a
from ..apis.models import FakeDataProvider
from ..core.auth import get_current_user
from ..apis.provider import get_provider_url_map

router = APIRouter()


@router.get("/api_a/{num}", tags=["v1"])
async def view_a(num: int, auth=Depends(get_current_user)) -> Dict[str, int]:
    return main_func_a(num)

@router.get("/providers/", tags=["v1"])
async def get_providers():
    return get_provider_url_map()

@router.get("/provider/{provider_name}", tags=["v1"])
async def get_provider(provider_name: FakeDataProvider):
    return {"provider_name": provider_name, "message": "Deep Learning FTW!"}

