import os
from typing import AsyncGenerator, Annotated

from dotenv import load_dotenv
from logging import getLogger
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
logger = getLogger(__name__)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set.")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def check_db_connection() -> None:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Successfully connected to database")
    except Exception:
        logger.exception("❌ Failed to connect to database")


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
