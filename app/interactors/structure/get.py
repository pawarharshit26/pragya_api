from app.entities.structure import StructureEntity
from app.interactors.base import BaseInteractor
from app.services.structure import StructureService


class GetStructureInteractor(BaseInteractor[int, StructureEntity]):
    def __init__(self, structure_service: StructureService) -> None:
        self.structure_service = structure_service

    async def execute(self, input: int) -> StructureEntity:
        return await self.structure_service.get(user_id=input)
