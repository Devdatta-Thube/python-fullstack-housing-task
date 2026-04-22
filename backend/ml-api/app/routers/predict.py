from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_model_service
from app.model import ModelService
from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HousingFeatures,
    PredictionItem,
    SinglePredictionResponse,
)

router = APIRouter(tags=["predict"])


def _require_loaded(svc: ModelService) -> None:
    if not svc.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Train the model before serving.",
        )


@router.post("/predict", response_model=SinglePredictionResponse)
def predict_single(
    features: HousingFeatures,
    svc: ModelService = Depends(get_model_service),
) -> SinglePredictionResponse:
    _require_loaded(svc)
    prices = svc.predict([features.model_dump()])
    return SinglePredictionResponse(price=prices[0])


@router.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(
    body: BatchPredictionRequest,
    svc: ModelService = Depends(get_model_service),
) -> BatchPredictionResponse:
    _require_loaded(svc)
    if not body.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="items cannot be empty",
        )
    prices = svc.predict([f.model_dump() for f in body.items])
    return BatchPredictionResponse(
        predictions=[PredictionItem(price=p) for p in prices]
    )
