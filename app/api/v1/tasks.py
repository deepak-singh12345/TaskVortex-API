

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