from datetime import date as date_

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import CreateUpdateDeleteModel


class Day(CreateUpdateDeleteModel):
    __tablename__ = "day"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_day_user_date"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    date: Mapped[date_] = mapped_column(Date, nullable=False)

    written_primary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="'Felt like me' on a normal day, 'what happened' on a hard day",
    )
    written_drift: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="'Felt like drifting' — shown on both normal and hard days",
    )
    is_hard_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mood: Mapped[str | None] = mapped_column(String, nullable=True)

    user = relationship(argument="User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Day(id={self.id}, user_id={self.user_id}, date={self.date})>"
