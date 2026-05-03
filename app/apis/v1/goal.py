from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.apis.exceptions import BaseAPIException
from app.apis.response import ResponseEntity
from app.core.hash_ids import HashId, decode
from app.dependencies import (
    get_current_user_id,
    get_get_goal_detail_interactor,
    get_list_goals_interactor,
)
from app.entities.goal import GoalDetailEntity, GoalEntity
from app.interactors.goal.get_detail import GetGoalDetailInput, GetGoalDetailInteractor
from app.interactors.goal.list import ListGoalsInteractor

goal_router = APIRouter()


@goal_router.get(path="/", response_model=ResponseEntity[list[GoalEntity]])
async def list_goals(
    interactor: Annotated[ListGoalsInteractor, Depends(get_list_goals_interactor)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    result = await interactor.execute(input=user_id)
    return ResponseEntity[list[GoalEntity]](data=result)


@goal_router.get(path="/{goal_id}", response_model=ResponseEntity[GoalDetailEntity])
async def get_goal_detail(
    goal_id: str,
    interactor: Annotated[
        GetGoalDetailInteractor, Depends(get_get_goal_detail_interactor)
    ],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    try:
        result = await interactor.execute(
            input=GetGoalDetailInput(user_id=user_id, goal_id=decode(goal_id))
        )
        return ResponseEntity[GoalDetailEntity](data=result)
    except GetGoalDetailInteractor.GoalNotFoundException as e:
        raise BaseAPIException(
            message=str(e.message), status_code=status.HTTP_404_NOT_FOUND
        ) from e
