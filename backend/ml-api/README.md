# ml-api — Housing Price Prediction API

FastAPI + scikit-learn service that predicts house prices from seven features.
Used by both Task-2 backends (`estimator-api`, `market-api`) as the single ML
source of truth.

## Endpoints

| Method | Path              | Purpose                                    |
| ------ | ----------------- | ------------------------------------------ |
| GET    | `/health`         | Liveness + whether the model is loaded     |
| GET    | `/model-info`     | Coefficients, intercept, training metrics  |
| POST   | `/predict`        | Single-property price prediction           |
| POST   | `/predict/batch`  | Batch prediction (`{"items": [...]}`)      |

Interactive docs: `http://localhost:8000/docs` (Swagger) and `/redoc`.

## Run locally

```bash
cd backend/ml-api
python -m venv .venv && source .venv/bin/activate    # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train.py                 # produces artifacts/model.pkl + metadata.json
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

## Run tests

```bash
pytest -q
```

`conftest.py` auto-trains the model the first time tests run.

## Run via Docker

```bash
docker build -t housing-ml-api .
docker run --rm -p 8000:8000 housing-ml-api
```

The image trains the model during `docker build`, so `docker run` serves
immediately.

## Model

- Algorithm: `sklearn.linear_model.LinearRegression`
- Training data: `data/housing.csv` (50 rows, 7 features → `price`)
- Metrics: training R², MAE, RMSE, plus 5-fold CV R² mean/std.
- Chosen for interpretability — `/model-info` exposes per-feature coefficients
  so any client can introspect how the model reasons.
