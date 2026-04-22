# `docker-images/` — pre-built Docker images

This folder is the drop-point for **pre-built Docker images** saved as
`.tar` files. The interview deliverable for Task 1 is the ML API image;
it is the one you will typically find here.

## Why this folder exists

Docker images are usually pulled from a registry (Docker Hub, GHCR,
etc.). For this interview the image is shared as a file so the
reviewer does not need a registry account: they just **load** the file
into their own Docker and run it.

## What is expected inside

| File name                | What it is                                     | Size (approx) |
|--------------------------|------------------------------------------------|---------------|
| `housing-ml-api.tar.gz`  | The `ml-api` image (FastAPI + scikit-learn)    | ~150 MB       |

The file is large (binary), so it is **not committed to git** — it is
transferred separately (attached to the delivery email, or downloaded
from the link in that email). See the `.gitignore` at the repo root.

If this folder is empty when you clone the repo, that is expected. You
can either:

- Run the stack from source with `docker compose up --build` from the
  repo root (recommended — it builds the image locally), **or**
- Load the `.tar.gz` that was shared with you, then run it (instructions
  below).

## Running the pre-built image

Assuming you have `housing-ml-api.tar.gz` in this folder:

```bash
# 1. Load the image into your local Docker
docker load -i docker-images/housing-ml-api.tar.gz

# 2. Confirm it's there
docker images | grep housing-ml-api

# 3. Run it on port 8000
docker run --rm -p 8000:8000 housing-ml-api:latest
```

Then open <http://localhost:8000/docs> — that is the interactive API
explorer (Swagger UI). You can try predictions from there without
needing the rest of the stack.

The image already contains the trained model — no further setup needed.

## How it fits with the rest of the project

```
docker-images/housing-ml-api.tar.gz
     │ docker load
     ▼
housing-ml-api:latest  (image in your local Docker)
     │ docker run
     ▼
Running ml-api on port 8000  ◄─── Swagger UI  (http://localhost:8000/docs)
                               ◄─── Also reachable from estimator-api
                                    and market-api if you bring those up
                                    separately.
```

If you want the full website experience (estimator form + market
dashboard), run `docker compose up --build -d` from the repo root
instead — that spins up all four services and wires them together
automatically.

## Saving a new image (for the submitter)

If you change `ml-api` and need to ship a new tarball:

```bash
docker compose build ml-api
docker save housing-ml-api:latest | gzip > docker-images/housing-ml-api.tar.gz
```
