from logging import basicConfig

from fastapi import FastAPI

from .database import lifespan_check

from .api import api_router
from .exception_logger import custom_exception_handler

basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Holdmybeer API",
    description="Welcome to Holdmybeer API documentation!",
    lifespan=lifespan_check
)
app.include_router(api_router, prefix="/api")
app.add_exception_handler(Exception, custom_exception_handler)
