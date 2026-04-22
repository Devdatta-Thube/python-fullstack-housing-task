"""
HTTP client for ml-api. Mirrors estimator-api/app/ml_client.py in shape so the
error contract is consistent across both consumers of the ML service.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class MLServiceError(Exception):
    """Translates ml-api failures into a status_code + detail we can surface."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class MLClient:
    """Thin httpx wrapper around ml-api. Single instance per process."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self._base_url = (base_url or settings.ML_API_URL).rstrip("/")
        self._timeout = timeout if timeout is not None else settings.ML_API_TIMEOUT
        self._client: httpx.Client | None = None

    # ----- lifecycle -----

    def _get(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # ----- public API -----

    def health(self) -> dict[str, Any]:
        try:
            resp = self._get().get("/health")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as exc:
            logger.warning("ml-api unreachable: %s", exc)
            raise MLServiceError(502, f"ml-api unreachable: {exc}") from exc

    def model_info(self) -> dict[str, Any]:
        try:
            resp = self._get().get("/model-info")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise self._translate(exc)
        except httpx.RequestError as exc:
            raise MLServiceError(502, f"ml-api unreachable: {exc}") from exc

    def predict(self, features: dict[str, Any]) -> float:
        try:
            resp = self._get().post("/predict", json=features)
            resp.raise_for_status()
            body = resp.json()
            # ml-api returns {"price": <float>}; tolerate legacy {"predicted_price": ...}.
            return float(body.get("price", body.get("predicted_price")))
        except httpx.HTTPStatusError as exc:
            raise self._translate(exc)
        except httpx.RequestError as exc:
            raise MLServiceError(502, f"ml-api unreachable: {exc}") from exc

    # ----- error translation -----

    @staticmethod
    def _translate(exc: httpx.HTTPStatusError) -> MLServiceError:
        status = exc.response.status_code
        try:
            body = exc.response.json()
            detail = body.get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text

        if status == 503:
            return MLServiceError(503, str(detail))
        if status == 422:
            return MLServiceError(422, str(detail))
        return MLServiceError(502, f"ml-api error {status}: {detail}")


# Process-wide singleton. Django creates one per worker; tests override it.
_singleton: MLClient | None = None


def get_ml_client() -> MLClient:
    global _singleton
    if _singleton is None:
        _singleton = MLClient()
    return _singleton


def set_ml_client(client: MLClient | None) -> None:
    """Used by tests to swap in a fake."""
    global _singleton
    if _singleton is not None:
        _singleton.close()
    _singleton = client
