from app.entities.user import UserSignUpEntity, UserTokenEntity
from app.interactors.base import BaseInteractor
from app.services.user import UserService


class SignupInteractor(BaseInteractor[UserSignUpEntity, UserTokenEntity]):
    class UserAlreadyExistsException(BaseInteractor.InteractorException):
        message = "User already exists"

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, input: UserSignUpEntity) -> UserTokenEntity:
        try:
            return await self.user_service.create_user(input=input)
        except UserService.UserAlreadyExistsException as e:
            raise self.UserAlreadyExistsException() from e
