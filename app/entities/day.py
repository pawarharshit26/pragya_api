from datetime import date as date_
from typing import Literal

from pydantic import Field

from app.core.hash_ids import HashId
from app.entities.base import BaseEntity

Mood = Literal["very_low", "low", "neutral", "high", "very_high"]


class DayEntity(BaseEntity):
    id: HashId
    date: date_
    written_primary: str | None = None
    written_drift: str | None = None
    is_hard_day: bool = False
    tags: list[str] = Field(default_factory=list)
    duration_minutes: int | None = None
    energy: int | None = None
    mood: Mood | None = None


class DayUpdateEntity(BaseEntity):
    written_primary: str | None = None
    written_drift: str | None = None
    is_hard_day: bool | None = None
    tags: list[str] | None = None
    duration_minutes: int | None = None
    energy: int | None = None
    mood: Mood | None = None
