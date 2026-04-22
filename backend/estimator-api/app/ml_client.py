from __future__ import annotations

import httpx


class MLServiceError(Exception):
    """Raised when ml-api is unreachable or returns an error status."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"ml-api error ({status_code}): {detail}")


class MLClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def predict(self, features: dict) -> float:
        try:
            response = self._client.post("/predict", json=features)
        except httpx.RequestError as exc:
            raise MLServiceError(
                502, f"cannot reach ml-api at {self.base_url}: {exc}"
            ) from exc

        if response.status_code == 422:
            raise MLServiceError(422, str(response.json().get("detail", "validation error")))
        if response.status_code == 503:
            raise MLServiceError(503, "ml-api model not loaded")
        if response.status_code >= 400:
            raise MLServiceError(response.status_code, response.text)

        return float(response.json()["price"])

    def health(self) -> dict | None:
        try:
            response = self._client.get("/health", timeout=3.0)
        except httpx.RequestError:
            return None
        if response.status_code != 200:
            return None
        return response.json()
