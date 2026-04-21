from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score

FEATURE_COLUMNS: list[str] = [
    "square_footage",
    "bedrooms",
    "bathrooms",
    "year_built",
    "lot_size",
    "distance_to_city_center",
    "school_rating",
]
TARGET_COLUMN = "price"

MODEL_FILENAME = "model.pkl"
METADATA_FILENAME = "metadata.json"


def train_and_save(csv_path: Path, artifacts_dir: Path) -> dict:
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    r2 = float(r2_score(y, y_pred))
    mae = float(mean_absolute_error(y, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=kf, scoring="r2")

    metadata = {
        "model_type": "LinearRegression",
        "features": FEATURE_COLUMNS,
        "coefficients": {
            feat: float(coef) for feat, coef in zip(FEATURE_COLUMNS, model.coef_)
        },
        "intercept": float(model.intercept_),
        "metrics": {
            "r2": r2,
            "mae": mae,
            "rmse": rmse,
            "cv_r2_mean": float(cv_scores.mean()),
            "cv_r2_std": float(cv_scores.std()),
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_training_rows": int(len(df)),
    }

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifacts_dir / MODEL_FILENAME)
    (artifacts_dir / METADATA_FILENAME).write_text(json.dumps(metadata, indent=2))
    return metadata


class ModelService:
    def __init__(self, artifacts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir
        self._model: LinearRegression | None = None
        self._metadata: dict | None = None

    def load(self) -> None:
        model_path = self.artifacts_dir / MODEL_FILENAME
        metadata_path = self.artifacts_dir / METADATA_FILENAME
        if not model_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Model artifacts not found in {self.artifacts_dir}. "
                "Run `python train.py` first."
            )
        self._model = joblib.load(model_path)
        self._metadata = json.loads(metadata_path.read_text())

    @property
    def is_loaded(self) -> bool:
        return self._model is not None and self._metadata is not None

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            raise RuntimeError("Model metadata is not loaded")
        return self._metadata

    def predict(self, features_list: list[dict]) -> list[float]:
        if self._model is None:
            raise RuntimeError("Model is not loaded")
        df = pd.DataFrame(features_list, columns=FEATURE_COLUMNS)
        preds = self._model.predict(df.values)
        return [float(p) for p in preds]
