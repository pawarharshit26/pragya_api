from app.entities.base import BaseEntity
from app.entities.goal import GoalDetailEntity
from app.interactors.base import BaseInteractor
from app.services.goal import GoalService


class GetGoalDetailInput(BaseEntity):
    user_id: int
    goal_id: int


class GetGoalDetailInteractor(BaseInteractor[GetGoalDetailInput, GoalDetailEntity]):
    class GoalNotFoundException(BaseInteractor.InteractorException):
        message = "Goal not found"

    def __init__(self, goal_service: GoalService) -> None:
        self.goal_service = goal_service

    async def execute(self, input: GetGoalDetailInput) -> GoalDetailEntity:
        try:
            return await self.goal_service.get_detail(
                user_id=input.user_id, goal_id=input.goal_id
            )
        except GoalService.GoalNotFoundException as e:
            raise self.GoalNotFoundException() from e
