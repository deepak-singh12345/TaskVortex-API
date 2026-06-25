from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.user_service import UserService
from app.repository.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
async def get_user_with_tasks(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    result = await service.get_user_with_tasks(user_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result 

@router.post("/create-test-user")
async def create_test_user(
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)

    user = await user_repo.create_user(
        name="Renu",
        email="renu@gmail.com"
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }