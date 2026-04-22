from fastapi import APIRouter, Depends

from app.dependencies import get_model_service
from app.model import ModelService
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(svc: ModelService = Depends(get_model_service)) -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=svc.is_loaded)
