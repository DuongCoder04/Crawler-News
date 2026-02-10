"""
Base Crawler Class
Cung cấp các chức năng cơ bản cho tất cả crawler
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from utils.rate_limiter import RateLimiter
from utils.robots_checker import RobotsChecker
from utils.url_normalizer import URLNormalizer
from utils.content_cleaner import ContentCleaner
from config import settings


class BaseCrawler(ABC):
    """Base class cho tất cả crawler"""
    
    def __init__(self, config: Dict, db_client):
        """
        Args:
            config: Domain configuration từ JSON
            db_client: Database client instance
        """
        self.config = config
        self.db_client = db_client
        self.domain = config['domain']
        self.name = config['name']
        
        # Initialize utilities
        self.rate_limiter = RateLimiter(
            requests_per_minute=config['rate_limit']['requests_per_minute']
        )
        self.robots_checker = RobotsChecker(self.domain)
        self.url_normalizer = URLNormalizer()
        self.content_cleaner = ContentCleaner()
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.CRAWLER_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Statistics tracking
        self.stats = {
            'new': 0,
            'duplicate': 0,
            'total': 0,
            'failed': 0
        }
        
        logger.info(f"Initialized {self.name} crawler")
    
    def fetch_page(self, url: str, retries: int = None) -> Optional[str]:
        """
        Fetch HTML content từ URL với retry logic
        
        Args:
            url: URL cần fetch
            retries: Số lần retry
            
        Returns:
            HTML content hoặc None nếu fail
        """
        if retries is None:
            retries = settings.CRAWLER_MAX_RETRIES
            
        # Check robots.txt
        if not self.robots_checker.can_fetch(url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        for attempt in range(retries):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.get(url, timeout=settings.CRAWLER_TIMEOUT)
                response.raise_for_status()
                
                logger.success(f"Successfully fetched: {url}")
                return response.text
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.error(f"403 Forbidden: {url}")
                    return None
                elif e.response.status_code == 404:
                    logger.warning(f"404 Not Found: {url}")
                    return None
                else:
                    logger.error(f"HTTP Error {e.response.status_code}: {url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout: {url}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
            
            # Delay before retry
            if attempt < retries - 1:
                delay = settings.CRAWLER_RETRY_DELAY
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        logger.error(f"Failed to fetch after {retries} attempts: {url}")
        return None
    
    @abstractmethod
    def extract_article_links(self, html: str, base_url: str) -> List[str]:
        """
        Trích xuất danh sách link bài viết từ trang danh sách
        
        Args:
            html: HTML content
            base_url: Base URL để resolve relative links
            
        Returns:
            List of article URLs
        """
        pass
    
    @abstractmethod
    def extract_article_data(self, html: str, url: str) -> Optional[Dict]:
        """
        Trích xuất dữ liệu từ trang chi tiết bài viết
        
        Args:
            html: HTML content
            url: Article URL
            
        Returns:
            Dictionary chứa dữ liệu bài viết hoặc None
        """
        pass
    
    def crawl_list_page(self, category: str) -> List[str]:
        """
        Crawl trang danh sách để lấy links bài viết
        
        Args:
            category: Category slug (e.g., 'thoi-su')
            
        Returns:
            List of article URLs
        """
        url_pattern = self.config['list_page']['url_pattern']
        list_url = url_pattern.format(category=category)
        
        logger.info(f"Crawling list page: {list_url}")
        
        html = self.fetch_page(list_url)
        if not html:
            return []
        
        article_links = self.extract_article_links(html, list_url)
        
        # Normalize URLs
        normalized_links = [
            self.url_normalizer.normalize(link) 
            for link in article_links
        ]
        
        # Limit articles per category
        max_articles = settings.MAX_ARTICLES_PER_CATEGORY
        if len(normalized_links) > max_articles:
            logger.info(f"Limiting to {max_articles} articles (found {len(normalized_links)})")
            normalized_links = normalized_links[:max_articles]
        
        logger.info(f"Found {len(normalized_links)} articles in {category}")
        return normalized_links
    
    def crawl_article(self, url: str) -> Optional[Dict]:
        """
        Crawl chi tiết một bài viết
        
        Args:
            url: Article URL
            
        Returns:
            Article data dictionary hoặc None
        """
        logger.info(f"Crawling article: {url}")
        
        html = self.fetch_page(url)
        if not html:
            return None
        
        article_data = self.extract_article_data(html, url)
        
        if article_data:
            # Clean content
            article_data['content'] = self.content_cleaner.clean(
                article_data['content']
            )
            
            # Add metadata
            article_data['source_url'] = url
            article_data['source_name'] = self.name
            
            logger.success(f"Successfully extracted: {article_data['title'][:50]}...")
        
        return article_data
    
    def run(self, categories: Optional[List[str]] = None):
        """
        Chạy crawler cho các categories
        
        Args:
            categories: List of category slugs, None = all categories
        """
        from utils.console import Console
        
        if not self.config.get('enabled', True):
            logger.warning(f"{self.name} crawler is disabled")
            return
        
        logger.info(f"Starting {self.name} crawler")
        
        # Reset stats
        self.stats = {
            'new': 0,
            'duplicate': 0,
            'total': 0,
            'failed': 0
        }
        
        # Get categories to crawl
        if categories is None:
            categories = list(self.config['category_mapping'].keys())
        
        for category in categories:
            logger.info(f"Processing category: {category}")
            
            # Get article links
            article_links = self.crawl_list_page(category)
            
            for link in article_links:
                self.stats['total'] += 1
                
                # Crawl article
                article_data = self.crawl_article(link)
                
                if not article_data:
                    self.stats['failed'] += 1
                    continue
                
                # Map category
                xwise_category = self.config['category_mapping'].get(category)
                article_data['category_code'] = xwise_category
                
                # Check if duplicate before pushing
                source_url = article_data.get('source_url')
                if source_url and self.db_client.check_duplicate(source_url):
                    self.stats['duplicate'] += 1
                    Console.article(article_data['title'], status="duplicate")
                    continue
                
                # Push to database
                success = self.db_client.create_news(article_data)
                
                if success:
                    self.stats['new'] += 1
                    Console.article(article_data['title'], status="new")
                else:
                    self.stats['failed'] += 1
        
        logger.info(
            f"{self.name} crawler finished: "
            f"{self.stats['new']} new, {self.stats['duplicate']} duplicates, "
            f"{self.stats['failed']} failed out of {self.stats['total']} total"
        )
