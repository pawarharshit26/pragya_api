from app.entities.vision import VisionEntity
from app.interactors.base import BaseInteractor
from app.services.vision import VisionService


class GetActiveVisionInteractor(BaseInteractor[int, VisionEntity]):
    class VisionNotFoundException(BaseInteractor.InteractorException):
        message = "Vision not found"

    def __init__(self, vision_service: VisionService) -> None:
        self.vision_service = vision_service

    async def execute(self, input: int) -> VisionEntity:
        try:
            return await self.vision_service.get_active(user_id=input)
        except VisionService.VisionNotFoundException as e:
            raise self.VisionNotFoundException() from e
