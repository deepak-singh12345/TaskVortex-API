from fastapi import FastAPI
from .api.health import router as health_router

app = FastAPI(
    title="TaskVortex API",
    description="Production-grade asynchronous task orchestration engine.",
    version="1.0.0",
)

app.include_router(health_router, prefix='/api')