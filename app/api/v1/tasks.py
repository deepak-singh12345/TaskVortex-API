from datetime import datetime

from app.core.auth import get_current_user
from app.models.task import TaskStatus
from app.models.user import User
from app.repository.task_repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, Depends, HTTPException
from app.core.database import get_db

from fastapi import APIRouter, status, Query
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService 

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    task: TaskCreate, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Ingests a new computational task and validates it's payload structure. 
    """
    
    task_service = TaskService(db)
    result = await task_service.create_task(task=task, background_tasks=background_tasks, user_id=current_user.id)
    return result

@router.get("/history")
async def get_task_history(
    status: TaskStatus | None = None,
    search_query: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    
    # 3. Optional Query Parameters (With fallback defaults)
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service = TaskService(db)
    
    response = await task_service.get_task_history(
        user_id=current_user.id,
        status=status,
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )

    return response
    
@router.patch("/{task_id}")
async def update_task(
    task: TaskUpdate,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    result = await task_service.update_task(user_id=current_user.id, task_id=task_id, task_update=task)
    return result 
    
# @router.post("/create-test-task")
# async def create_test_task(
#     db: AsyncSession = Depends(get_db) 
# ):
#     task_repo = TaskRepository(db)

#     task = await task_repo.create_task(
#         title="Test Task",
#         description="Testing task creation",
#         task_type="web_scraping",
#         priority=1,
#         user_id=1
#     )

#     return {
#         "id": task.id,
#         "title": task.title,
#         "user_id": task.user_id
#     }