from datetime import date

from sqlalchemy import select

from app.db.models.daily_reflection import DailyReflection
from app.entities.reflection import ReflectionEntity
from app.repositories.base import BaseRepository


def _to_entity(r: DailyReflection) -> ReflectionEntity:
    return ReflectionEntity(id=r.id, date=r.date, mood=r.mood)


class ReflectionRepository(BaseRepository):
    async def get_by_date(self, user_id: int, for_date: date) -> ReflectionEntity | None:
        result = await self.db.execute(
            select(DailyReflection).where(
                DailyReflection.user_id == user_id,
                DailyReflection.date == for_date,
                DailyReflection.deleted_at.is_(None),
            )
        )
        r = result.scalar_one_or_none()
        return _to_entity(r) if r else None
