from datetime import datetime

from sqlalchemy import select

from app.db.models.goal import Goal
from app.db.models.theme import Theme
from app.db.models.track import Track
from app.db.models.vision import Vision
from app.entities.goal import GoalEntity
from app.repositories.base import BaseRepository


def _to_entity(g: Goal) -> GoalEntity:
    return GoalEntity(id=g.id, track_id=g.track_id, title=g.title, horizon=g.horizon)


class GoalRepository(BaseRepository):
    def _base_query(self, user_id: int):
        return (
            select(Goal)
            .join(Track, Goal.track_id == Track.id)
            .join(Theme, Track.theme_id == Theme.id)
            .join(Vision, Theme.vision_id == Vision.id)
            .where(
                Vision.user_id == user_id,
                Vision.deleted_at.is_(None),
                Theme.deleted_at.is_(None),
                Track.deleted_at.is_(None),
                Goal.deleted_at.is_(None),
            )
        )

    async def list(self, user_id: int, track_id: int | None = None) -> list[GoalEntity]:
        q = self._base_query(user_id=user_id)
        if track_id is not None:
            q = q.where(Goal.track_id == track_id)
        result = await self.db.execute(q)
        return [_to_entity(g) for g in result.scalars().all()]

    async def get_owned(self, goal_id: int, user_id: int) -> GoalEntity | None:
        result = await self.db.execute(
            self._base_query(user_id=user_id).where(Goal.id == goal_id)
        )
        g = result.scalar_one_or_none()
        return _to_entity(g) if g else None

    async def create(
        self,
        track_id: int,
        user_id: int,
        title: str,
        horizon: str | None,
    ) -> GoalEntity:
        now = datetime.utcnow()
        g = Goal(
            track_id=track_id,
            title=title,
            horizon=horizon,
            created_at=now,
            updated_at=now,
            creator_id=user_id,
            updater_id=user_id,
        )
        self.db.add(g)
        await self.db.commit()
        await self.db.refresh(g)
        return _to_entity(g)

    async def update(
        self,
        goal_id: int,
        user_id: int,
        title: str | None,
        horizon: str | None,
    ) -> GoalEntity:
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.deleted_at.is_(None))
        )
        g = result.scalar_one()
        if title is not None:
            g.title = title
        if horizon is not None:
            g.horizon = horizon
        g.updated_at = datetime.utcnow()
        g.updater_id = user_id
        await self.db.commit()
        await self.db.refresh(g)
        return _to_entity(g)

    async def delete(self, goal_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.deleted_at.is_(None))
        )
        g = result.scalar_one()
        g.deleted_at = datetime.utcnow()
        g.deleter_id = user_id
        await self.db.commit()
