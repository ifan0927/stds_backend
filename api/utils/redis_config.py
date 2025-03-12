import redis
import os
import json
import logging
from typing import Any, Optional

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

DEFAULT_CACHE_TTL = 3600  # 1小時

# 建立Redis連接池
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,  # 自動將byte轉為字串
    )
    logging.info(f"Redis connection established to {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logging.error(f"Failed to connect to Redis: {e}")
    redis_client = None


def get_cache(key: str) -> Optional[Any]:
    """從Redis獲取快取資料，並自動反序列化JSON"""
    if redis_client is None:
        return None

    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logging.error(f"Error getting data from Redis cache: {e}")
        return None


def set_cache(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL) -> bool:
    """將資料存入Redis並序列化為JSON，設定過期時間"""
    if redis_client is None:
        return False

    try:
        serialized_value = json.dumps(value)
        redis_client.set(key, serialized_value, ex=ttl)
        return True
    except Exception as e:
        logging.error(f"Error setting data to Redis cache: {e}")
        return False


def delete_cache(key: str) -> bool:
    """刪除Redis中的快取"""
    if redis_client is None:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logging.error(f"Error deleting data from Redis cache: {e}")
        return False


def delete_pattern(pattern: str) -> bool:
    """刪除符合模式的所有快取"""
    if redis_client is None:
        return False

    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        logging.error(f"Error deleting pattern from Redis cache: {e}")
        return False