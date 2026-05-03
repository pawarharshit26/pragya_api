from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class ExecutionLogEntity(BaseEntity):
    id: HashId
    commitment_id: HashId
    actual_minutes: int | None
    energy_level: int | None
    note: str | None


class CreateExecutionLogEntity(BaseEntity):
    commitment_id: HashId
    actual_minutes: int | None = None
    energy_level: int | None = None
    note: str | None = None


class UpdateExecutionLogEntity(BaseEntity):
    actual_minutes: int | None = None
    energy_level: int | None = None
    note: str | None = None
