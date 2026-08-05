from app.repository.metrics_cache_repository import MetricsCacheRepository

class MetricsService:
    def __init__(self):
        self.cache_repo = MetricsCacheRepository()
        
    async def get_health(self) -> dict:
        snapshot = await self.cache_repo.get_snapshot()
        
        completed = snapshot["completed"]
        failed = snapshot["failed"]
        ingested = snapshot["ingested"]
        total_exec_ms = snapshot["total_execution_ms"]
        
        total_processed = completed + failed 
        in_flight = max(ingested - total_processed, 0)
        
        return {
            "tasks_ingested": ingested,
            "tasks_in_flight": in_flight,
            "tasks_completed": completed,
            "tasks_failed": failed,
            "success_rate": round(completed / total_processed, 4) if total_processed else None,
            "avg_execution_time_ms": round(total_exec_ms / completed, 2) if completed else None,
        }