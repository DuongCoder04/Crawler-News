"""
Robots.txt Checker
Kiểm tra robots.txt trước khi crawl
"""

from urllib.robotparser import RobotFileParser
from loguru import logger


class RobotsChecker:
    """Kiểm tra robots.txt"""
    
    def __init__(self, domain: str):
        """
        Args:
            domain: Domain cần kiểm tra (e.g., 'vnexpress.net')
        """
        self.domain = domain
        self.robots_url = f"https://{domain}/robots.txt"
        self.parser = RobotFileParser()
        self.parser.set_url(self.robots_url)
        
        try:
            self.parser.read()
            logger.info(f"Loaded robots.txt for {domain}")
        except Exception as e:
            logger.warning(f"Could not load robots.txt for {domain}: {e}")
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """
        Kiểm tra xem có được phép crawl URL không
        
        Args:
            url: URL cần kiểm tra
            user_agent: User agent string
            
        Returns:
            True nếu được phép, False nếu bị cấm
        """
        try:
            return self.parser.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {e}")
            return True  # Default: allow if error
    
    def get_crawl_delay(self, user_agent: str = '*') -> float:
        """
        Lấy crawl delay từ robots.txt
        
        Args:
            user_agent: User agent string
            
        Returns:
            Crawl delay in seconds
        """
        try:
            delay = self.parser.crawl_delay(user_agent)
            return float(delay) if delay else 0.0
        except Exception:
            return 0.0
