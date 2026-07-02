from datetime import datetime
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.repository.task_repository import TaskRepository
from fastapi import BackgroundTasks
from uuid import uuid4
import asyncio

from app.core.database import AsyncSessionLocal

from app.schemas.task import TaskCreate

class TaskService:
    def __init__(self, db:AsyncSession):
        self.task_repo = TaskRepository(db)
        
    async def create_task(
        self, 
        task:TaskCreate, 
        user_id: int, 
        background_tasks: BackgroundTasks
        ) -> Task | dict:        
        
        if task.complexity == "light":
            print("TaskStatus.COMPLETED =", TaskStatus.COMPLETED)
            print("TaskStatus.COMPLETED.value =", TaskStatus.COMPLETED.value)
            print("type =", type(TaskStatus.COMPLETED))
            
            task_obj = Task(
                title = task.title,
                description = task.description,
                priority = task.priority,
                payload = task.payload,
                status = TaskStatus.COMPLETED,
                tracking_token = None,
                user_id = user_id,
            )
            saved_task = await self.task_repo.save(task_obj)
            return saved_task
        else:
            token = uuid4()
            task_obj = Task(
                title = task.title,
                description = task.description,
                priority = task.priority,
                payload = task.payload,
                status = TaskStatus.QUEUED,
                tracking_token = token,
                user_id = user_id,
            )
            saved_task = await self.task_repo.save(task_obj)
            background_tasks.add_task(simulate_heavy_processing, saved_task.id)
            return {
                "message": "Task accepted for processing",
                "tracking_token": str(token)
            }
            
    async def get_task_history(
        self, 
        user_id: int,
        status: TaskStatus | None,
        search_query: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int = 1,
        limit: int = 10,) -> dict:
        if search_query:
            search_query = search_query.strip() 
        tasks, total_count = await self.task_repo.get_paginated_tasks_for_user(
            user_id=user_id, status=status, search_query=search_query, start_date=start_date, end_date=end_date, page=page, limit=limit)
        return {
            "tasks": tasks,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
            
async def simulate_heavy_processing(task_id: int):
    await asyncio.sleep(10)
    async with AsyncSessionLocal() as db:
        task_repo = TaskRepository(db)
        task = await task_repo.get_task_by_id(task_id)
        if not task:
            return 
        task.status = TaskStatus.COMPLETED
        await db.commit()
        
        