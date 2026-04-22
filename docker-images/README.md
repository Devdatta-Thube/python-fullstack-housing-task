# `docker-images/` — pre-built Docker images

The ML API is published as a pre-built Docker image so a reviewer can
run it without cloning the repo or rebuilding from source. Two
distribution channels are provided; pick whichever your environment
allows.

## Option A — GitHub Container Registry (recommended)

The image is hosted on **GHCR** (GitHub's container registry). If your
machine can reach `ghcr.io`, this is the simplest path — one command
to download, one command to run:

```bash
docker pull ghcr.io/devdatta-thube/housing-ml-api:1.0.0
docker run --rm -p 8000:8000 ghcr.io/devdatta-thube/housing-ml-api:1.0.0
```

Then open <http://localhost:8000/docs> — that is the interactive
Swagger UI where you can try predictions.

Image page:
<https://github.com/Devdatta-Thube/python-fullstack-housing-task/pkgs/container/housing-ml-api>

Available tags:
- `1.0.0` — pinned to the v1.0.0 Release.
- `latest` — tracks the most recent build.

## Option B — Offline tarball from a GitHub Release

If `ghcr.io` is blocked or you want an air-gapped copy, download the
image as a `.tar.gz` from the v1.0.0 Release:

<https://github.com/Devdatta-Thube/python-fullstack-housing-task/releases/tag/v1.0.0>

Look for `housing-ml-api.tar.gz` (~154 MB). Then:

```bash
docker load -i housing-ml-api.tar.gz
docker run --rm -p 8000:8000 housing-ml-api:latest
```

## What is and is not in this folder

This folder itself ships no binaries. It is the documented drop-point
for a local `.tar.gz` copy if you choose to keep one alongside the
code; `.gitignore` excludes `*.tar` / `*.tar.gz` from version control
because binary blobs do not belong in git.

If you want to regenerate the tarball locally:

```bash
docker compose build ml-api
docker save housing-ml-api:latest | gzip > docker-images/housing-ml-api.tar.gz
```

## How this fits with the rest of the project

```
   Option A: docker pull from GHCR
   Option B: docker load from the Release tarball
                         │
                         ▼
   housing-ml-api:latest (or 1.0.0) image in your local Docker
                         │ docker run -p 8000:8000 ...
                         ▼
   ml-api running at http://localhost:8000
     └─ Swagger UI:    http://localhost:8000/docs
     └─ Health check:  http://localhost:8000/health
```

If you want the full website experience (estimator form + market
dashboard), run `docker compose up --build -d` from the repo root
instead — that spins up all four services and wires them together
automatically.
