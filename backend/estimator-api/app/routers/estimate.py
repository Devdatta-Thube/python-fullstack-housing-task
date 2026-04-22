import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db import (
    clear_estimates,
    delete_estimate,
    get_estimate,
    insert_estimate,
    list_estimates,
)
from app.dependencies import get_db, get_ml_client
from app.ml_client import MLClient, MLServiceError
from app.schemas import EstimateRequest, EstimateResponse, HistoryListResponse

router = APIRouter(tags=["estimator"])


@router.post(
    "/estimate",
    response_model=EstimateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_estimate(
    body: EstimateRequest,
    conn: sqlite3.Connection = Depends(get_db),
    ml: MLClient = Depends(get_ml_client),
) -> EstimateResponse:
    try:
        price = ml.predict(body.features.model_dump())
    except MLServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    record = insert_estimate(
        conn,
        body.features.model_dump(),
        body.label,
        price,
    )
    return EstimateResponse(**record)


@router.get("/history", response_model=HistoryListResponse)
def list_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db),
) -> HistoryListResponse:
    items, total = list_estimates(conn, limit=limit, offset=offset)
    return HistoryListResponse(
        items=[EstimateResponse(**i) for i in items],
        total=total,
    )


@router.get("/history/{record_id}", response_model=EstimateResponse)
def get_history_item(
    record_id: str,
    conn: sqlite3.Connection = Depends(get_db),
) -> EstimateResponse:
    record = get_estimate(conn, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return EstimateResponse(**record)


@router.delete("/history/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    record_id: str,
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    if not delete_estimate(conn, record_id):
        raise HTTPException(status_code=404, detail="Estimate not found")


@router.delete("/history")
def delete_all_history(conn: sqlite3.Connection = Depends(get_db)) -> dict:
    deleted = clear_estimates(conn)
    return {"deleted": deleted}
