# `keys/` — configuration reference

This folder is a **reference sheet** for every setting (environment
variable) the services read when they start. It is not a vault of
secrets: **this project has no API keys, passwords, or tokens** — the
services do not call any paid service, store personal data, or talk to
an external database.

The folder is named `keys/` because that is the conventional label for
"settings the services need". The more accurate name would be
*environment variables* or *configuration* — if you have worked with
`.env` files before, this is the same idea.

## What is shipped

- `.env.example` — a commented example of every variable each service
  reads, with the default value in brackets. Copy it to `.env` if you
  want to override anything; nothing is *required* to be set (all
  values have working defaults).

## What each variable does (plain English)

### ml-api (port 8000)
| Variable          | Used for                                    | Default           |
|-------------------|---------------------------------------------|-------------------|
| `ML_HOST`         | Bind address inside the container.          | `0.0.0.0`         |
| `ML_PORT`         | Port inside the container.                  | `8000`            |

### estimator-api (port 8001)
| Variable          | Used for                                                    | Default                |
|-------------------|-------------------------------------------------------------|------------------------|
| `ML_API_URL`      | Where to reach the ML service.                              | `http://ml-api:8000`   |
| `HISTORY_DB_PATH` | File path for the SQLite database of past submissions.      | `/app/data/history.db` |

### market-api (port 8002)
| Variable                | Used for                                                             | Default                    |
|-------------------------|----------------------------------------------------------------------|----------------------------|
| `ML_API_URL`            | Where to reach the ML service for what-if predictions.               | `http://ml-api:8000`       |
| `DATASET_PATH`          | CSV file the stats and tables are computed from.                     | `/app/data/housing.csv`    |
| `AGGREGATE_CACHE_TTL`   | How long (seconds) to cache computed summaries before recomputing.   | `300`                      |
| `DJANGO_DEBUG`          | Turns on Django's debug mode. Always `0` in production.              | `0`                        |
| `DJANGO_ALLOWED_HOSTS`  | Comma-separated list of hostnames the service will accept.           | `market-api,localhost,127.0.0.1` |
| `DJANGO_SECRET_KEY`     | A random string Django uses for signing sessions / cookies.          | A built-in insecure value — set your own if you care. |

### portal / frontend (port 3000)
| Variable                          | Used for                                                      | Default                  |
|-----------------------------------|---------------------------------------------------------------|--------------------------|
| `NEXT_PUBLIC_ESTIMATOR_API_URL`   | Where the browser should call the estimator API.              | `http://localhost:8001`  |
| `NEXT_PUBLIC_MARKET_API_URL`      | Where the browser should call the market API.                 | `http://localhost:8002`  |

Because these two are rendered into the browser bundle at build time,
they must be URLs your browser can reach — not Docker-internal names.

## How to override a setting

Either:

1. Edit `docker-compose.yml` under the service's `environment:` block
   and re-run `docker compose up -d --build`, or
2. Create a `.env` file in the repository root (same folder as
   `docker-compose.yml`) and list the variables there. Docker Compose
   picks it up automatically.

## Is there anything secret here?

No. Nothing in this folder, or anywhere in the repo, should be treated
as a secret. If you ever add a real secret later (e.g. an external API
key), put it in your private `.env` file and make sure the `.env` line
in `.gitignore` stays intact.
