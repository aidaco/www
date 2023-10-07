import time

import aiosqlite
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import config

db: aiosqlite.Connection


async def opendb():
    global db
    db = await aiosqlite.connect(config.locations.database)
    await db.execute(
        """CREATE TABLE IF NOT EXISTS requests(
         count INTEGER PRIMARY KEY AUTOINCREMENT,
         received_ts_ns INTEGER,
         elapsed_ns INTEGER,
         method TEXT,
         url TEXT,
         headers TEXT,
         query_params TEXT,
         path_params TEXT,
         client TEXT,
         cookies TEXT
    );"""
    )


async def closedb():
    global db
    await db.close()
    del db


async def _insert(request, received, elapsed):
    await db.execute(
        "INSERT INTO requests("
        "received_ts_ns,"
        "elapsed_ns,"
        "method,"
        "url,"
        "headers,"
        "query_params,"
        "path_params,"
        "client,"
        "cookies"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        (
            received,
            elapsed,
            str(request.method),
            str(request.url),
            str(request.headers),
            str(request.query_params),
            str(request.path_params),
            str(request.client),
            str(request.cookies),
        ),
    )
    await db.commit()


class LogRequests(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        received = time.time_ns()
        response = await call_next(request)
        elapsed = time.time_ns() - received
        await _insert(request, received, elapsed)
        return response
