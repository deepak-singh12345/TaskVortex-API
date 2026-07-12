from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .api.health import router as health_router
from .api.v1.tasks import router as tasks_router
from .api.v1.users import router as user_router
from .core.database import engine
from .models.base import Base
from .models import * 
from app.core.logging import listener, setup_logging
from app.middlewares.logging_middleware import LoggingMiddleware
import logging 

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting application and initializing database...")

    try:
        yield
    finally:
        listener.stop()
        logger.info("Application shutting down")



# @asynccontextmanager 
# async def lifespan(app: FastAPI):
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield 
#     await engine.dispose()


app = FastAPI(
    title="TaskVortex API",
    description="Production-grade asynchronous task orchestration engine.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(
                str(loc) for loc in error["loc"] if loc != "body"
            ),
            "issue": error["msg"],
            "rejected_value": error.get("input")
        })
        
    return JSONResponse(
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
        content = {
            'success': False, 
            "error_type": "ValidationError",
            "details": errors
        }
    )
    

app.include_router(health_router, prefix='/api')
app.include_router(tasks_router, prefix='/api')
app.include_router(user_router, prefix="/api")