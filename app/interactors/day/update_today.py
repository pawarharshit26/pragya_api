from app.entities.base import BaseEntity
from app.entities.day import DayEntity, DayUpdateEntity
from app.interactors.base import BaseInteractor
from app.services.day import DayService


class UpdateTodayInput(BaseEntity):
    user_id: int
    data: DayUpdateEntity


class UpdateTodayInteractor(BaseInteractor[UpdateTodayInput, DayEntity]):
    def __init__(self, day_service: DayService) -> None:
        self.day_service = day_service

    async def execute(self, input: UpdateTodayInput) -> DayEntity:
        return await self.day_service.update_today(
            user_id=input.user_id, input=input.data
        )
