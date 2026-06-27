from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User

class UserRepository:   
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db 
        
    async def create_user(self, name: str, email: str, hashed_password: str) -> User:
        user = User(name=name, email=email, hashed_password=hashed_password)  #An ORM object (instance of User class) is created in Python memory.
        self.db.add(user)   #Session starts tracking this object as a pending insert.
        await self.db.commit()  #We commit the transaction, causing SQLAlchemy to send INSERT SQL to PostgreSQL.
        await self.db.refresh(user)  #refresh() reloads database-generated values into the Python object.
        return user  #here we returned the user object with the values stored in the db
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.tasks))  #Blueprint of the sql query
        
        result = await self.db.execute(stmt)  #query is executed and a sqlalchemy result wrapper
        user = result.scalar_one_or_none()  #here data is extracted from the result, either the first column/object or none
        return user
    
    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user