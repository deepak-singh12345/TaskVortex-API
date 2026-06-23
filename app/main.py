from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .api.health import router as health_router
from .api.v1.tasks import router as tasks_router

app = FastAPI(
    title="TaskVortex API",
    description="Production-grade asynchronous task orchestration engine.",
    version="1.0.0",
)

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