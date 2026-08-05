from fastapi import APIRouter

from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/v1/metrics", tags=["Metrics"])


@router.get("/health")
async def get_metrics_health():
    service = MetricsService()
    return await service.get_health()

