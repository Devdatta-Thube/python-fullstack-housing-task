from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.model import ModelService
from app.routers import health, model_info, predict

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = ModelService(ARTIFACTS_DIR)
    try:
        service.load()
    except FileNotFoundError as exc:
        print(f"[ml-api] WARNING: {exc}")
    app.state.model_service = service
    yield


app = FastAPI(
    title="Housing Price ML API",
    description=(
        "Predicts house prices from seven features using a linear regression "
        "model trained on the provided dataset."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(model_info.router)
