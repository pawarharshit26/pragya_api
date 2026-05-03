from datetime import datetime

from sqlalchemy import select

from app.db.models.vision import Vision
from app.entities.vision import VisionEntity
from app.repositories.base import BaseRepository


def _to_entity(v: Vision) -> VisionEntity:
    return VisionEntity(id=v.id, title=v.title, description=v.description, is_active=v.is_active)


class VisionRepository(BaseRepository):
    async def get_active(self, user_id: int) -> VisionEntity | None:
        result = await self.db.execute(
            select(Vision).where(
                Vision.user_id == user_id,
                Vision.is_active.is_(True),
                Vision.deleted_at.is_(None),
            )
        )
        v = result.scalar_one_or_none()
        return _to_entity(v) if v else None

    async def get_owned(self, vision_id: int, user_id: int) -> VisionEntity | None:
        result = await self.db.execute(
            select(Vision).where(
                Vision.id == vision_id,
                Vision.user_id == user_id,
                Vision.deleted_at.is_(None),
            )
        )
        v = result.scalar_one_or_none()
        return _to_entity(v) if v else None

    async def create(self, user_id: int, title: str, description: str) -> VisionEntity:
        now = datetime.utcnow()
        v = Vision(
            user_id=user_id,
            title=title,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
            creator_id=user_id,
            updater_id=user_id,
        )
        self.db.add(v)
        await self.db.commit()
        await self.db.refresh(v)
        return _to_entity(v)

    async def update(
        self,
        vision_id: int,
        user_id: int,
        title: str | None,
        description: str | None,
    ) -> VisionEntity:
        result = await self.db.execute(
            select(Vision).where(Vision.id == vision_id, Vision.deleted_at.is_(None))
        )
        v = result.scalar_one()
        if title is not None:
            v.title = title
        if description is not None:
            v.description = description
        v.updated_at = datetime.utcnow()
        v.updater_id = user_id
        await self.db.commit()
        await self.db.refresh(v)
        return _to_entity(v)

    async def delete(self, vision_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Vision).where(Vision.id == vision_id, Vision.deleted_at.is_(None))
        )
        v = result.scalar_one()
        v.deleted_at = datetime.utcnow()
        v.deleter_id = user_id
        await self.db.commit()
