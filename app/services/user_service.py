from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repository.task_repository import TaskRepository
from app.repository.user_repository import UserRepository
from app.core.security import hash_password
from app.core.exception import UserAlreadyExistsError
import asyncio 


class UserService:
    def __init__(self, db:AsyncSession):
        self.user_repo = UserRepository(db)
        self.task_repo = TaskRepository(db)
        
    async def get_user_with_tasks(self, user_id: int):
        user = await self.user_repo.get_user_by_id(user_id)

        return user 
    
    async def create_user(self, user_email: str, user_name: str, user_password: str):
        existing_user = await self.user_repo.get_user_by_email(user_email)
        
        if existing_user:
            raise UserAlreadyExistsError()
        
        hashed_password = hash_password(password=user_password)
        user = await self.user_repo.create_user(name=user_name, email=user_email, hashed_password=hashed_password)
        
        return user 
        
#         """
        
#         why sequential instead of doing concurrent 
#         user, tasks = await asyncio.gather(
#         self.user_repo.get_user_by_id(user_id),
#         self.task_repo.get_tasks_by_user(user_id)
#     )
#         classic tradeoff
# Concurrent approach

# Pros:

# Lower latency
# Faster responses

# Cons:

# May waste resources

# Best when:

# both queries are usually needed
# invalid requests are rare
# Sequential approach

# Pros:

# Efficient DB usage
# No wasted queries

# Cons:

# Higher latency

# Best when:

# second query depends on first
# invalid requests happen often"""
        