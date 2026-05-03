from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.db.base import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class CreateModel(BaseModel):
    __abstract__ = True

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime,
            nullable=False,
            default=datetime.utcnow,
            comment="Timestamp when this record was created",
        )

    @declared_attr
    def creator_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            ForeignKey("user.id"),
            nullable=True,
            comment="References the user who created this record",
        )

    @declared_attr
    def creator(cls) -> Mapped[Optional["User"]]:
        return relationship(argument="User", foreign_keys=[cls.creator_id])


class UpdateModel(BaseModel):
    __abstract__ = True

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime,
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            comment="Timestamp when this record was updated",
        )

    @declared_attr
    def updater_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            ForeignKey("user.id"),
            nullable=True,
            comment="References the user who last updated this record",
        )

    @declared_attr
    def updater(cls) -> Mapped[Optional["User"]]:
        return relationship(argument="User", foreign_keys=[cls.updater_id])


class DeleteModel(BaseModel):
    __abstract__ = True

    @declared_attr
    def deleted_at(cls) -> Mapped[Optional[datetime]]:
        return mapped_column(
            DateTime,
            nullable=True,
            comment="Timestamp when this record was deleted",
        )

    @declared_attr
    def deleter_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            ForeignKey("user.id"),
            nullable=True,
            comment="References the user who deleted this record",
        )

    @declared_attr
    def deleter(cls) -> Mapped[Optional["User"]]:
        return relationship(argument="User", foreign_keys=[cls.deleter_id])


class CreateUpdateDeleteModel(CreateModel, UpdateModel, DeleteModel):
    __abstract__ = True
