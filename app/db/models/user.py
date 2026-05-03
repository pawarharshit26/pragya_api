from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import CreateModel, CreateUpdateDeleteModel


class User(CreateUpdateDeleteModel):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="User's email address (must be unique)",
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False, comment="User's full name"
    )
    password: Mapped[str] = mapped_column(
        String, nullable=False, comment="Hashed password"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the user account is active",
    )

    auth_token = relationship(
        argument="AuthToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="[AuthToken.user_id]",
    )

    vision = relationship(
        argument="Vision", back_populates="user", foreign_keys="[Vision.user_id]"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class AuthToken(CreateModel):
    __tablename__ = "auth_token"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, unique=True
    )
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user = relationship(
        argument="User", back_populates="auth_token", foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f"<AuthToken(id={self.id}, token='{self.user_id}')>"
