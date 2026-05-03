from fastapi import APIRouter

from app.apis.v1.goal import goal_router
from app.apis.v1.structure import structure_router
from app.apis.v1.today import today_router
from app.apis.v1.user import user_router
from app.apis.v1.vision import vision_router

router = APIRouter(prefix="/v1")

router.include_router(router=user_router, prefix="/user", tags=["User"])
router.include_router(router=vision_router, prefix="/vision", tags=["Vision"])
router.include_router(router=structure_router, prefix="/structure", tags=["Structure"])
router.include_router(router=goal_router, prefix="/goal", tags=["Goal"])
router.include_router(router=today_router, prefix="/today", tags=["Today"])
