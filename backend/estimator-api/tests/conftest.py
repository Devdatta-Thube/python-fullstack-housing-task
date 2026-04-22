from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class FakeMLClient:
    """Stand-in for MLClient. Lets tests run without ml-api being up."""

    def __init__(self) -> None:
        self.predict_price: float = 250_000.0
        self.reachable: bool = True
        self.model_loaded: bool = True
        self.raise_on_predict: Exception | None = None
        self.calls: list[dict] = []

    def predict(self, features: dict) -> float:
        if self.raise_on_predict is not None:
            raise self.raise_on_predict
        self.calls.append(features)
        return self.predict_price

    def health(self) -> dict | None:
        if not self.reachable:
            return None
        return {"status": "ok", "model_loaded": self.model_loaded}

    def close(self) -> None:
        pass


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ESTIMATOR_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("ML_API_URL", "http://ml-api-not-used-in-tests.invalid")

    from app.main import app

    with TestClient(app) as c:
        # Swap the real MLClient out for our fake. The real one was created
        # during lifespan startup and never actually called because all tests
        # go through this fixture.
        app.state.ml_client.close()
        fake = FakeMLClient()
        app.state.ml_client = fake
        yield c, fake
