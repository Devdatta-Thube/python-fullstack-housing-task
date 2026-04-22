import sqlite3
from typing import Iterator

from fastapi import Request

from app.db import connection
from app.ml_client import MLClient


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    with connection(request.app.state.db_path) as conn:
        yield conn


def get_ml_client(request: Request) -> MLClient:
    return request.app.state.ml_client
