from app.ml_client import MLServiceError

SAMPLE_FEATURES: dict = {
    "square_footage": 1850,
    "bedrooms": 3,
    "bathrooms": 2,
    "year_built": 1998,
    "lot_size": 7500,
    "distance_to_city_center": 5.6,
    "school_rating": 8.2,
}


def test_health_ok(client):
    c, fake = client
    fake.reachable = True
    fake.model_loaded = True
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["ml_api_reachable"] is True
    assert body["ml_api_model_loaded"] is True


def test_health_degraded_when_ml_unreachable(client):
    c, fake = client
    fake.reachable = False
    r = c.get("/health")
    body = r.json()
    assert body["status"] == "degraded"
    assert body["ml_api_reachable"] is False


def test_estimate_forwards_to_ml_and_persists(client):
    c, fake = client
    fake.predict_price = 285_000.0
    r = c.post("/estimate", json={"features": SAMPLE_FEATURES, "label": "My house"})
    assert r.status_code == 201
    body = r.json()
    assert body["predicted_price"] == 285_000.0
    assert body["label"] == "My house"
    assert "id" in body

    # MLClient was invoked with the submitted features
    assert len(fake.calls) == 1
    assert fake.calls[0]["square_footage"] == 1850

    # Row persisted to history
    r2 = c.get("/history")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["total"] == 1
    assert body2["items"][0]["id"] == body["id"]


def test_estimate_validation_error_returns_422(client):
    c, _ = client
    bad = {"features": {**SAMPLE_FEATURES, "bedrooms": -1}}
    r = c.post("/estimate", json=bad)
    assert r.status_code == 422


def test_estimate_surfaces_ml_errors(client):
    c, fake = client
    fake.raise_on_predict = MLServiceError(502, "cannot reach ml-api")
    r = c.post("/estimate", json={"features": SAMPLE_FEATURES})
    assert r.status_code == 502
    assert "ml-api" in r.json()["detail"]


def test_history_pagination(client):
    c, _ = client
    for i in range(5):
        c.post("/estimate", json={"features": SAMPLE_FEATURES, "label": f"h{i}"})
    r = c.get("/history?limit=2")
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_get_and_delete_history(client):
    c, _ = client
    post = c.post("/estimate", json={"features": SAMPLE_FEATURES})
    rid = post.json()["id"]

    r_get = c.get(f"/history/{rid}")
    assert r_get.status_code == 200
    assert r_get.json()["id"] == rid

    r_del = c.delete(f"/history/{rid}")
    assert r_del.status_code == 204

    r_missing = c.get(f"/history/{rid}")
    assert r_missing.status_code == 404


def test_clear_history(client):
    c, _ = client
    for _ in range(3):
        c.post("/estimate", json={"features": SAMPLE_FEATURES})
    r = c.delete("/history")
    assert r.json()["deleted"] == 3
    assert c.get("/history").json()["total"] == 0
