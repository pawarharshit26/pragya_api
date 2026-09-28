from fastapi import APIRouter

from app.apis.v1.user import user_router

router = APIRouter(prefix="/v1")

router.include_router(router=user_router, prefix="/user", tags=["User"])
