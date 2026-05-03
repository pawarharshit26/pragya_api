from datetime import date

from app.core.hash_ids import HashId
from app.db.models.phase import PhaseLifecycle
from app.entities.base import BaseEntity


class PhaseEntity(BaseEntity):
    id: HashId
    goal_id: HashId
    title: str
    start_date: date
    end_date: date
    lifecycle: PhaseLifecycle
    outcome: str | None


class CreatePhaseEntity(BaseEntity):
    goal_id: HashId
    title: str
    start_date: date
    end_date: date
    lifecycle: PhaseLifecycle = PhaseLifecycle.DRAFT
    outcome: str | None = None


class UpdatePhaseEntity(BaseEntity):
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    lifecycle: PhaseLifecycle | None = None
    outcome: str | None = None
