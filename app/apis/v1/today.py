from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from app.apis.response import ResponseEntity
from app.dependencies import get_current_user_id, get_get_today_interactor
from app.entities.today import TodayEntity
from app.interactors.today.get import GetTodayInput, GetTodayInteractor

today_router = APIRouter()


@today_router.get(path="/", response_model=ResponseEntity[TodayEntity])
async def get_today(
    interactor: Annotated[GetTodayInteractor, Depends(get_get_today_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    result = await interactor.execute(
        input=GetTodayInput(user_id=user_id, date=date.today())
    )
    return ResponseEntity[TodayEntity](data=result)
