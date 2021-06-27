from typing import Dict

from ..apis.api_a.mainmod import main_func as main_func_a
from ..core.auth import get_current_user
from fastapi import APIRouter, Depends


router = APIRouter()


@router.get("/api_a/{num}", tags=["api_a"])
async def view_a(num: int, auth=Depends(get_current_user)) -> Dict[str, int]:
    return main_func_a(num)


@router.get("/generators/", tags=["generators"])
async def get_generators():
    return {"available_generators": [], "example_request": "/generator/address?count=5"}
