# market-api

Django 5 + Django REST Framework service for the "market" side of the
app. It exposes aggregate statistics over the training dataset,
paginated row access, CSV and PDF exports, and a what-if prediction
proxy that calls `ml-api`.

Part of the four-service stack — see the repo-root `README.md` and
`backend/README.md` for the big picture.

## Responsibilities

- Load the training CSV once into `LocMemCache` (TTL controlled by
  `AGGREGATE_CACHE_TTL`, default 300 s). No database is used — the
  Django `DATABASES` setting points at `:memory:` and is never touched.
- Compute summary statistics: price min/median/mean/max, an 8-bucket
  histogram, per-feature summaries, bedroom distribution.
- Serve the raw dataset with `limit`, `offset`, `sort_by`, `desc`,
  `bedrooms`, `min_price`, `max_price` query parameters.
- Forward what-if requests to `ml-api/predict` and optionally diff
  against any dataset row.
- Render CSV and PDF exports. PDF uses `reportlab`; DejaVuSans is
  registered at import time so the Indian rupee glyph (₹) renders.

## Endpoints (all under `/api/`)

| Method | Path              | Purpose                                          |
|--------|-------------------|--------------------------------------------------|
| GET    | `health/`         | Liveness + dataset-loaded check.                 |
| GET    | `stats/`          | Aggregate stats (cached).                        |
| GET    | `rows/`           | Filtered / sorted dataset rows.                  |
| POST   | `what-if/`        | Prediction + optional baseline delta.            |
| GET    | `export/csv/`     | Dataset as CSV.                                  |
| GET    | `export/pdf/`     | One-page PDF summary.                            |

DRF's browsable API is disabled (`JSONRenderer` only).

## Run the service on its own

```bash
# From backend/market-api/
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Dev server
.venv/bin/python manage.py runserver 8002

# Tests (no live ml-api needed — the ml-client is patched via
# market.ml_client.set_ml_client in the test suite)
.venv/bin/python manage.py test market -v 2
```

The dataset must be at `backend/market-api/data/housing.csv` (or
override via the `DATASET_PATH` environment variable). See
[`../../DATA.md`](../../DATA.md).

## Environment variables

- `ML_API_URL` (default `http://ml-api:8000`)
- `DATASET_PATH` (default `/app/data/housing.csv`)
- `AGGREGATE_CACHE_TTL` seconds (default `300`)
- `DJANGO_DEBUG` (`0` in production)
- `DJANGO_ALLOWED_HOSTS` (comma-separated)
- `DJANGO_SECRET_KEY`

## Notes worth knowing before editing

- `ml-api`'s `/predict` response returns `{"price": ...}` — the client
  in `market/ml_client.py` tolerates either `price` or
  `predicted_price`.
- `collectstatic` runs during the Docker build because
  `django.contrib.staticfiles` is installed, even though DRF's
  browsable API is off.
- `fonts-dejavu-core` is installed in the Docker image so reportlab can
  render the ₹ glyph in PDFs. When running outside Docker on a host
  without the font, the PDF falls back to an ASCII `Rs.` prefix.
