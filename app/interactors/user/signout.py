from app.interactors.base import BaseInteractor
from app.services.user import UserService


class SignoutInteractor(BaseInteractor[int, None]):
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, input: int) -> None:
        await self.user_service.signout(user_id=input)
