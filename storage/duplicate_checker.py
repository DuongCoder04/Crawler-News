"""
Duplicate Checker
Kiểm tra bài viết đã được crawl chưa
"""

from storage.cache import RedisCache
from loguru import logger
import hashlib
from config import settings


class DuplicateChecker:
    """Kiểm tra duplicate articles"""
    
    def __init__(self):
        self.cache = RedisCache()
        self.prefix = "crawler:article:"
        self.ttl = settings.CACHE_TTL  # 90 days default
    
    def _get_key(self, url: str) -> str:
        """Generate cache key từ URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{self.prefix}{url_hash}"
    
    def is_crawled(self, url: str) -> bool:
        """
        Kiểm tra URL đã được crawl chưa
        
        Args:
            url: Article URL
            
        Returns:
            True nếu đã crawl, False nếu chưa
        """
        key = self._get_key(url)
        return self.cache.exists(key)
    
    def mark_crawled(self, url: str, article_id: str = None):
        """
        Đánh dấu URL đã được crawl
        
        Args:
            url: Article URL
            article_id: X-Wise news ID (optional)
        """
        key = self._get_key(url)
        value = article_id or "crawled"
        self.cache.set(key, value, expire=self.ttl)
        logger.debug(f"Marked as crawled: {url}")
    
    def get_article_id(self, url: str) -> str:
        """
        Lấy article ID từ cache
        
        Args:
            url: Article URL
            
        Returns:
            Article ID hoặc None
        """
        key = self._get_key(url)
        return self.cache.get(key)
