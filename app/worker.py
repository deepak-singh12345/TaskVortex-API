import asyncio
import json
from uuid import UUID

import aio_pika
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSessionLocal
from app.models.task import Task, TaskStatus
from app.repository.task_repository import TaskRepository
from app.core.redis import redis_client


import logging 

logger = logging.getLogger(__name__)

async def process_heavy_task():
    await asyncio.sleep(15)

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        
        logger.info(
            "Message received",
            extra={
                "context": {
                    "tracking_token": body["tracking_token"],
                    "user_id": body["user_id"],
                }
            },
        )

        async with AsyncSessionLocal() as db:
            
            repo = TaskRepository(db)

            
            task = Task(
                title=body["title"],
                description=body["description"],
                priority=body["priority"],
                payload=body["payload"],
                status=TaskStatus.PROCESSING,
                tracking_token=body["tracking_token"],
                user_id=body["user_id"],
            )
            try: 
                await repo.save(task)
                await db.commit() 
                await db.refresh(task) 
                
                # task.status = TaskStatus.PROCESSING
                
                # await db.commit()
                # await db.refresh(task)
                logger.info(
                    "Task processing started",
                    extra={
                        "context": {
                            "task_id": task.id,
                            "tracking_token": str(task.tracking_token)
                        }
                    }
                )
                # await process_heavy_task()
                await asyncio.wait_for(
                    process_heavy_task(),
                    timeout=10.0
                )
                
                task.status = TaskStatus.COMPLETED
                
                
                await db.commit()
                await db.refresh(task)
                
                logger.info(
                    "Task Completed",
                    extra={
                        "context": {
                            "task_id": task.id,
                            "tracking_token": str(task.tracking_token)
                        }
                    }
                )
                
                keys_to_delete = []
                async for key in redis_client.scan_iter(match=f"task_history:{task.user_id}:*"):
                    keys_to_delete.append(key)
                    
                if keys_to_delete:
                    await redis_client.delete(*keys_to_delete)
                    
                logger.info(
                        "Task history cache invalidated",
                        extra={
                            "context": {
                                "user_id": task.user_id,
                                "deleted_keys": len(keys_to_delete),
                            }
                        }
                    )
            except asyncio.TimeoutError:
                task.status = TaskStatus.FAILED
                await db.commit()
                await db.refresh(task)
                
                keys_to_delete = []
                async for key in redis_client.scan_iter(match=f"task_history:{task.user_id}:*"):
                    keys_to_delete.append(key)
                    
                if keys_to_delete:
                    await redis_client.delete(*keys_to_delete)
                    
                logger.info(
                        "Task history cache invalidated",
                        extra={
                            "context": {
                                "user_id": task.user_id,
                                "deleted_keys": len(keys_to_delete),
                            }
                        }
                    )

                logger.warning(
                    "Task processing timed out",
                    extra = {
                        "context": {
                            "task_id": task.id,
                            "tracking_token": str(task.tracking_token)
                        }
                    }
                )    
                
            except IntegrityError as e:
                await db.rollback()

                if getattr(e.orig, "sqlstate", None) == "23505":
                    logger.info(
                    "Duplicate task ignored",
                    extra={
                        "context": {
                            "tracking_token": body["tracking_token"]
                        }
                    }
                )
                    return

                logger.exception(
                    "Unexpected integrity error",
                    extra={
                        "context": {
                            "tracking_token": body["tracking_token"]
                        }
                    }
                )

                raise 


async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(
        "task_queue",
        durable=True,
    )

    await queue.consume(process_message)

    print("Worker started. Waiting for messages...")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())