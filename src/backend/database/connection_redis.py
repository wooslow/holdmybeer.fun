import os
import logging

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
logger = logging.getLogger(__name__)

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not set in environment variables.")

redis: Redis = Redis.from_url(REDIS_URL, decode_responses=True)


async def check_redis_connection():
    try:
        pong = await redis.ping()

        if pong:
            logger.info("✅ Successfully connected to Redis")
        else:
            raise RuntimeError("Redis ping failed")
    except Exception:
        logger.exception("❌ Failed to connect to Redis")
