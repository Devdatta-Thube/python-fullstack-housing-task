# estimator-api — Property Value Estimator backend (Task 2, App 1)

Thin FastAPI service that sits between the portal frontend and `ml-api`. It
validates form submissions, forwards them to `ml-api`'s `/predict`, and
persists each submission + prediction in a SQLite history so the frontend can
show "previous estimates" and "compare side-by-side" views without refetching
predictions.

## Endpoints

| Method | Path                 | Purpose                                     |
| ------ | -------------------- | ------------------------------------------- |
| GET    | `/health`            | Self status + whether `ml-api` is reachable |
| POST   | `/estimate`          | Submit features → stored estimate + price   |
| GET    | `/history`           | Paginated list (`limit`, `offset` query)    |
| GET    | `/history/{id}`      | Single stored estimate                      |
| DELETE | `/history/{id}`      | Delete a single estimate                    |
| DELETE | `/history`           | Clear the whole history                     |

Interactive docs: `http://localhost:8001/docs`.

## Environment

| Variable              | Default                   | Purpose                      |
| --------------------- | ------------------------- | ---------------------------- |
| `ML_API_URL`          | `http://localhost:8000`   | Base URL of `ml-api`         |
| `ML_API_TIMEOUT`      | `10.0` (seconds)          | httpx request timeout        |
| `ESTIMATOR_DB_PATH`   | `<pkg>/data/history.db`   | SQLite file location         |

In docker-compose the `ML_API_URL` resolves to `http://ml-api:8000` via
Docker's service DNS.

## Run locally (alongside a running ml-api)

```bash
cd backend/estimator-api
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Point at a locally running ml-api on :8000
ML_API_URL=http://localhost:8000 uvicorn app.main:app --reload --port 8001
```

## Run tests

```bash
pytest -q
```

Tests use a `FakeMLClient` fixture — `ml-api` does **not** need to be running.

## Via docker compose (from repo root)

```bash
docker compose up -d --build ml-api estimator-api
curl -s http://localhost:8001/health
```

## Design notes

- **Why a separate backend at all?** The brief asked for a Python backend
  distinct from the ML service, so features like validation, history, and
  future authentication/audit can evolve without touching the model container.
- **Why SQLite + sync sqlite3?** Zero-config and the database is a single
  inspectable file. Synchronous code is shorter and easier to reason about at
  this scale than an async SQL driver.
- **Why a mirrored `HousingFeatures` Pydantic model?** It lets this service
  enforce its own request shape and return clean 422s before any network call
  to `ml-api`, and lets the two services evolve independently.
- **Error propagation:** `ml-api` 422/503/5xx become the same status at this
  layer; network failures become 502. Callers see a consistent surface.
