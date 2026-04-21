# Data ingestion

The housing dataset used to train the model and drive the market-insights
service is **not** included in this repository. It is proprietary to the
organisation that issued this task and must be supplied locally before the
stack can be built or run.

This document explains where the data is expected, what shape it must have,
and how each service consumes it.

---

## 1. What you need

A CSV file containing the 50 training records, one row per property, with
a header row and the columns listed in §3. This is the file that was
distributed with the task brief; in this repository it is referred to
generically as **`housing.csv`**.

If you are running this project for the first time and do not have this
file, you cannot proceed past this page — the build will halt at the
`COPY data` step of the `ml-api` and `market-api` Dockerfiles.

## 2. Where to place it

Two copies are required, one per service that needs the data:

```
ml-api/data/housing.csv          ← training input for the model
market-api/data/housing.csv      ← aggregates and dataset browser
```

Both paths are **already listed in `.gitignore`**. A file placed here will
not be tracked by version control and will not end up in any commit.

The simplest way to put the file in both places at once:

```bash
# from the repository root
mkdir -p ml-api/data market-api/data
cp /path/to/your/housing.csv ml-api/data/housing.csv
cp /path/to/your/housing.csv market-api/data/housing.csv
```

On Windows with WSL, you can copy a file from a Windows path like so:

```bash
cp /mnt/c/Users/you/Downloads/housing.csv ml-api/data/housing.csv
cp /mnt/c/Users/you/Downloads/housing.csv market-api/data/housing.csv
```

## 3. Expected schema

The first row of the CSV must be a header. Column names are matched
case-sensitively. Order within the row does not matter — the loader
reads by column name — but the *model's* `FEATURE_COLUMNS` order defined
in `ml-api/app/model.py` is what determines the order of coefficients
in `/model-info`.

| Column                      | Type  | Notes                                |
|-----------------------------|-------|--------------------------------------|
| `square_footage`            | int   | Interior area, square feet           |
| `bedrooms`                  | int   | Non-negative                         |
| `bathrooms`                 | float | Non-negative, half-baths allowed     |
| `year_built`                | int   | Four-digit calendar year             |
| `lot_size`                  | int   | Lot area, square feet                |
| `distance_to_city_center`   | float | Kilometres                           |
| `school_rating`             | float | Usually 1–10                         |
| `price`                     | int   | Target variable (INR). Only required in the training CSV; the live `/predict` request does **not** include it. |

A UTF-8 BOM on the first column is tolerated — both loaders strip it when
reading the header.

## 4. How each service consumes the data

### `ml-api`

- **Build time.** The Dockerfile copies `ml-api/data/housing.csv` into the
  image and runs `python train.py`. That script:
  1. Loads the CSV with pandas.
  2. Fits a `LinearRegression` on the seven feature columns against
     `price`.
  3. Writes `artifacts/model.pkl` and `artifacts/metadata.json`
     (training timestamp, metrics, feature columns).
- **Runtime.** The service only reads the `artifacts/` directory. The raw
  CSV is not needed at runtime and is not re-read.
- **Local (non-Docker) workflow:** run `python train.py` manually whenever
  you change the dataset; the FastAPI app picks up the new `.pkl` on
  startup.

### `market-api`

- **Runtime only.** Django loads `market-api/data/housing.csv` into
  `LocMemCache` the first time any endpoint that needs it is called
  (`/api/stats/`, `/api/rows/`, `/api/export/*`). Subsequent requests hit
  the cache (TTL controlled by `AGGREGATE_CACHE_TTL`, default 300 s).
- **Schema:** same as above; the `price` column *is* required here
  because stats and histograms are computed over it.
- **Override:** set the `DATASET_PATH` environment variable to point at
  an alternate CSV path for local experimentation.

### `estimator-api`

- Does **not** read the dataset directly. It forwards prediction requests
  to `ml-api` and stores the submitted features + returned price in its
  own SQLite history.

### `portal`

- Also does not read the dataset. It is a browser of the two backends.

## 5. A different dataset

The stack is not hard-wired to any particular dataset — only to the schema
in §3. If you want to retrain against a different CSV:

1. Replace both `ml-api/data/housing.csv` and `market-api/data/housing.csv`.
2. Rebuild the affected services:

   ```bash
   docker compose build ml-api market-api
   docker compose up -d ml-api market-api
   ```

3. Visit `GET /model-info` on the rebuilt `ml-api` to confirm the new
   training timestamp and metrics.

If your new CSV adds or renames columns, you must also update
`FEATURE_COLUMNS` in `ml-api/app/model.py`, the Pydantic model in
`ml-api/app/schemas.py`, the mirrored model in
`estimator-api/app/schemas.py`, the DRF serializer in
`market-api/market/serializers.py`, and the zod schema in
`portal/lib/schemas.ts`. Keep the order identical across all five.

## 6. What `.gitignore` excludes

To keep confidential source material out of version control, the following
patterns are excluded at the repository root:

```
/Interview Tasks Fullstack.pdf
/House Price Dataset.csv
/Test Data For Prediction.csv
ml-api/data/*.csv
market-api/data/*.csv
```

If you later need to verify that nothing confidential has slipped in, run:

```bash
git status --short --untracked-files=all | \
  grep -E 'CLAUDE|House Price|Test Data|Interview|data/housing' || echo OK
```

A clean `OK` means the data is safely out of the tree.
