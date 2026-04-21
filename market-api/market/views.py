"""
DRF views. APIView (not ViewSets) — fewer layers of magic to explain.
"""

from __future__ import annotations

import logging
from typing import Any

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .exporters import rows_to_csv, stats_to_pdf
from .ml_client import MLServiceError, get_ml_client
from .serializers import WhatIfRequestSerializer
from .services import (
    FEATURE_COLUMNS,
    compute_stats,
    load_rows,
    paginate_rows,
)

logger = logging.getLogger(__name__)


class HealthView(APIView):
    """Degraded if ml-api is unreachable, ok otherwise."""

    def get(self, request):
        ml = get_ml_client()
        ml_reachable = True
        ml_model_loaded = False
        detail = "ok"
        try:
            ml_health = ml.health()
            ml_model_loaded = bool(ml_health.get("model_loaded"))
            if not ml_model_loaded:
                detail = "ml-api reachable but model not loaded"
        except MLServiceError as exc:
            ml_reachable = False
            detail = exc.detail

        try:
            row_count = len(load_rows())
        except FileNotFoundError as exc:
            return Response(
                {
                    "status": "degraded",
                    "dataset_loaded": False,
                    "ml_api_reachable": ml_reachable,
                    "ml_api_model_loaded": ml_model_loaded,
                    "detail": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        body = {
            "status": "ok" if (ml_reachable and ml_model_loaded) else "degraded",
            "dataset_loaded": True,
            "dataset_rows": row_count,
            "ml_api_reachable": ml_reachable,
            "ml_api_model_loaded": ml_model_loaded,
            "detail": detail,
        }
        return Response(body)


class StatsView(APIView):
    def get(self, request):
        try:
            return Response(compute_stats())
        except FileNotFoundError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class RowsView(APIView):
    """GET /api/rows/?limit=&offset=&sort_by=&desc=&min_price=&max_price=&bedrooms="""

    def get(self, request):
        def _int(key: str, default: int) -> int:
            val = request.query_params.get(key)
            return int(val) if val is not None and val != "" else default

        def _float_opt(key: str) -> float | None:
            val = request.query_params.get(key)
            return float(val) if val is not None and val != "" else None

        def _int_opt(key: str) -> int | None:
            val = request.query_params.get(key)
            return int(val) if val is not None and val != "" else None

        try:
            result = paginate_rows(
                limit=_int("limit", 20),
                offset=_int("offset", 0),
                sort_by=request.query_params.get("sort_by", "id"),
                descending=request.query_params.get("desc") == "1",
                min_price=_float_opt("min_price"),
                max_price=_float_opt("max_price"),
                bedrooms=_int_opt("bedrooms"),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        except FileNotFoundError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(result)


class WhatIfView(APIView):
    """
    POST /api/what-if/  {features, baseline_id?}

    Forwards the features to ml-api /predict, and — if baseline_id is given —
    also returns that dataset row plus the delta from actual price.
    """

    def post(self, request):
        serializer = WhatIfRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        features: dict[str, Any] = serializer.validated_data["features"]
        baseline_id: int | None = serializer.validated_data.get("baseline_id")

        try:
            predicted = get_ml_client().predict(features)
        except MLServiceError as exc:
            return Response({"detail": exc.detail}, status=exc.status_code)

        body: dict[str, Any] = {
            "features": features,
            "predicted_price": predicted,
        }

        if baseline_id is not None:
            rows = load_rows()
            match = next((r for r in rows if r["id"] == baseline_id), None)
            if match is None:
                return Response(
                    {"detail": f"baseline_id {baseline_id} not in dataset"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            body["baseline"] = match
            body["delta_from_actual"] = round(predicted - match["price"], 2)

        return Response(body)


# ---------------------------- exports ----------------------------


class ExportCsvView(APIView):
    def get(self, request):
        try:
            rows = load_rows()
        except FileNotFoundError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        columns = ["id", *FEATURE_COLUMNS, "price"]
        payload = rows_to_csv(rows, columns)
        resp = HttpResponse(payload, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="housing.csv"'
        return resp


class ExportPdfView(APIView):
    def get(self, request):
        try:
            stats = compute_stats()
        except FileNotFoundError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        payload = stats_to_pdf(stats)
        resp = HttpResponse(payload, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="market-summary.pdf"'
        return resp
