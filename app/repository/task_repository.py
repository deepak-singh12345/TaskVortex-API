from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.task import Task, TaskStatus

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db
        
    # async def create_task(
    #     self,
    #     title: str,
    #     description: str | None,
    #     # task_type: str,
    #     priority: int,
    #     user_id: int,
    #     payload: dict,
    #     status: str,
    #     tracking_token: str
    # ) -> Task:
    #     task = Task(
    #         title=title,
    #         description=description,
    #         # task_type=task_type,
    #         priority=priority,
    #         user_id=user_id
    #     )

    #     self.db.add(task)
    #     await self.db.commit()
    #     await self.db.refresh(task)

    #     return task
    
    async def save(self, task: Task) -> None:
        self.db.add(task)
        
        return None
        
    async def get_task_by_id(self, task_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id) 
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        return task 
    
    async def get_tasks_by_user(self, user_id: int) -> list[Task]:
        stmt = select(Task).where(Task.user_id == user_id)
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        return tasks 
    
    async def get_paginated_tasks_for_user(
        self, 
        user_id: int, 
        status: TaskStatus | None =None, 
        search_query: str| None=None, 
        start_date: datetime | None=None, 
        end_date: datetime | None=None, 
        page: int=1, 
        limit: int=10) -> tuple[list[Task], int]:
        
        stmt = select(Task).where(Task.user_id == user_id)
        
        if status is not None:
            stmt = stmt.where(Task.status == status)
        
        if search_query is not None:
            stmt = stmt.where(Task.title.ilike(f"%{search_query}%"))
        
        if start_date is not None:
            stmt = stmt.where(Task.created_at >= start_date)
            
        if end_date is not None:
            stmt = stmt.where(Task.created_at <= end_date)
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar_one()
        
        offset = (page - 1) * limit
        stmt = stmt.order_by(Task.created_at.desc())
        paginated_stmt = stmt.limit(limit).offset(offset)
        
        tasks_result = await self.db.execute(paginated_stmt)
        tasks = tasks_result.scalars().all()
        
        return tasks, total_count