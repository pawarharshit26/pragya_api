from datetime import date

from app.db.models.daily_reflection import Mood
from app.entities.base import BaseEntity
from app.entities.commitment import CommitmentEntity
from app.entities.execution_log import ExecutionLogEntity


class TodayItemEntity(BaseEntity):
    commitment: CommitmentEntity
    log: ExecutionLogEntity | None


class TodayEntity(BaseEntity):
    date: date
    mood: Mood | None
    items: list[TodayItemEntity]
