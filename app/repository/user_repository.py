from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User

class UserRepository:   
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db 
        
    async def create_user(self, user:User) -> None:
        # user = User(name=name, email=email, hashed_password=hashed_password)  #An ORM object (instance of User class) is created in Python memory.
        self.db.add(user)   #Session starts tracking this object as a pending insert.
        
        return None  #here we returned the user object with the values stored in the db
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)  #Blueprint of the sql query
        
        result = await self.db.execute(stmt)  #query is executed and a sqlalchemy result wrapper
        user = result.scalar_one_or_none()  #here data is extracted from the result, either the first column/object or none
        return user
    
    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user