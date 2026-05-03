from app.core.exceptions import BaseException
from app.entities.goal import GoalDetailEntity, GoalEntity
from app.repositories.goal import GoalRepository
from app.repositories.phase import PhaseRepository
from app.services.base import BaseService


class GoalService(BaseService):
    class GoalNotFoundException(BaseException):
        message = "Goal not found"

    def __init__(self, goal_repo: GoalRepository, phase_repo: PhaseRepository) -> None:
        self.goal_repo = goal_repo
        self.phase_repo = phase_repo

    async def list(self, user_id: int) -> list[GoalEntity]:
        return await self.goal_repo.list(user_id=user_id)

    async def get_detail(self, user_id: int, goal_id: int) -> GoalDetailEntity:
        goal = await self.goal_repo.get_owned(goal_id=goal_id, user_id=user_id)
        if not goal:
            raise self.GoalNotFoundException()
        phases = await self.phase_repo.list(user_id=user_id, goal_id=goal_id)
        return GoalDetailEntity(goal=goal, phases=phases)
