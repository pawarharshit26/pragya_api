from datetime import datetime

from sqlalchemy import select

from app.db.models.theme import Theme
from app.db.models.track import Track
from app.db.models.vision import Vision
from app.entities.track import TrackEntity
from app.repositories.base import BaseRepository


def _to_entity(t: Track) -> TrackEntity:
    return TrackEntity(
        id=t.id,
        theme_id=t.theme_id,
        name=t.name,
        description=t.description,
        is_active=t.is_active,
        cadence_per_week=t.cadence_per_week,
        is_paused=t.is_paused,
        paused_at=t.paused_at,
    )


class TrackRepository(BaseRepository):
    def _base_query(self, user_id: int):
        return (
            select(Track)
            .join(Theme, Track.theme_id == Theme.id)
            .join(Vision, Theme.vision_id == Vision.id)
            .where(
                Vision.user_id == user_id,
                Vision.deleted_at.is_(None),
                Theme.deleted_at.is_(None),
                Track.deleted_at.is_(None),
            )
        )

    async def list(self, user_id: int, theme_id: int | None = None) -> list[TrackEntity]:
        q = self._base_query(user_id=user_id)
        if theme_id is not None:
            q = q.where(Track.theme_id == theme_id)
        result = await self.db.execute(q)
        return [_to_entity(t) for t in result.scalars().all()]

    async def get_owned(self, track_id: int, user_id: int) -> TrackEntity | None:
        result = await self.db.execute(
            self._base_query(user_id=user_id).where(Track.id == track_id)
        )
        t = result.scalar_one_or_none()
        return _to_entity(t) if t else None

    async def create(
        self,
        theme_id: int,
        user_id: int,
        name: str,
        description: str | None,
        cadence_per_week: int | None,
    ) -> TrackEntity:
        now = datetime.utcnow()
        t = Track(
            theme_id=theme_id,
            name=name,
            description=description,
            is_active=True,
            cadence_per_week=cadence_per_week,
            is_paused=False,
            paused_at=None,
            created_at=now,
            updated_at=now,
            creator_id=user_id,
            updater_id=user_id,
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        return _to_entity(t)

    async def update(
        self,
        track_id: int,
        user_id: int,
        name: str | None,
        description: str | None,
        cadence_per_week: int | None,
        is_active: bool | None,
    ) -> TrackEntity:
        result = await self.db.execute(
            select(Track).where(Track.id == track_id, Track.deleted_at.is_(None))
        )
        t = result.scalar_one()
        if name is not None:
            t.name = name
        if description is not None:
            t.description = description
        if cadence_per_week is not None:
            t.cadence_per_week = cadence_per_week
        if is_active is not None:
            t.is_active = is_active
        t.updated_at = datetime.utcnow()
        t.updater_id = user_id
        await self.db.commit()
        await self.db.refresh(t)
        return _to_entity(t)

    async def set_paused(self, track_id: int, user_id: int, paused: bool) -> TrackEntity:
        result = await self.db.execute(
            select(Track).where(Track.id == track_id, Track.deleted_at.is_(None))
        )
        t = result.scalar_one()
        t.is_paused = paused
        t.paused_at = datetime.utcnow() if paused else None
        t.updated_at = datetime.utcnow()
        t.updater_id = user_id
        await self.db.commit()
        await self.db.refresh(t)
        return _to_entity(t)

    async def delete(self, track_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Track).where(Track.id == track_id, Track.deleted_at.is_(None))
        )
        t = result.scalar_one()
        t.deleted_at = datetime.utcnow()
        t.deleter_id = user_id
        await self.db.commit()
