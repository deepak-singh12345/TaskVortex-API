from app.main import app
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import get_db 
from app.core.config import settings
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool


TEST_DATABASE_URL: str = settings.TEST_DATABASE_URL

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)
        
# app.dependency_overrides[get_db] = get_test_db


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client 
    
    app.dependency_overrides.clear()
        
    
@pytest_asyncio.fixture
async def db_connection():
    async with test_engine.connect() as connection:
        yield connection
        
@pytest_asyncio.fixture
async def db_transaction(db_connection):
    transaction = await db_connection.begin()
    yield db_connection
    await transaction.rollback()
    
    
@pytest_asyncio.fixture
async def db_session(db_transaction):
    session = AsyncSession(bind=db_transaction, expire_on_commit=False)
    yield session
    await session.close()