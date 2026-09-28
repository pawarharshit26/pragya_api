from datetime import date as date_

import structlog

from app.core.exceptions import BaseException
from app.entities.day import DayEntity, DayUpdateEntity
from app.repositories.day import DayRepository
from app.services.base import BaseService

logger = structlog.get_logger(__name__)


class DayService(BaseService):
    class DayException(BaseException):
        message = "Day Exception"

    def __init__(self, repo: DayRepository) -> None:
        self.repo = repo

    async def get_today(self, user_id: int) -> DayEntity:
        today = date_.today()
        day = await self.repo.get_by_date(user_id=user_id, date=today)
        if day:
            return day

        logger.info("Creating today's day", user_id=user_id, date=today)
        return await self.repo.create(user_id=user_id, date=today)

    async def update_today(self, user_id: int, input: DayUpdateEntity) -> DayEntity:
        today = date_.today()
        day = await self.repo.get_by_date(user_id=user_id, date=today)
        if not day:
            day = await self.repo.create(user_id=user_id, date=today)

        fields = input.model_dump(exclude_unset=True)
        if not fields:
            return day

        updated = await self.repo.update(day_id=day.id, user_id=user_id, fields=fields)
        assert updated is not None  # just created/fetched under the same user_id
        return updated
