from sqlalchemy import select

from app.db.models.goal import Goal
from app.db.models.phase import Phase
from app.db.models.theme import Theme
from app.db.models.track import Track
from app.db.models.vision import Vision
from app.entities.phase import PhaseEntity
from app.repositories.base import BaseRepository


def _to_entity(p: Phase) -> PhaseEntity:
    return PhaseEntity(
        id=p.id,
        goal_id=p.goal_id,
        title=p.title,
        start_date=p.start_date,
        end_date=p.end_date,
        lifecycle=p.lifecycle,
        outcome=p.outcome,
    )


class PhaseRepository(BaseRepository):
    async def list(self, user_id: int, goal_id: int) -> list[PhaseEntity]:
        result = await self.db.execute(
            select(Phase)
            .join(Goal, Phase.goal_id == Goal.id)
            .join(Track, Goal.track_id == Track.id)
            .join(Theme, Track.theme_id == Theme.id)
            .join(Vision, Theme.vision_id == Vision.id)
            .where(
                Vision.user_id == user_id,
                Phase.goal_id == goal_id,
                Vision.deleted_at.is_(None),
                Theme.deleted_at.is_(None),
                Track.deleted_at.is_(None),
                Goal.deleted_at.is_(None),
                Phase.deleted_at.is_(None),
            )
        )
        return [_to_entity(p) for p in result.scalars().all()]
