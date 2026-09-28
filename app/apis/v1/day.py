from typing import Annotated

from fastapi import APIRouter, Depends

from app.apis.response import ResponseEntity
from app.dependencies import (
    get_current_user_id,
    get_today_interactor,
    get_update_today_interactor,
)
from app.entities.day import DayEntity, DayUpdateEntity
from app.interactors.day.get_today import GetTodayInteractor
from app.interactors.day.update_today import UpdateTodayInput, UpdateTodayInteractor

day_router = APIRouter()


@day_router.get(path="/today", response_model=ResponseEntity[DayEntity])
async def get_today(
    interactor: Annotated[GetTodayInteractor, Depends(get_today_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    result = await interactor.execute(input=user_id)
    return ResponseEntity[DayEntity](data=result)


@day_router.patch(path="/today", response_model=ResponseEntity[DayEntity])
async def update_today(
    data: DayUpdateEntity,
    interactor: Annotated[UpdateTodayInteractor, Depends(get_update_today_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    result = await interactor.execute(
        input=UpdateTodayInput(user_id=user_id, data=data)
    )
    return ResponseEntity[DayEntity](data=result)
