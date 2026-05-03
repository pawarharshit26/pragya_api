from app.entities.base import BaseEntity
from app.entities.theme import ThemeEntity
from app.entities.track import TrackEntity


class StructureEntity(BaseEntity):
    themes: list[ThemeEntity]
    tracks: list[TrackEntity]
