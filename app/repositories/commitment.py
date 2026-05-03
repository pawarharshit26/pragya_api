from datetime import date

from sqlalchemy import select

from app.db.models.daily_commitment import DailyCommitment
from app.db.models.goal import Goal
from app.db.models.phase import Phase
from app.db.models.theme import Theme
from app.db.models.track import Track
from app.db.models.vision import Vision
from app.entities.commitment import CommitmentEntity
from app.repositories.base import BaseRepository


def _to_entity(c: DailyCommitment) -> CommitmentEntity:
    return CommitmentEntity(
        id=c.id,
        phase_id=c.phase_id,
        date=c.commitment_date,
        intent=c.intent,
        expected_minutes=c.expected_minutes,
        mve_minutes=c.mve_minutes,
    )


class CommitmentRepository(BaseRepository):
    async def list_by_date(self, user_id: int, for_date: date) -> list[CommitmentEntity]:
        result = await self.db.execute(
            select(DailyCommitment)
            .join(Phase, DailyCommitment.phase_id == Phase.id)
            .join(Goal, Phase.goal_id == Goal.id)
            .join(Track, Goal.track_id == Track.id)
            .join(Theme, Track.theme_id == Theme.id)
            .join(Vision, Theme.vision_id == Vision.id)
            .where(
                Vision.user_id == user_id,
                DailyCommitment.commitment_date == for_date,
                Vision.deleted_at.is_(None),
                Theme.deleted_at.is_(None),
                Track.deleted_at.is_(None),
                Goal.deleted_at.is_(None),
                Phase.deleted_at.is_(None),
                DailyCommitment.deleted_at.is_(None),
            )
        )
        return [_to_entity(c) for c in result.scalars().all()]
