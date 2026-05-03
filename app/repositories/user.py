from datetime import datetime

from sqlalchemy import delete, select

from app.core.security import verify_hash
from app.db.models.user import AuthToken, User
from app.entities.user import UserEntity
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        user = result.scalar_one_or_none()
        return self._to_user_entity(user=user) if user else None

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        user = result.scalar_one_or_none()
        return self._to_user_entity(user=user) if user else None

    async def create_user(
        self,
        email: str,
        name: str,
        hashed_password: str,
        creator_id: int | None = None,
    ) -> UserEntity:
        now = datetime.utcnow()
        user = User(
            email=email,
            name=name,
            password=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
            creator_id=creator_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return self._to_user_entity(user=user)

    async def check_password(self, email: str, plain_password: str) -> bool:
        result = await self.db.execute(
            select(User.password).where(
                User.email == email,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        hashed = result.scalar_one_or_none()
        if not hashed:
            return False
        return verify_hash(input=plain_password, hashed=hashed)

    async def get_valid_auth_token(self, token: str) -> int | None:
        result = await self.db.execute(
            select(AuthToken.user_id)
            .join(User, onclause=AuthToken.user_id == User.id)
            .where(
                AuthToken.token == token,
                AuthToken.expires_at > datetime.utcnow(),
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_auth_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> None:
        await self.db.execute(delete(AuthToken).where(AuthToken.user_id == user_id))
        self.db.add(AuthToken(user_id=user_id, token=token, expires_at=expires_at))
        await self.db.commit()

    async def delete_auth_tokens(self, user_id: int) -> None:
        await self.db.execute(delete(AuthToken).where(AuthToken.user_id == user_id))
        await self.db.commit()

    def _to_user_entity(self, user: User) -> UserEntity:
        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
