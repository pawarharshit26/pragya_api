from app.entities.user import UserEntity
from app.interactors.base import BaseInteractor
from app.services.user import UserService


class GetMeInteractor(BaseInteractor[int, UserEntity]):
    class UserNotFoundException(BaseInteractor.InteractorException):
        message = "User not found"

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, input: int) -> UserEntity:
        try:
            return await self.user_service.get_user(user_id=input)
        except UserService.UserNotFoundException as e:
            raise self.UserNotFoundException() from e
