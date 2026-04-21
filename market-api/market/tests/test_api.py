"""
End-to-end-ish tests using Django's test client + DRF.

ml-api is faked via `market.ml_client.set_ml_client(FakeClient(...))` — the
real service is never contacted.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from market import ml_client, services


class _FakeClient:
    """Stand-in for MLClient used in tests."""

    def __init__(
        self,
        *,
        reachable: bool = True,
        model_loaded: bool = True,
        price: float = 123456.0,
        predict_raises: Exception | None = None,
    ):
        self._reachable = reachable
        self._model_loaded = model_loaded
        self._price = price
        self._predict_raises = predict_raises
        self.predict_calls: list[dict[str, Any]] = []

    def health(self) -> dict[str, Any]:
        if not self._reachable:
            raise ml_client.MLServiceError(502, "ml-api unreachable (fake)")
        return {"status": "ok", "model_loaded": self._model_loaded}

    def model_info(self) -> dict[str, Any]:  # pragma: no cover
        return {"model_type": "fake", "feature_columns": services.FEATURE_COLUMNS}

    def predict(self, features: dict[str, Any]) -> float:
        self.predict_calls.append(features)
        if self._predict_raises is not None:
            raise self._predict_raises
        return self._price

    def close(self) -> None:  # pragma: no cover
        pass


class MarketApiTests(SimpleTestCase):
    """All endpoints. No DB migrations needed — we don't use the ORM."""

    databases: set[str] = set()  # opt out of DB setup entirely

    def setUp(self) -> None:
        cache.clear()
        self.client = APIClient()
        self.fake = _FakeClient()
        ml_client.set_ml_client(self.fake)

    def tearDown(self) -> None:
        ml_client.set_ml_client(None)
        cache.clear()

    # ---------- health ----------

    def test_health_ok(self):
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "ok")
        self.assertTrue(body["dataset_loaded"])
        self.assertEqual(body["dataset_rows"], 50)
        self.assertTrue(body["ml_api_reachable"])
        self.assertTrue(body["ml_api_model_loaded"])

    def test_health_degraded_when_ml_unreachable(self):
        ml_client.set_ml_client(_FakeClient(reachable=False))
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "degraded")
        self.assertFalse(body["ml_api_reachable"])

    # ---------- stats ----------

    def test_stats_shape(self):
        resp = self.client.get(reverse("stats"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["count"], 50)
        self.assertIn("price", body)
        self.assertIn("min", body["price"])
        self.assertIn("histogram", body["price"])
        self.assertIn("features", body)
        for feat in services.FEATURE_COLUMNS:
            self.assertIn(feat, body["features"])
            for key in ("min", "max", "mean", "median"):
                self.assertIn(key, body["features"][feat])
        self.assertIsInstance(body["bedrooms"], list)
        self.assertGreater(len(body["bedrooms"]), 0)

    # ---------- rows ----------

    def test_rows_default(self):
        resp = self.client.get(reverse("rows"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total"], 50)
        self.assertEqual(len(body["items"]), 20)
        # default sort is by id ascending
        ids = [r["id"] for r in body["items"]]
        self.assertEqual(ids, sorted(ids))

    def test_rows_filter_bedrooms(self):
        resp = self.client.get(reverse("rows"), {"bedrooms": 3, "limit": 200})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertGreater(body["total"], 0)
        self.assertTrue(all(r["bedrooms"] == 3 for r in body["items"]))

    def test_rows_sort_desc(self):
        resp = self.client.get(
            reverse("rows"), {"sort_by": "price", "desc": "1", "limit": 5}
        )
        body = resp.json()
        prices = [r["price"] for r in body["items"]]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_rows_invalid_sort_returns_400(self):
        resp = self.client.get(reverse("rows"), {"sort_by": "nope"})
        self.assertEqual(resp.status_code, 400)

    # ---------- what-if ----------

    _features = {
        "square_footage": 1850,
        "bedrooms": 3,
        "bathrooms": 2,
        "year_built": 1998,
        "lot_size": 7500,
        "distance_to_city_center": 5.6,
        "school_rating": 8.2,
    }

    def test_what_if_forwards_to_ml(self):
        self.fake = _FakeClient(price=250000.0)
        ml_client.set_ml_client(self.fake)
        resp = self.client.post(
            reverse("what-if"), {"features": self._features}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["predicted_price"], 250000.0)
        self.assertEqual(len(self.fake.predict_calls), 1)

    def test_what_if_with_baseline(self):
        self.fake = _FakeClient(price=250000.0)
        ml_client.set_ml_client(self.fake)
        resp = self.client.post(
            reverse("what-if"),
            {"features": self._features, "baseline_id": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("baseline", body)
        self.assertEqual(body["baseline"]["id"], 1)
        self.assertIn("delta_from_actual", body)

    def test_what_if_baseline_not_found(self):
        resp = self.client.post(
            reverse("what-if"),
            {"features": self._features, "baseline_id": 9999},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_what_if_validation_error(self):
        bad = {**self._features, "bedrooms": -1}
        resp = self.client.post(
            reverse("what-if"), {"features": bad}, format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_what_if_surface_ml_service_error(self):
        ml_client.set_ml_client(
            _FakeClient(
                predict_raises=ml_client.MLServiceError(503, "model not loaded")
            )
        )
        resp = self.client.post(
            reverse("what-if"), {"features": self._features}, format="json"
        )
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.json()["detail"], "model not loaded")

    # ---------- exports ----------

    def test_export_csv(self):
        resp = self.client.get(reverse("export-csv"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("text/csv"))
        body = resp.content.decode("utf-8")
        self.assertTrue(body.startswith("id,square_footage,"))
        self.assertEqual(len(body.splitlines()), 51)  # header + 50

    def test_export_pdf(self):
        resp = self.client.get(reverse("export-pdf"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF-"))
