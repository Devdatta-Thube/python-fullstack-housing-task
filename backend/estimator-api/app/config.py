import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_ml_api_url() -> str:
    return os.getenv("ML_API_URL", "http://localhost:8000")


def get_ml_api_timeout() -> float:
    return float(os.getenv("ML_API_TIMEOUT", "10.0"))


def get_db_path() -> Path:
    default = BASE_DIR / "data" / "history.db"
    return Path(os.getenv("ESTIMATOR_DB_PATH", str(default)))
