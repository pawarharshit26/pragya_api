from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.apis.exceptions import BaseAPIException
from app.apis.response import ResponseEntity
from app.dependencies import (
    get_current_user_id,
    get_me_interactor,
    get_signin_interactor,
    get_signout_interactor,
    get_signup_interactor,
)
from app.entities.user import (
    UserEntity,
    UserSignInEntity,
    UserSignUpEntity,
    UserTokenEntity,
)
from app.interactors.user.get_me import GetMeInteractor
from app.interactors.user.signin import SigninInteractor
from app.interactors.user.signout import SignoutInteractor
from app.interactors.user.signup import SignupInteractor

user_router = APIRouter()


@user_router.post(path="/signup", response_model=ResponseEntity[UserTokenEntity])
async def signup(
    data: UserSignUpEntity,
    interactor: Annotated[SignupInteractor, Depends(get_signup_interactor)],
):
    try:
        result = await interactor.execute(input=data)
        return ResponseEntity[UserTokenEntity](data=result)
    except SignupInteractor.UserAlreadyExistsException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_400_BAD_REQUEST
        ) from e


@user_router.post(path="/signin", response_model=ResponseEntity[UserTokenEntity])
async def signin(
    data: UserSignInEntity,
    interactor: Annotated[SigninInteractor, Depends(get_signin_interactor)],
):
    try:
        result = await interactor.execute(input=data)
        return ResponseEntity[UserTokenEntity](data=result)
    except SigninInteractor.InvalidCredentialsException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_401_UNAUTHORIZED
        ) from e
    except SigninInteractor.UserNotFoundException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_404_NOT_FOUND
        ) from e


@user_router.get(path="/me", response_model=ResponseEntity[UserEntity])
async def me(
    interactor: Annotated[GetMeInteractor, Depends(get_me_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    try:
        result = await interactor.execute(input=user_id)
        return ResponseEntity[UserEntity](data=result)
    except GetMeInteractor.UserNotFoundException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_404_NOT_FOUND
        ) from e


@user_router.post(path="/signout", response_model=ResponseEntity)
async def signout(
    interactor: Annotated[SignoutInteractor, Depends(get_signout_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    await interactor.execute(input=user_id)
    return ResponseEntity(data={})
