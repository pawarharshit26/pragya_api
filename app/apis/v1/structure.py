from typing import Annotated

from fastapi import APIRouter, Depends

from app.apis.response import ResponseEntity
from app.dependencies import get_current_user_id, get_get_structure_interactor
from app.entities.structure import StructureEntity
from app.interactors.structure.get import GetStructureInteractor

structure_router = APIRouter()


@structure_router.get(path="/", response_model=ResponseEntity[StructureEntity])
async def get_structure(
    interactor: Annotated[GetStructureInteractor, Depends(get_get_structure_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    result = await interactor.execute(input=user_id)
    return ResponseEntity[StructureEntity](data=result)
