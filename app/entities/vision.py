from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class VisionEntity(BaseEntity):
    id: HashId
    title: str
    description: str
    is_active: bool


class CreateVisionEntity(BaseEntity):
    title: str
    description: str


class UpdateVisionEntity(BaseEntity):
    title: str | None = None
    description: str | None = None
