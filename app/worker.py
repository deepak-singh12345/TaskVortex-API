import asyncio
import json
import logging

import aio_pika
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError

from app.core.database import AsyncSessionLocal
from app.models.task import TaskStatus
from app.repository.task_repository import TaskRepository
from app.core.redis import redis_client


import logging 

logger = logging.getLogger(__name__)

async def process_heavy_task():
    await asyncio.sleep(5)
    
@retry(
    retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
)
async def _fetch_task_with_retry(repo: TaskRepository, task_id):
    return await repo.get_task_for_processing(task_id)

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
                
            body = json.loads(message.body.decode())
            task_id = body["task_id"]
        except (json.JSONDecodeError, KeyError):
            return 
        
        logger.info(
            "Message received",
            extra={
                "context": {
                    # "tracking_token": body["tracking_token"],
                    "task_id": task_id,
                }
            },
        )

        async with AsyncSessionLocal() as db:
            repo = TaskRepository(db)

            try:
                task = await _fetch_task_with_retry(repo, task_id)
            except OperationalError:  #later add something so, that we know that the db was down or something so, that it can be hanlded.
                # DB unreachable after 3 retries — this IS the case we
                # want to actually escalate. Let it propagate so the
                # message nacks and we don't silently pretend it worked.
                logger.exception(
                    "DB unreachable after retries", extra={"context": {"task_id": task_id}}
                )
                raise 
            
            if task is None:
                logger.warning("Task not found, dropping message", extra={"context": {"task_id": task_id}})
                return
            
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                logger.info("Duplicate delivery ignored", extra={"context": {"task_id": task_id}})
                return
            
            task.status = TaskStatus.PROCESSING
            await db.commit()
            
            try: 
                await asyncio.wait_for(process_heavy_task(), timeout=10.0)
                task.status = TaskStatus.COMPLETED
                await db.commit()
                logger.info("Task completed", extra={"context": {"task_id": task_id}})
            
            except asyncio.TimeoutError:
                task.status = TaskStatus.FAILED
                await db.commit()
                logger.warning("Task processing timed out", extra={"context": {"task_id": task_id}})
                
            except Exception:
                # Catch-all: anything unexpected in the processing step
                # becomes a recorded FAILED row, not a vanished message.
                await db.rollback()
                task.status = TaskStatus.FAILED
                await db.commit()
                logger.exception("Unexpected error during processing", extra={"context": {"task_id": task_id}})
                
            keys_to_delete = []
            async for key in redis_client.scan_iter(match=f"task_history:{task.user_id}:*"):
                keys_to_delete.append(key)
            if keys_to_delete:
                await redis_client.delete(*keys_to_delete)
            
            
            
async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1) 

    queue = await channel.declare_queue(
        "task_queue",
        durable=True,
    )

    await queue.consume(process_message)

    print("Worker started. Waiting for messages...")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())