from typing import Annotated

import structlog
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.exceptions import UnauthorizedException
from app.core.jwt import JWTService, get_jwt_service
from app.db.base import get_db
from app.interactors.day.get_today import GetTodayInteractor
from app.interactors.day.update_today import UpdateTodayInteractor
from app.interactors.user.get_me import GetMeInteractor
from app.interactors.user.signin import SigninInteractor
from app.interactors.user.signout import SignoutInteractor
from app.interactors.user.signup import SignupInteractor
from app.repositories.day import DayRepository
from app.repositories.user import UserRepository
from app.services.day import DayService
from app.services.user import UserService

logger = structlog.get_logger(__name__)


# --- User ---


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db=db)


def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> UserService:
    return UserService(repo=repo, jwt_service=jwt_service)


def get_signup_interactor(
    service: Annotated[UserService, Depends(get_user_service)],
) -> SignupInteractor:
    return SignupInteractor(user_service=service)


def get_signin_interactor(
    service: Annotated[UserService, Depends(get_user_service)],
) -> SigninInteractor:
    return SigninInteractor(user_service=service)


def get_signout_interactor(
    service: Annotated[UserService, Depends(get_user_service)],
) -> SignoutInteractor:
    return SignoutInteractor(user_service=service)


def get_me_interactor(
    service: Annotated[UserService, Depends(get_user_service)],
) -> GetMeInteractor:
    return GetMeInteractor(user_service=service)


# --- Day ---


def get_day_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DayRepository:
    return DayRepository(db=db)


def get_day_service(
    repo: Annotated[DayRepository, Depends(get_day_repository)],
) -> DayService:
    return DayService(repo=repo)


def get_today_interactor(
    service: Annotated[DayService, Depends(get_day_service)],
) -> GetTodayInteractor:
    return GetTodayInteractor(day_service=service)


def get_update_today_interactor(
    service: Annotated[DayService, Depends(get_day_service)],
) -> UpdateTodayInteractor:
    return UpdateTodayInteractor(day_service=service)


# --- Auth guard ---


async def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=False))
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> int:
    logger.info("Getting current user id")
    if not credentials:
        raise UnauthorizedException()
    try:
        return await user_service.resolve_user_id_from_token(
            jwt_token=credentials.credentials
        )
    except UserService.UserAuthException as e:
        raise UnauthorizedException() from e
