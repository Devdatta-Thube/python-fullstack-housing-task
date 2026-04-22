# `backend/` — the three server-side services

This folder holds the three services that answer questions for the
website. They are the "engine room" of the project. The website in
`frontend/` does not know anything about prediction — it just asks
these services and shows what comes back.

## The three services

| Sub-folder       | What it is                       | Port  | Its job in plain words                                              |
|------------------|----------------------------------|-------|---------------------------------------------------------------------|
| `ml-api/`        | FastAPI + scikit-learn           | 8000  | Trains the prediction model once, then answers "how much is it worth?" requests. |
| `estimator-api/` | FastAPI (forwarder)              | 8001  | Takes requests from the website, asks `ml-api` for a price, and remembers every submission in a small database so users can review their history. |
| `market-api/`    | Django + Django REST Framework   | 8002  | Reads the whole training dataset and produces summaries (averages, distributions, tables). Can export the data as CSV or a PDF report. |

Each sub-folder has its own README with technical details. If you only
want to run the whole stack, you don't need to look inside.

## How they combine

```
  frontend (port 3000)
    │
    ├───► estimator-api (8001) ──► ml-api (8000)
    │        └── stores submission in its own SQLite DB
    │
    └───► market-api   (8002) ──► ml-api (8000)  (only for "what-if")
             └── loads the CSV into memory for stats and exports
```

Key point: **only `ml-api` owns the machine-learning model**. The other
two services are HTTP clients — they call `ml-api` over the network.
This means the model lives in exactly one place, which makes retraining
predictable.

## Running the backends alone (for API work)

You rarely need this — `docker compose up --build` at the repo root
runs everything. If you want to develop one service on its own, each
sub-folder documents a Python + pip workflow. In short:

```bash
# From backend/<service>/
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
# then follow the per-service README for the run command
```

Python 3.12 in WSL Ubuntu is recommended on Windows; the services are
tested against that combination.

## Why two different backend frameworks?

The interview brief asks for two applications in **different**
frameworks. To keep the whole stack in one language (Python) while
still contrasting two styles, this repo uses:

- **FastAPI** for `estimator-api` — lightweight, async-ready, generates
  an OpenAPI schema automatically.
- **Django + DRF** for `market-api` — batteries-included, with built-in
  admin, settings, middleware, and the DRF view layer.

Both deliver the same kind of outcome (a REST API), but show two
distinct flavours of Python backend development.

## Where the dataset goes

The training CSV is not shipped with this repo. Two of the three
services need a copy:

- `backend/ml-api/data/housing.csv` — the training input baked into the image.
- `backend/market-api/data/housing.csv` — the runtime source for stats.

See [`../DATA.md`](../DATA.md) for the exact steps.

## Health checks

When everything is running, each service has a simple health URL:

```
http://localhost:8000/health          (ml-api)
http://localhost:8001/health          (estimator-api)
http://localhost:8002/api/health/     (market-api)
```

A `200 OK` response means the service is alive.
