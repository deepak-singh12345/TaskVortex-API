from datetime import datetime
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.repository.task_repository import TaskRepository
from fastapi import BackgroundTasks, HTTPException
from uuid import uuid4
import asyncio
import json
from app.core.redis import redis_client

from app.core.database import AsyncSessionLocal

from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, db:AsyncSession):
        self.db = db
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
            await self.task_repo.save(task_obj)
            await self.db.commit()
            await self.db.refresh(task_obj)
            
            #invalidate cache
            keys = await redis_client.keys(f"task_history:{user_id}:*")
            if keys:
                await redis_client.delete(*keys)
            return task_obj
        
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
            await self.task_repo.save(task_obj)
            
            await self.db.commit()
            await self.db.refresh(task_obj)
            
            #invalidate cache
            
            keys = await redis_client.keys(f"task_history:{user_id}:*")
            if keys: 
                await redis_client.delete(*keys)            
            
            background_tasks.add_task(simulate_heavy_processing, task_obj.id)
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
            
        cache_key = (
            f"task_history:"
            f"{user_id}:"
            f"{status or 'all'}:"
            f"{search_query or 'none'}:"
            f"{start_date or 'none'}:"
            f"{end_date or 'none'}:"
            f"{page}:"
            f"{limit}"
        )
        cached_data = await redis_client.get(cache_key)

        if cached_data:
            print("Cache Hit")
            return json.loads(cached_data)

        print("Cache Miss")
        
        tasks, total_count = await self.task_repo.get_paginated_tasks_for_user(
            user_id=user_id, 
            status=status, 
            search_query=search_query, 
            start_date=start_date, 
            end_date=end_date, 
            page=page, 
            limit=limit)
        tasks_data = []

        for task in tasks:
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority,
                "payload": task.payload,
                "tracking_token": str(task.tracking_token) if task.tracking_token else None,
                "created_at": task.created_at.isoformat(),
            })
        response =  {
            "tasks": tasks_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
        await redis_client.set(cache_key, json.dumps(response), ex=300)
        return response 
    
    async def update_task(self, task_id: int, user_id: int, task_update: TaskUpdate):
        task = await self.task_repo.get_task_for_update(task_id, user_id)
        
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        update_data = task_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        for key, value in update_data.items():
            setattr(task, key, value)
        
        await self.db.commit()
        await self.db.refresh(task)  #commit writes and refresh reads back
        
        keys = await redis_client.keys(f"task_history:{user_id}:*")
        if keys:
            await redis_client.delete(*keys)
            
        return task
        
            
async def simulate_heavy_processing(task_id: int):
    await asyncio.sleep(10)
    async with AsyncSessionLocal() as db:
        task_repo = TaskRepository(db)
        task = await task_repo.get_task_by_id(task_id)
        if not task:
            return 
        task.status = TaskStatus.COMPLETED
        await db.commit()
        
        
