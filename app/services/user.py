import secrets
from datetime import datetime, timedelta

import structlog

from app.core.config import settings
from app.core.exceptions import BaseException
from app.core.jwt import JWTService
from app.core.security import get_hash
from app.entities.user import UserEntity, UserSignInEntity, UserSignUpEntity, UserTokenEntity
from app.repositories.user import UserRepository
from app.services.base import BaseService

logger = structlog.get_logger(__name__)


class UserService(BaseService):
    class UserException(BaseException):
        message = "User Exception"

    class UserAlreadyExistsException(UserException):
        message = "User Already Exists"

    class UserNotFoundException(UserException):
        message = "User Not Found"

    class UserInvalidPasswordException(UserException):
        message = "Invalid Password"

    class UserAuthException(UserException):
        message = "Authentication failed"

    def __init__(self, repo: UserRepository, jwt_service: JWTService) -> None:
        self.repo = repo
        self.jwt_service = jwt_service

    async def create_user(self, input: UserSignUpEntity) -> UserTokenEntity:
        logger.info("Creating user", email=input.email)

        if await self.repo.get_by_email(email=input.email):
            logger.info("User already exists", email=input.email)
            raise self.UserAlreadyExistsException()

        user = await self.repo.create_user(
            email=input.email,
            name=input.name,
            hashed_password=get_hash(input=input.password),
            creator_id=None,  # bootstrap: no authenticated user at signup
        )

        jwt_token = await self._issue_token(user_id=user.id)

        logger.info("User created", email=user.email)
        return UserTokenEntity(token=jwt_token, user=user)

    async def sign_in(self, input: UserSignInEntity) -> UserTokenEntity:
        logger.info("Signing in user", email=input.email)

        user = await self.repo.get_by_email(email=input.email)
        if not user:
            logger.info("User not found", email=input.email)
            raise self.UserNotFoundException()

        if not await self.repo.check_password(email=input.email, plain_password=input.password):
            logger.info("Invalid password", email=user.email)
            raise self.UserInvalidPasswordException()

        logger.info("Identity verified", email=user.email)

        jwt_token = await self._issue_token(user_id=user.id)

        logger.info("User signed in", email=user.email)
        return UserTokenEntity(token=jwt_token, user=user)

    async def signout(self, user_id: int) -> None:
        logger.info("Signing out user", user_id=user_id)
        await self.repo.delete_auth_tokens(user_id=user_id)
        logger.info("User signed out", user_id=user_id)

    async def get_user(self, user_id: int) -> UserEntity:
        user = await self.repo.get_by_id(user_id=user_id)
        if not user:
            raise self.UserNotFoundException()
        return user

    async def resolve_user_id_from_token(self, jwt_token: str) -> int:
        try:
            payload = self.jwt_service.decode(token=jwt_token)
        except JWTService.JWTException as e:
            raise self.UserAuthException() from e

        sub = payload.get("sub")
        if not sub or "auth_token" not in sub:
            raise self.UserAuthException()

        user_id = await self.repo.get_valid_auth_token(token=sub["auth_token"])
        if not user_id:
            raise self.UserAuthException()

        return user_id

    async def _issue_token(self, user_id: int) -> str:
        token_str = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        await self.repo.create_auth_token(user_id=user_id, token=token_str, expires_at=expires_at)
        return self.jwt_service.encode(subject={"auth_token": token_str})
