from app.core.redis import redis_client

class MetricsCacheRepository:
    KEYS = {
        "ingested": "metrics:tasks_ingested",
        "completed": "metrics:tasks_completed",
        "failed": "metrics:tasks_failed",
        "total_execution_ms": "metrics:total_execution_ms"   
    }
    
    async def incr_ingested(self) -> None:
        await redis_client.incr(self.KEYS["ingested"])
        
    async def incr_completed(self, execution_time_ms: int) -> None:
        async with redis_client.pipeline() as pipe:
            pipe.incr(self.KEYS["completed"])
            pipe.incr(self.KEYS["total_execution_ms"], execution_time_ms)
            await pipe.execute()
            
    async def incr_failed(self) -> None:
        await redis_client.incr(self.KEYS["failed"])
        
    async def get_snapshot(self) -> dict:
        values = await redis_client.mget(
            self.KEYS["ingested"],
            self.KEYS["completed"],
            self.KEYS["failed"],
            self.KEYS["total_execution_ms"],
        )
        ingested, completed, failed, total_exec_ms = (int(v) if v else 0 for v in values)
        
        return {
            "ingested": ingested,
            "completed": completed,
            "failed": failed,
            "total_execution_ms": total_exec_ms,
        }