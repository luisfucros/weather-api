from backend.config import settings
from datetime import timedelta
import logging
import redis
import json


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

redis_client = redis.Redis.from_url(url=settings.redis_url, decode_responses=True)
CACHE_TTL = timedelta(minutes=10)


def get_cached_data(key: str) -> dict[str, any]:
    cached_data = redis_client.get(key)
    logging.info(f"Cache hit for key: {key}")
    return cached_data

def insert_data(key: str, data: dict[str, any]) -> None:
    redis_client.setex(key, CACHE_TTL, json.dumps(data))
    logging.info(f"Caching data for key: {key}")