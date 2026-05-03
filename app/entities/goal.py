from app.core.hash_ids import HashId
from app.entities.base import BaseEntity
from app.entities.phase import PhaseEntity


class GoalEntity(BaseEntity):
    id: HashId
    track_id: HashId
    title: str
    horizon: str | None


class GoalDetailEntity(BaseEntity):
    goal: GoalEntity
    phases: list[PhaseEntity]


class CreateGoalEntity(BaseEntity):
    track_id: HashId
    title: str
    horizon: str | None = None


class UpdateGoalEntity(BaseEntity):
    title: str | None = None
    horizon: str | None = None
