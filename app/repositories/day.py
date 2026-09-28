from datetime import date as date_
from typing import Any

from sqlalchemy import select

from app.db.models.day import Day
from app.entities.day import DayEntity
from app.repositories.base import BaseRepository


class DayRepository(BaseRepository):
    async def get_by_date(self, user_id: int, date: date_) -> DayEntity | None:
        result = await self.db.execute(
            select(Day).where(
                Day.user_id == user_id,
                Day.date == date,
                Day.deleted_at.is_(None),
            )
        )
        day = result.scalar_one_or_none()
        return self._to_entity(day=day) if day else None

    async def create(self, user_id: int, date: date_) -> DayEntity:
        day = Day(user_id=user_id, date=date, tags=[], creator_id=user_id)
        self.db.add(day)
        await self.db.commit()
        await self.db.refresh(day)
        return self._to_entity(day=day)

    async def update(
        self, day_id: int, user_id: int, fields: dict[str, Any]
    ) -> DayEntity | None:
        result = await self.db.execute(
            select(Day).where(
                Day.id == day_id,
                Day.user_id == user_id,
                Day.deleted_at.is_(None),
            )
        )
        day = result.scalar_one_or_none()
        if not day:
            return None

        for key, value in fields.items():
            setattr(day, key, value)
        day.updater_id = user_id

        await self.db.commit()
        await self.db.refresh(day)
        return self._to_entity(day=day)

    def _to_entity(self, day: Day) -> DayEntity:
        return DayEntity(
            id=day.id,
            date=day.date,
            written_primary=day.written_primary,
            written_drift=day.written_drift,
            is_hard_day=day.is_hard_day,
            tags=day.tags,
            duration_minutes=day.duration_minutes,
            energy=day.energy,
            mood=day.mood,
        )
