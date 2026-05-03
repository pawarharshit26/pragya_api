from app.entities.goal import GoalEntity
from app.interactors.base import BaseInteractor
from app.services.goal import GoalService


class ListGoalsInteractor(BaseInteractor[int, list[GoalEntity]]):
    def __init__(self, goal_service: GoalService) -> None:
        self.goal_service = goal_service

    async def execute(self, input: int) -> list[GoalEntity]:
        return await self.goal_service.list(user_id=input)
