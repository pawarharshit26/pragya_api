from datetime import date

from app.entities.base import BaseEntity
from app.entities.today import TodayEntity
from app.interactors.base import BaseInteractor
from app.services.today import TodayService


class GetTodayInput(BaseEntity):
    user_id: int
    date: date


class GetTodayInteractor(BaseInteractor[GetTodayInput, TodayEntity]):
    def __init__(self, today_service: TodayService) -> None:
        self.today_service = today_service

    async def execute(self, input: GetTodayInput) -> TodayEntity:
        return await self.today_service.get(user_id=input.user_id, for_date=input.date)
