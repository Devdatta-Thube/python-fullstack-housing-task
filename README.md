# Housing Price — Fullstack Application

A small multi-service application that trains a regression model on a housing
dataset and exposes it through a REST API, a second REST backend, and a web
portal. The entire stack runs with a single `docker compose up`.

## Services

| Service          | Framework                 | Port  | Responsibility                                                |
|------------------|---------------------------|-------|---------------------------------------------------------------|
| `ml-api`         | FastAPI + scikit-learn    | 8000  | Owns the trained model. The only service that imports sklearn.|
| `estimator-api`  | FastAPI                   | 8001  | Forwards predictions to `ml-api` and stores submission history in SQLite. |
| `market-api`     | Django 5 + DRF            | 8002  | Aggregate stats, dataset browser, what-if analysis, CSV/PDF export. |
| `portal`         | Next.js 16 + Tailwind v4  | 3000  | Web UI with `/estimator` and `/market` routes.                |

All four services run on a single Docker network. Inter-service calls use
Docker DNS (`http://ml-api:8000`); browser-side env vars point at
`http://localhost:800X`.

## Architecture

```
         ┌────────────┐          ┌────────────────┐
Browser  │   portal   │  HTTP →  │ estimator-api  │ ──► ml-api   (single predict)
(3000)   │  (Next.js) │          └────────────────┘     + SQLite history
         │            │          ┌────────────────┐
         │            │  HTTP →  │   market-api   │ ──► ml-api   (what-if)
         │            │          │ (Django + DRF) │     + LocMemCache of aggregates
         └────────────┘          └────────────────┘
```

`ml-api` is the single source of truth for predictions. The other two backends
are HTTP clients — they never import scikit-learn. The feature order in
`ml-api/app/model.py::FEATURE_COLUMNS` is the contract between the model
artefact and every downstream caller.

## Prerequisites

- Docker Desktop / Docker Engine with compose v2
- A copy of the housing dataset (see **[DATA.md](DATA.md)** — the dataset is
  *not* shipped with this repository and must be provided before building).

Optional, only if you want to run services outside Docker for development:

- Python 3.12 (WSL Ubuntu on Windows)
- Node 24 via `nvm` (Next 16 / Tailwind v4 require a modern Node)

## Quick start

1. Place the dataset as described in [DATA.md](DATA.md). Without it the
   container builds will fail at the `COPY data` step.
2. From the repository root:

   ```bash
   docker compose up --build -d
   ```

3. Wait ~30 seconds for healthchecks to settle, then confirm all four
   services report `healthy`:

   ```bash
   docker compose ps
   ```

4. Open in your browser:

   - Portal — <http://localhost:3000>
     - `/estimator` — submit features, see prediction, browse past submissions.
     - `/market` — aggregate stats, dataset table, what-if analysis, exports.
   - `ml-api` Swagger — <http://localhost:8000/docs>
   - `estimator-api` Swagger — <http://localhost:8001/docs>
   - `market-api` health — <http://localhost:8002/api/health/>

To stop:

```bash
docker compose down           # stop and remove containers
docker compose down -v        # also drop the estimator-data SQLite volume
```

## Developing a single service

Each service runs stand-alone outside Docker. Entry points and commands are
listed in each service's own `README.md`:

- [`ml-api/README.md`](ml-api/README.md) — training (`python train.py`), dev server (`uvicorn app.main:app`).
- [`estimator-api/README.md`](estimator-api/README.md) — dev server on :8001, tests with a fake ml-client.
- `market-api/` — `python manage.py runserver 8002`, tests via `python manage.py test market`.
- `portal/` — `npm run dev` (Node 24 required), `npx tsc --noEmit` to typecheck.

## Repository layout

```
ml-api/              Task 1  — FastAPI + scikit-learn. Trains at build time.
estimator-api/       Task 2 App 1 — FastAPI forwarder + SQLite history.
market-api/          Task 2 App 2 — Django + DRF aggregates + exports.
portal/              Next.js App Router. /estimator and /market pages.
docker-compose.yml   Brings all four services up on one network.
DATA.md              How to supply the dataset (not included in this repo).
```

## Design choices

- **Single source of truth for the model.** Only `ml-api` imports scikit-learn.
  Retraining happens once, in `ml-api/train.py`, triggered during
  `docker build`. The two other backends treat the model as a remote service.
- **Two backend frameworks by design.** FastAPI (estimator) and Django + DRF
  (market) exercise two different Python backend styles — a lightweight
  async-ready service versus a batteries-included framework — without the
  overhead of running two language ecosystems.
- **`market-api` has no database.** The dataset is a small CSV; using the
  Django ORM for 50 rows would be theatre. `DATABASES` is `:memory:` and is
  never touched; the CSV is loaded into `LocMemCache` on first request.
- **Two separate `/predict` endpoints on `ml-api`.** `/predict` takes a single
  record and `/predict/batch` takes a list. A union type would muddy the
  OpenAPI schema.
- **Cached aggregates.** `GET /api/stats/` is cached for 5 minutes
  (`AGGREGATE_CACHE_TTL`). Rows endpoints are not cached because they take
  query parameters; filter/sort runs over the cached in-memory list.
- **Artefacts are built, not committed.** `ml-api/artifacts/model.pkl` is
  produced by `train.py` or the Docker build. Tests regenerate it via a
  pytest fixture if missing.
- **Portal is one app, two pages.** `/estimator` and `/market` share one layout
  and one header. Shared UI primitives live under `portal/components/ui/`.

## API surface

### `ml-api` (port 8000)
- `GET /health` — liveness + whether model is loaded
- `GET /model-info` — model type, training date, feature columns, metrics
- `POST /predict` — single `HousingFeatures` → `{ "price": <float> }`
- `POST /predict/batch` — `{ "items": [...] }` → `{ "predictions": [...] }`

### `estimator-api` (port 8001)
- `GET /health`
- `POST /api/estimate` — forwards to `ml-api`, persists submission, returns full record
- `GET /api/history`, `GET /api/history/{id}`
- `DELETE /api/history/{id}`, `DELETE /api/history`

### `market-api` (port 8002)
- `GET /api/health/`
- `GET /api/stats/` — count, price summary, 8-bucket histogram, feature summaries, bedroom distribution
- `GET /api/rows/` — paginated dataset with `limit`, `offset`, `sort_by`, `desc`, `bedrooms`, `min_price`, `max_price`
- `POST /api/what-if/` — `{ features, baseline_id? }` → prediction plus optional delta vs a dataset row
- `GET /api/export/csv/` — dataset as CSV
- `GET /api/export/pdf/` — one-page PDF of stats + top rows (reportlab)

## Smoke tests (with the stack running)

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8001/health
curl -s http://localhost:8002/api/health/
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/
curl -sf http://localhost:8002/api/stats/ | python3 -m json.tool | head
```

## License

Interview deliverable; not licensed for redistribution.
