"""
URL Normalizer
Chuẩn hóa và làm sạch URLs
"""

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re
from loguru import logger


class URLNormalizer:
    """Chuẩn hóa URLs"""
    
    def __init__(self):
        # Danh sách query parameters cần loại bỏ
        self.unwanted_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid',
            'ref', 'source', 'campaign',
            '_ga', '_gid'
        ]
    
    def normalize(self, url: str) -> str:
        """
        Chuẩn hóa URL
        
        Args:
            url: Raw URL
            
        Returns:
            Normalized URL
        """
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Remove unwanted query parameters
            query_params = parse_qs(parsed.query)
            cleaned_params = {
                k: v for k, v in query_params.items()
                if k not in self.unwanted_params
            }
            
            # Rebuild query string
            new_query = urlencode(cleaned_params, doseq=True)
            
            # Remove fragment
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                ''  # Remove fragment
            ))
            
            # Remove trailing slash
            if normalized.endswith('/') and normalized.count('/') > 3:
                normalized = normalized[:-1]
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return url
    
    def is_article_url(self, url: str, domain: str) -> bool:
        """
        Kiểm tra xem URL có phải là bài viết không
        
        Args:
            url: URL cần kiểm tra
            domain: Domain của trang báo
            
        Returns:
            True nếu là bài viết, False nếu không
        """
        # Danh sách path patterns không phải bài viết
        excluded_patterns = [
            r'/tag/',
            r'/category/',
            r'/search',
            r'/login',
            r'/register',
            r'/comment',
            r'/page/\d+',
            r'/\d{4}/$',  # Chỉ có năm
            r'/\d{4}/\d{2}/$',  # Chỉ có năm/tháng
        ]
        
        parsed = urlparse(url)
        
        # Check domain
        if domain not in parsed.netloc:
            return False
        
        # Check excluded patterns
        for pattern in excluded_patterns:
            if re.search(pattern, parsed.path):
                return False
        
        # Article URL thường có format: /category/article-slug-123456.html
        # hoặc /article-slug-123456.html
        if re.search(r'-\d+\.html?$', parsed.path):
            return True
        
        # Hoặc có ID trong path
        if re.search(r'/\d{6,}', parsed.path):
            return True
        
        return True  # Default: coi như là article
