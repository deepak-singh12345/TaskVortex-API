from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task

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
    
    async def save(self, task: Task) -> Task:
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task 
        
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