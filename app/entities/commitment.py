from datetime import date

from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class CommitmentEntity(BaseEntity):
    id: HashId
    phase_id: HashId
    date: date
    intent: str
    expected_minutes: int | None
    mve_minutes: int | None


class CreateCommitmentEntity(BaseEntity):
    phase_id: HashId
    commitment_date: date
    intent: str
    expected_minutes: int | None = None
    mve_minutes: int | None = None


class UpdateCommitmentEntity(BaseEntity):
    intent: str | None = None
    expected_minutes: int | None = None
    mve_minutes: int | None = None
