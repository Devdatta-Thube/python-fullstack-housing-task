from fastapi.testclient import TestClient

from app.main import app

SAMPLE: dict = {
    "square_footage": 1850,
    "bedrooms": 3,
    "bathrooms": 2,
    "year_built": 1998,
    "lot_size": 7500,
    "distance_to_city_center": 5.6,
    "school_rating": 8.2,
}


def _client() -> TestClient:
    return TestClient(app)


def test_health() -> None:
    with _client() as client:
        r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_model_info() -> None:
    with _client() as client:
        r = client.get("/model-info")
    assert r.status_code == 200
    body = r.json()
    assert body["model_type"] == "LinearRegression"
    assert len(body["features"]) == 7
    assert "square_footage" in body["coefficients"]
    assert body["metrics"]["r2"] > 0.5
    assert body["n_training_rows"] == 50


def test_predict_single() -> None:
    with _client() as client:
        r = client.post("/predict", json=SAMPLE)
    assert r.status_code == 200
    assert r.json()["price"] > 0


def test_predict_batch() -> None:
    with _client() as client:
        r = client.post("/predict/batch", json={"items": [SAMPLE, SAMPLE]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["predictions"]) == 2
    assert body["predictions"][0]["price"] > 0


def test_predict_validation_error() -> None:
    bad = {**SAMPLE, "bedrooms": -1}
    with _client() as client:
        r = client.post("/predict", json=bad)
    assert r.status_code == 422


def test_predict_batch_empty() -> None:
    with _client() as client:
        r = client.post("/predict/batch", json={"items": []})
    assert r.status_code == 400
