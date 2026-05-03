from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.apis.exceptions import BaseAPIException
from app.apis.response import ResponseEntity
from app.dependencies import get_current_user_id, get_get_active_vision_interactor
from app.entities.vision import VisionEntity
from app.interactors.vision.get_active import GetActiveVisionInteractor

vision_router = APIRouter()


@vision_router.get(path="/me", response_model=ResponseEntity[VisionEntity])
async def get_active_vision(
    interactor: Annotated[
        GetActiveVisionInteractor, Depends(get_get_active_vision_interactor)
    ],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    try:
        result = await interactor.execute(input=user_id)
        return ResponseEntity[VisionEntity](data=result)
    except GetActiveVisionInteractor.VisionNotFoundException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_404_NOT_FOUND
        ) from e
