from app.entities.user import UserSignInEntity, UserTokenEntity
from app.interactors.base import BaseInteractor
from app.services.user import UserService


class SigninInteractor(BaseInteractor[UserSignInEntity, UserTokenEntity]):
    class UserNotFoundException(BaseInteractor.InteractorException):
        message = "User not found"

    class InvalidCredentialsException(BaseInteractor.InteractorException):
        message = "Invalid credentials"

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, input: UserSignInEntity) -> UserTokenEntity:
        try:
            return await self.user_service.sign_in(input=input)
        except UserService.UserNotFoundException as e:
            raise self.UserNotFoundException() from e
        except UserService.UserInvalidPasswordException as e:
            raise self.InvalidCredentialsException() from e
