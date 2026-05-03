from app.entities.structure import StructureEntity
from app.repositories.theme import ThemeRepository
from app.repositories.track import TrackRepository
from app.services.base import BaseService


class StructureService(BaseService):
    def __init__(self, theme_repo: ThemeRepository, track_repo: TrackRepository) -> None:
        self.theme_repo = theme_repo
        self.track_repo = track_repo

    async def get(self, user_id: int) -> StructureEntity:
        themes = await self.theme_repo.list(user_id=user_id)
        tracks = await self.track_repo.list(user_id=user_id)
        return StructureEntity(themes=themes, tracks=tracks)
