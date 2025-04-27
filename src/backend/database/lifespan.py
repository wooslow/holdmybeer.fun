from contextlib import asynccontextmanager

from fastapi import FastAPI

from .connection_postgres import check_db_connection, engine
from .connection_redis import check_redis_connection


@asynccontextmanager
async def lifespan_check(app: FastAPI):
    await check_db_connection()
    await check_redis_connection()
    yield
    await engine.dispose()
