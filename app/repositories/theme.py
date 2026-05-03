from datetime import datetime

from sqlalchemy import select

from app.db.models.theme import Theme
from app.db.models.vision import Vision
from app.entities.theme import ThemeEntity
from app.repositories.base import BaseRepository


def _to_entity(t: Theme) -> ThemeEntity:
    return ThemeEntity(
        id=t.id,
        vision_id=t.vision_id,
        name=t.name,
        description=t.description,
        preset_key=t.preset_key,
        is_active=t.is_active,
    )


class ThemeRepository(BaseRepository):
    def _base_query(self, user_id: int):
        return (
            select(Theme)
            .join(Vision, Theme.vision_id == Vision.id)
            .where(
                Vision.user_id == user_id,
                Vision.deleted_at.is_(None),
                Theme.deleted_at.is_(None),
            )
        )

    async def list(self, user_id: int) -> list[ThemeEntity]:
        result = await self.db.execute(self._base_query(user_id=user_id))
        return [_to_entity(t) for t in result.scalars().all()]

    async def get_owned(self, theme_id: int, user_id: int) -> ThemeEntity | None:
        result = await self.db.execute(
            self._base_query(user_id=user_id).where(Theme.id == theme_id)
        )
        t = result.scalar_one_or_none()
        return _to_entity(t) if t else None

    async def create(
        self,
        vision_id: int,
        user_id: int,
        name: str,
        description: str,
        preset_key: str,
    ) -> ThemeEntity:
        now = datetime.utcnow()
        t = Theme(
            vision_id=vision_id,
            name=name,
            description=description,
            preset_key=preset_key,
            is_active=True,
            created_at=now,
            updated_at=now,
            creator_id=user_id,
            updater_id=user_id,
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        return _to_entity(t)

    async def update(
        self,
        theme_id: int,
        user_id: int,
        name: str | None,
        description: str | None,
        preset_key: str | None,
        is_active: bool | None,
    ) -> ThemeEntity:
        result = await self.db.execute(
            select(Theme).where(Theme.id == theme_id, Theme.deleted_at.is_(None))
        )
        t = result.scalar_one()
        if name is not None:
            t.name = name
        if description is not None:
            t.description = description
        if preset_key is not None:
            t.preset_key = preset_key
        if is_active is not None:
            t.is_active = is_active
        t.updated_at = datetime.utcnow()
        t.updater_id = user_id
        await self.db.commit()
        await self.db.refresh(t)
        return _to_entity(t)

    async def delete(self, theme_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Theme).where(Theme.id == theme_id, Theme.deleted_at.is_(None))
        )
        t = result.scalar_one()
        t.deleted_at = datetime.utcnow()
        t.deleter_id = user_id
        await self.db.commit()
