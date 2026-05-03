from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class ThemeEntity(BaseEntity):
    id: HashId
    vision_id: HashId
    name: str
    description: str
    preset_key: str
    is_active: bool


class CreateThemeEntity(BaseEntity):
    vision_id: HashId
    name: str
    description: str
    preset_key: str


class UpdateThemeEntity(BaseEntity):
    name: str | None = None
    description: str | None = None
    preset_key: str | None = None
    is_active: bool | None = None
