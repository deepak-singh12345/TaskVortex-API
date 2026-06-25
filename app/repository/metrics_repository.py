from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.log_metrics import LogMetrics

class MetricsRepository:
    def __init__(self, db: AsyncSession):
        self.db:AsyncSession = db 
        
    async def create_log(
        self, 
        task_id: int,
        status: str,
        execution_time_ms: int,
        message: str | None,
    ) -> LogMetrics:
        metric = LogMetrics(
            task_id=task_id,
            # task = task,
            status = status,
            execution_time_ms = execution_time_ms,
            message = message
        )

        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)

        return metric 
    
    async def get_logs_by_task(self, task_id: int) -> list[LogMetrics]:
        stmt = select(LogMetrics).where(LogMetrics.task_id == task_id)
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        return logs 