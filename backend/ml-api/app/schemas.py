from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class HousingFeatures(BaseModel):
    """Seven-feature input matching the training dataset columns."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "square_footage": 1850,
                "bedrooms": 3,
                "bathrooms": 2,
                "year_built": 1998,
                "lot_size": 7500,
                "distance_to_city_center": 5.6,
                "school_rating": 8.2,
            }
        }
    )

    square_footage: Annotated[float, Field(gt=0, le=20000, description="Living area in sq ft")]
    bedrooms: Annotated[int, Field(ge=0, le=20)]
    bathrooms: Annotated[float, Field(ge=0, le=20)]
    year_built: Annotated[int, Field(ge=1800, le=2100)]
    lot_size: Annotated[float, Field(gt=0, le=500000, description="Lot size in sq ft")]
    distance_to_city_center: Annotated[float, Field(ge=0, le=500)]
    school_rating: Annotated[float, Field(ge=0, le=10)]


class SinglePredictionResponse(BaseModel):
    price: float


class BatchPredictionRequest(BaseModel):
    items: list[HousingFeatures]


class PredictionItem(BaseModel):
    price: float


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionItem]


class ModelMetrics(BaseModel):
    r2: float
    mae: float
    rmse: float
    cv_r2_mean: float
    cv_r2_std: float


class ModelInfoResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_type: str
    features: list[str]
    coefficients: dict[str, float]
    intercept: float
    metrics: ModelMetrics
    trained_at: str
    n_training_rows: int


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
