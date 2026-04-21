from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class HousingFeatures(BaseModel):
    """Mirror of ml-api's HousingFeatures. Kept separately so this service can
    evolve its own validation rules independently if needed."""

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

    square_footage: Annotated[float, Field(gt=0, le=20000)]
    bedrooms: Annotated[int, Field(ge=0, le=20)]
    bathrooms: Annotated[float, Field(ge=0, le=20)]
    year_built: Annotated[int, Field(ge=1800, le=2100)]
    lot_size: Annotated[float, Field(gt=0, le=500000)]
    distance_to_city_center: Annotated[float, Field(ge=0, le=500)]
    school_rating: Annotated[float, Field(ge=0, le=10)]


class EstimateRequest(BaseModel):
    features: HousingFeatures
    label: str | None = Field(default=None, max_length=100)


class EstimateResponse(BaseModel):
    id: str
    features: HousingFeatures
    predicted_price: float
    label: str | None
    created_at: datetime


class HistoryListResponse(BaseModel):
    items: list[EstimateResponse]
    total: int


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    ml_api_reachable: bool
    ml_api_model_loaded: bool | None = None
