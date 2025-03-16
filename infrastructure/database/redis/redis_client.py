import asyncio
import redis.asyncio as redis
from typing import Optional

from core.config import settings
from core.logger import logger
from core.exceptions import DatabaseException


class RedisClient:
    """Redis client singleton"""
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_instance(cls) -> redis.Redis:
        """Get or create Redis client instance"""
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                raise DatabaseException(f"Redis connection failed: {str(e)}")
        
        return cls._instance
    
    @classmethod
    async def close(cls) -> None:
        """Close Redis connection if open"""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
            logger.info("Redis connection closed")


def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    return RedisClient.get_instance()