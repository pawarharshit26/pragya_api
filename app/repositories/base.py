from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRecord(BaseModel):
    pass


class BaseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
