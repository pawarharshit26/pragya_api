from sqlalchemy import select

from app.db.models.execution_log import ExecutionLog
from app.entities.execution_log import ExecutionLogEntity
from app.repositories.base import BaseRepository


def _to_entity(e: ExecutionLog) -> ExecutionLogEntity:
    return ExecutionLogEntity(
        id=e.id,
        commitment_id=e.commitment_id,
        actual_minutes=e.actual_minutes,
        energy_level=e.energy_level,
        note=e.note,
    )


class ExecutionLogRepository(BaseRepository):
    async def get_by_commitment_ids(
        self, commitment_ids: list[int]
    ) -> dict[int, ExecutionLogEntity]:
        if not commitment_ids:
            return {}
        result = await self.db.execute(
            select(ExecutionLog).where(
                ExecutionLog.commitment_id.in_(commitment_ids),
                ExecutionLog.deleted_at.is_(None),
            )
        )
        return {e.commitment_id: _to_entity(e) for e in result.scalars().all()}
