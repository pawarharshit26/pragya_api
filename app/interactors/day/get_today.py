from app.entities.day import DayEntity
from app.interactors.base import BaseInteractor
from app.services.day import DayService


class GetTodayInteractor(BaseInteractor[int, DayEntity]):
    def __init__(self, day_service: DayService) -> None:
        self.day_service = day_service

    async def execute(self, input: int) -> DayEntity:
        return await self.day_service.get_today(user_id=input)
