from datetime import date

from app.entities.today import TodayEntity, TodayItemEntity
from app.repositories.commitment import CommitmentRepository
from app.repositories.execution_log import ExecutionLogRepository
from app.repositories.reflection import ReflectionRepository
from app.services.base import BaseService


class TodayService(BaseService):
    def __init__(
        self,
        commitment_repo: CommitmentRepository,
        log_repo: ExecutionLogRepository,
        reflection_repo: ReflectionRepository,
    ) -> None:
        self.commitment_repo = commitment_repo
        self.log_repo = log_repo
        self.reflection_repo = reflection_repo

    async def get(self, user_id: int, for_date: date) -> TodayEntity:
        commitments = await self.commitment_repo.list_by_date(
            user_id=user_id, for_date=for_date
        )
        commitment_ids = [int(c.id) for c in commitments]
        logs = await self.log_repo.get_by_commitment_ids(commitment_ids=commitment_ids)
        reflection = await self.reflection_repo.get_by_date(
            user_id=user_id, for_date=for_date
        )
        items = [
            TodayItemEntity(commitment=c, log=logs.get(int(c.id)))
            for c in commitments
        ]
        return TodayEntity(
            date=for_date,
            mood=reflection.mood if reflection else None,
            items=items,
        )
