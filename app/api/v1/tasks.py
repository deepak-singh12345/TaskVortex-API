from app.repository.task_repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_db

from fastapi import APIRouter, status
from app.schemas.task import TaskCreate 

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_task(payload: TaskCreate)->dict:
    """
    Ingests a new computational task and validates it's payload structure. 
    """
    return {
        "message": "Payload validated successfully",
        "received_task": payload.model_dump()
    }
    
@router.post("/create-test-task")
async def create_test_task(
    db: AsyncSession = Depends(get_db)
):
    task_repo = TaskRepository(db)

    task = await task_repo.create_task(
        title="Test Task",
        description="Testing task creation",
        task_type="web_scraping",
        priority=1,
        user_id=1
    )

    return {
        "id": task.id,
        "title": task.title,
        "user_id": task.user_id
    }