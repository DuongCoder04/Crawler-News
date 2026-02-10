"""
Redis Cache
Cache để tránh crawl duplicate và lưu trữ tạm
"""

import redis
from typing import Optional
from loguru import logger
import json
from config import settings


class RedisCache:
    """Redis cache wrapper"""
    
    def __init__(self):
        if not settings.REDIS_ENABLED:
            logger.warning("Redis is disabled")
            self.client = None
            return
            
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True
            )
            self.client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            self.client = None
    
    def set(self, key: str, value: str, expire: int = None):
        """Set cache value"""
        if not self.client:
            return
        
        try:
            self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def get(self, key: str) -> Optional[str]:
        """Get cache value"""
        if not self.client:
            return None
        
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key"""
        if not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def set_json(self, key: str, value: dict, expire: int = None):
        """Set JSON value"""
        self.set(key, json.dumps(value), expire)
    
    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
