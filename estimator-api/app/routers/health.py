from fastapi import APIRouter, Depends

from app.dependencies import get_ml_client
from app.ml_client import MLClient
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(ml: MLClient = Depends(get_ml_client)) -> HealthResponse:
    ml_health = ml.health()
    if ml_health is None:
        return HealthResponse(
            status="degraded",
            ml_api_reachable=False,
            ml_api_model_loaded=None,
        )
    return HealthResponse(
        status="ok",
        ml_api_reachable=True,
        ml_api_model_loaded=bool(ml_health.get("model_loaded", False)),
    )
