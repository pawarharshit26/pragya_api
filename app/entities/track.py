from datetime import datetime

from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class TrackEntity(BaseEntity):
    id: HashId
    theme_id: HashId
    name: str
    description: str | None
    is_active: bool
    cadence_per_week: int | None
    is_paused: bool
    paused_at: datetime | None


class CreateTrackEntity(BaseEntity):
    theme_id: HashId
    name: str
    description: str | None = None
    cadence_per_week: int | None = None


class UpdateTrackEntity(BaseEntity):
    name: str | None = None
    description: str | None = None
    cadence_per_week: int | None = None
    is_active: bool | None = None
