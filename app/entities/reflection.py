from datetime import date

from app.core.hash_ids import HashId
from app.db.models.daily_reflection import Mood
from app.entities.base import BaseEntity


class ReflectionEntity(BaseEntity):
    id: HashId
    date: date
    mood: Mood | None


class UpsertReflectionEntity(BaseEntity):
    mood: Mood | None = None
