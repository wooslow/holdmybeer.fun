import os
import logging
from logging import basicConfig

from fastapi import FastAPI
from dotenv import load_dotenv
import sentry_sdk

from .database import lifespan_check
from .api import api_router
from .exception_logger import custom_exception_handler

load_dotenv()

basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=True,
)

app = FastAPI(
    title="Holdmybeer API",
    description="Welcome to Holdmybeer API documentation!",
    lifespan=lifespan_check,
)

app.add_exception_handler(Exception, custom_exception_handler)
app.include_router(api_router, prefix="/api")
