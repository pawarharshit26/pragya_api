from fastapi import APIRouter

from app.apis.v1.day import day_router
from app.apis.v1.user import user_router

router = APIRouter(prefix="/v1")

router.include_router(router=user_router, prefix="/user", tags=["User"])
router.include_router(router=day_router, prefix="/day", tags=["Day"])
