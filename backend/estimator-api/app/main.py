from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_db_path, get_ml_api_timeout, get_ml_api_url
from app.db import init_db
from app.ml_client import MLClient
from app.routers import estimate, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = get_db_path()
    init_db(db_path)
    app.state.db_path = db_path
    app.state.ml_client = MLClient(get_ml_api_url(), timeout=get_ml_api_timeout())
    try:
        yield
    finally:
        app.state.ml_client.close()


app = FastAPI(
    title="Property Value Estimator API",
    description=(
        "Task 2 App 1 backend. Validates property submissions, forwards to "
        "ml-api for a price prediction, and persists each submission to a "
        "SQLite history table."
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
app.include_router(estimate.router)
