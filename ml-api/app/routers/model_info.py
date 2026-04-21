from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_model_service
from app.model import ModelService
from app.schemas import ModelInfoResponse

router = APIRouter(tags=["model"])


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(svc: ModelService = Depends(get_model_service)) -> ModelInfoResponse:
    if not svc.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded.",
        )
    return ModelInfoResponse(**svc.metadata)
