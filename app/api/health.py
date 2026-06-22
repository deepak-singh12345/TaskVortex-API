from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["System Health"])

@router.get("/health", response_model=dict[str, str])
async def health() -> dict[str, str]:
    """
    Returns the operational status of the core API service."""
    
    return {"status": "healthy"}