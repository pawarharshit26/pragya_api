import secrets
from datetime import datetime, timedelta
from typing import Annotated

import structlog
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.exceptions import UnauthorizedException
from app.core.config import settings
from app.core.exceptions import BaseException
from app.core.hash_ids import HashId
from app.core.jwt import JWTService, get_jwt_service
from app.core.security import get_hash, verify_hash
from app.db.base import get_db
from app.db.models.user import AuthToken, User
from app.services.base import BaseEntity, BaseService

logger = structlog.get_logger(__name__)


class UserSignUpEntity(BaseEntity):
    email: EmailStr
    password: str
    name: str


class UserSignInEntity(BaseEntity):
    email: EmailStr
    password: str


class UserEntity(BaseEntity):
    id: HashId
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserTokenEntity(BaseEntity):
    token: str
    user: UserEntity


class UserService(BaseService):
    class UserException(BaseException):
        message = "User Exception"

    class UserAlreadyExistsException(UserException):
        message = "User Already Exists"

    class UserNotFoundException(UserException):
        message = "User Not Found"

    class UserInvalidPasswordException(UserException):
        message = "Invalid Password"

    async def create_user(self, input: UserSignUpEntity) -> UserTokenEntity:
        logger.info("Creating user", email=input.email)

        query = select(User).where(
            User.email == input.email,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.info("User already exists", email=input.email)
            raise self.UserAlreadyExistsException()

        user = User(
            email=input.email,
            name=input.name,
            password=get_hash(input.password),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        auth_token = await self.create_auth_token(user)
        jwt_token = self._encode_jwt(user=user, auth_token=auth_token)

        logger.info("User created", email=user.email)
        return UserTokenEntity.model_validate(
            {
                "token": jwt_token,
                "user": UserEntity.model_validate(user, from_attributes=True),
            }
        )

    async def sign_in(self, input: UserSignInEntity) -> UserTokenEntity:
        logger.info("Signing in user", email=input.email)

        query = select(User).where(
            User.email == input.email,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )

        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            logger.info("User not found", email=input.email)
            raise self.UserNotFoundException()

        if not verify_hash(input=input.password, hashed=user.password):
            logger.info("Invalid password", email=user.email)
            raise self.UserInvalidPasswordException()

        logger.info("Identity verified", email=user.email)

        auth_token = await self.create_auth_token(user)

        jwt_token = self._encode_jwt(user=user, auth_token=auth_token)

        logger.info("User signed in", email=user.email)
        return UserTokenEntity.model_validate(
            {
                "token": jwt_token,
                "user": UserEntity.model_validate(user, from_attributes=True),
            }
        )

    async def signout(self, user_id: int):
        logger.info("Signing out user", user_id=user_id)

        query = delete(AuthToken).where(AuthToken.user_id == user_id)
        await self.db.execute(query)
        await self.db.commit()

        logger.info("User signed out", user_id=user_id)

    async def create_auth_token(self, user: User) -> AuthToken:
        logger.info("create auth token", email=user.email)

        query = delete(AuthToken).where(AuthToken.user_id == user.id)
        await self.db.execute(query)

        token = AuthToken(
            user_id=user.id,
            token=self._genrate_token_string(),
            expires_at=datetime.now()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)

        logger.info("Token generated", email=user.email)
        return token

    async def get_user(self, user_id: int) -> UserEntity:
        query = select(User).where(
            User.id == user_id, User.is_active.is_(True), User.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise self.UserNotFoundException()
        return UserEntity.model_validate(user, from_attributes=True)

    def _genrate_token_string(self) -> str:
        return secrets.token_urlsafe(64)

    def _encode_jwt(self, user: User, auth_token: AuthToken) -> str:
        return get_jwt_service().encode(subject={"auth_token": auth_token.token})


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    return UserService(db)


async def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=False))
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> int:
    logger.info("Getting current user id")
    if not credentials:
        raise UnauthorizedException()

    try:
        payload = jwt_service.decode(credentials.credentials)
    except JWTService.JWTException as e:
        raise UnauthorizedException() from e

    logger.info("Decoded payload", payload=payload)

    sub = payload.get("sub")
    if not sub or "auth_token" not in sub:
        raise UnauthorizedException()

    token = sub.get("auth_token")
    query = (
        select(AuthToken)
        .join(User, onclause=AuthToken.user_id == User.id)
        .where(
            AuthToken.token == token,
            AuthToken.expires_at > datetime.now(),
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    auth_token = result.scalar_one_or_none()
    if not auth_token:
        raise UnauthorizedException()

    logger.info("User found, Auth token is valid")
    return auth_token.user_id
