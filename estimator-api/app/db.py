from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS estimate_history (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    label TEXT,
    square_footage REAL NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms REAL NOT NULL,
    year_built INTEGER NOT NULL,
    lot_size REAL NOT NULL,
    distance_to_city_center REAL NOT NULL,
    school_rating REAL NOT NULL,
    predicted_price REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_history_created_at
    ON estimate_history(created_at DESC);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _row_to_record(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "created_at": datetime.fromisoformat(row["created_at"]),
        "label": row["label"],
        "features": {
            "square_footage": row["square_footage"],
            "bedrooms": row["bedrooms"],
            "bathrooms": row["bathrooms"],
            "year_built": row["year_built"],
            "lot_size": row["lot_size"],
            "distance_to_city_center": row["distance_to_city_center"],
            "school_rating": row["school_rating"],
        },
        "predicted_price": row["predicted_price"],
    }


def insert_estimate(
    conn: sqlite3.Connection,
    features: dict,
    label: str | None,
    predicted_price: float,
) -> dict:
    record_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO estimate_history (
            id, created_at, label,
            square_footage, bedrooms, bathrooms, year_built,
            lot_size, distance_to_city_center, school_rating,
            predicted_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            created_at,
            label,
            features["square_footage"],
            features["bedrooms"],
            features["bathrooms"],
            features["year_built"],
            features["lot_size"],
            features["distance_to_city_center"],
            features["school_rating"],
            predicted_price,
        ),
    )
    return {
        "id": record_id,
        "created_at": datetime.fromisoformat(created_at),
        "label": label,
        "features": features,
        "predicted_price": predicted_price,
    }


def list_estimates(
    conn: sqlite3.Connection, limit: int = 50, offset: int = 0
) -> tuple[list[dict], int]:
    cursor = conn.execute(
        "SELECT * FROM estimate_history ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    items = [_row_to_record(r) for r in cursor.fetchall()]
    total = conn.execute("SELECT COUNT(*) AS n FROM estimate_history").fetchone()["n"]
    return items, total


def get_estimate(conn: sqlite3.Connection, record_id: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM estimate_history WHERE id = ?", (record_id,)
    ).fetchone()
    return _row_to_record(row) if row else None


def delete_estimate(conn: sqlite3.Connection, record_id: str) -> bool:
    cursor = conn.execute(
        "DELETE FROM estimate_history WHERE id = ?", (record_id,)
    )
    return cursor.rowcount > 0


def clear_estimates(conn: sqlite3.Connection) -> int:
    cursor = conn.execute("DELETE FROM estimate_history")
    return cursor.rowcount
