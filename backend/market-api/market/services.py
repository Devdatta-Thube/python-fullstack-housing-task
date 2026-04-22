"""
Dataset loader + aggregate computation.

The dataset is tiny (~50 rows), so we can:
  1. Read the entire CSV into a list of dicts at first access,
  2. Compute aggregates on the fly and cache them via Django's cache.

If the dataset grew into the thousands, swap the loader for pandas and the
aggregates for NumPy. The public functions' return shapes would not change.
"""

from __future__ import annotations

import csv
import logging
import statistics
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Order matches ml-api/app/model.py::FEATURE_COLUMNS. The market-api itself
# does not call scikit-learn, but the feature order is load-bearing for
# any what-if payloads forwarded to ml-api.
FEATURE_COLUMNS = [
    "square_footage",
    "bedrooms",
    "bathrooms",
    "year_built",
    "lot_size",
    "distance_to_city_center",
    "school_rating",
]

INT_COLUMNS = {"bedrooms", "year_built"}
NUMERIC_COLUMNS = {*FEATURE_COLUMNS, "price"}

ROWS_CACHE_KEY = "market:rows:v1"
STATS_CACHE_KEY = "market:stats:v1"


def _coerce(row: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, raw in row.items():
        if key is None:
            continue
        # Strip BOM from the first header if present.
        clean_key = key.lstrip("\ufeff").strip()
        value = raw.strip() if isinstance(raw, str) else raw
        if clean_key in INT_COLUMNS or clean_key == "id":
            out[clean_key] = int(value)
        elif clean_key in NUMERIC_COLUMNS:
            out[clean_key] = float(value)
        else:
            out[clean_key] = value
    return out


def _dataset_path() -> Path:
    return Path(settings.DATASET_PATH)


def load_rows() -> list[dict[str, Any]]:
    """Return every row with typed values. Cached for AGGREGATE_CACHE_TTL."""
    cached = cache.get(ROWS_CACHE_KEY)
    if cached is not None:
        return cached

    path = _dataset_path()
    if not path.exists():
        logger.error("Dataset missing at %s", path)
        raise FileNotFoundError(f"Dataset not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [_coerce(r) for r in reader]

    cache.set(ROWS_CACHE_KEY, rows, settings.AGGREGATE_CACHE_TTL)
    logger.info("Loaded %d rows from %s", len(rows), path)
    return rows


# ------------------------------ Aggregates -------------------------------


def _summary(values: list[float]) -> dict[str, float]:
    """min / max / mean / median for a non-empty list of numbers."""
    return {
        "min": float(min(values)),
        "max": float(max(values)),
        "mean": round(statistics.fmean(values), 2),
        "median": float(statistics.median(values)),
    }


def _histogram(values: list[float], bins: int = 8) -> list[dict[str, Any]]:
    """Uniform-width histogram. Returns [{range, count}] for chart rendering."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [{"range": f"{lo:g}", "count": len(values)}]

    width = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        # Index = floor((v - lo) / width), clamped to the last bin.
        idx = min(int((v - lo) / width), bins - 1)
        counts[idx] += 1

    return [
        {
            "range": f"{lo + i * width:.0f}–{lo + (i + 1) * width:.0f}",
            "count": counts[i],
        }
        for i in range(bins)
    ]


def _distribution(values: list[Any]) -> list[dict[str, Any]]:
    """Categorical distribution, sorted by key."""
    buckets: dict[Any, int] = {}
    for v in values:
        buckets[v] = buckets.get(v, 0) + 1
    return [
        {"value": k, "count": v}
        for k, v in sorted(buckets.items(), key=lambda kv: kv[0])
    ]


def compute_stats() -> dict[str, Any]:
    """Aggregate statistics over the dataset. Cached."""
    cached = cache.get(STATS_CACHE_KEY)
    if cached is not None:
        return cached

    rows = load_rows()
    if not rows:
        return {"count": 0, "price": None, "features": {}, "bedrooms": []}

    prices = [r["price"] for r in rows]
    stats: dict[str, Any] = {
        "count": len(rows),
        "price": {
            **_summary(prices),
            "histogram": _histogram(prices, bins=8),
        },
        "features": {
            col: _summary([r[col] for r in rows]) for col in FEATURE_COLUMNS
        },
        "bedrooms": _distribution([r["bedrooms"] for r in rows]),
    }

    cache.set(STATS_CACHE_KEY, stats, settings.AGGREGATE_CACHE_TTL)
    return stats


# ------------------------------ Paginated rows ---------------------------


ALLOWED_SORT_KEYS = {"id", "price", *FEATURE_COLUMNS}


def paginate_rows(
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "id",
    descending: bool = False,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
) -> dict[str, Any]:
    """Filter + sort + paginate. No caching — filter combinations blow up."""
    if sort_by not in ALLOWED_SORT_KEYS:
        raise ValueError(f"sort_by must be one of {sorted(ALLOWED_SORT_KEYS)}")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    rows = load_rows()

    def keep(row: dict[str, Any]) -> bool:
        if min_price is not None and row["price"] < min_price:
            return False
        if max_price is not None and row["price"] > max_price:
            return False
        if bedrooms is not None and row["bedrooms"] != bedrooms:
            return False
        return True

    filtered = [r for r in rows if keep(r)]
    filtered.sort(key=lambda r: r[sort_by], reverse=descending)
    page = filtered[offset : offset + limit]
    return {"total": len(filtered), "items": page}
