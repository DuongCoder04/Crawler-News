# Hệ Thống Crawler Tin Tức Tự Động cho CMS X-Wise

## 📋 Tổng Quan

Tài liệu này mô tả chi tiết hệ thống crawler tự động thu thập tin tức từ các trang báo tiếng Việt và đẩy vào CMS X-Wise thông qua REST API.

---

## 🎯 Mục Tiêu Hệ Thống

1. **Tự động thu thập** tin tức từ nhiều nguồn báo tiếng Việt (VnExpress, ZingNews, Tuổi Trẻ, Dân Trí, v.v.)
2. **Trích xuất và chuẩn hóa** dữ liệu phù hợp với cấu trúc database CMS X-Wise
3. **Tích hợp API** để tạo tin tức mới, tránh duplicate
4. **Chạy định kỳ** theo lịch cấu hình
5. **Xử lý lỗi** và logging chi tiết

---

## 🏗️ Kiến Trúc Hệ Thống

### 1. Cấu Trúc Database CMS X-Wise (Hiện Tại)

#### Bảng `news`
```sql
CREATE TABLE news (
    id UUID PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    created_at DATE,
    reaction_count INT DEFAULT 0,
    status TEXT,  -- 'ACTIVE' | 'INACTIVE'
    category_code VARCHAR(100)
);
```

**Lưu ý**: Crawler sẽ sử dụng schema hiện có, KHÔNG thêm trường mới. Thông tin nguồn (source_url, source_name) sẽ được:
- Lưu trong Redis cache để check duplicate
- Hoặc embed vào cuối `content` dưới dạng HTML comment nếu cần trace nguồn

#### Bảng `attachment`
```sql
CREATE TABLE attachment (
    id UUID PRIMARY KEY,
    url VARCHAR(255),
    object_type VARCHAR(255),  -- 'news'
    object_id VARCHAR(255),    -- news.id
    created_at DATE,
    status VARCHAR(255),
    file_name VARCHAR(255),
    extension VARCHAR(255)
);
```

#### Bảng `category`
```sql
CREATE TABLE category (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(255),
    parent_code VARCHAR(255),  -- 'NEWS'
    status VARCHAR(255),
    created_at DATE,
    updated_at DATE
);
```

### 2. API Endpoints CMS X-Wise

#### Base URL
```
Development: https://backend-dev-cms-staging.up.railway.app
Production: [TBD]
```

#### Authentication
```http
Authorization: Bearer <JWT_TOKEN>
```

#### Endpoint: Tạo Tin Tức Mới
```http
POST /cms/wise/news
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

Request Body:
{
    "title": "string (1-1000 chars, required)",
    "content": "string (1-50000 chars, required, HTML format)",
    "status": "ACTIVE | INACTIVE (default: ACTIVE)",
    "category_code": "string (max 100 chars, required)",
    "attachments": ["uuid1", "uuid2"]  // Array of attachment IDs
}

Response Success (200):
{
    "data": {
        "id": "uuid",
        "title": "...",
        "content": "...",
        "status": "ACTIVE",
        "category_code": "...",
        "created_at": "2026-02-10",
        "reaction_count": 0,
        "attachments": [...]
    },
    "meta": {
        "message": "News created successfully"
    }
}

Response Error (400/401/500):
{
    "meta": {
        "message": "Error message",
        "error": "Detailed error"
    }
}
```

#### Endpoint: Upload Attachment
```http
POST /cms/wise/attachment/upload
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

Request Body:
- file: File (image/document)

Response Success (200):
{
    "data": {
        "id": "uuid",
        "url": "https://...",
        "file_name": "image.jpg",
        "extension": "jpg",
        "status": "ACTIVE",
        "created_at": "2026-02-10"
    },
    "meta": {
        "message": "Upload successful"
    }
}
```

#### Endpoint: Lấy Danh Sách Categories
```http
GET /cms/wise/categories/by-parent/NEWS
Authorization: Bearer <JWT_TOKEN>

Response Success (200):
{
    "data": [
        {
            "id": "uuid",
            "code": "TECH",
            "name": "Công nghệ",
            "parent_code": "NEWS",
            "status": "ACTIVE"
        },
        ...
    ]
}
```

---

## 🔧 Công Nghệ Sử Dụng

### Stack Chính
- **Python 3.9+**: Ngôn ngữ chính
- **requests / httpx**: HTTP client cho trang tĩnh
- **BeautifulSoup4**: Parse HTML
- **Playwright**: Xử lý trang JavaScript-rendered
- **APScheduler**: Scheduler chạy định kỳ
- **Redis**: Cache và queue (optional)
- **python-dotenv**: Quản lý environment variables
- **loguru**: Logging nâng cao

### Thư Viện Bổ Sung
```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
playwright>=1.40.0
apscheduler>=3.10.0
redis>=5.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
validators>=0.22.0
```

---

## 📁 Cấu Trúc Dự Án

```
news-crawler/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Cấu hình chung
│   └── domains/
│       ├── __init__.py
│       ├── vnexpress.json       # Config VnExpress
│       ├── zingnews.json        # Config ZingNews
│       ├── tuoitre.json         # Config Tuổi Trẻ
│       └── dantri.json          # Config Dân Trí
├── engine/
│   ├── __init__.py
│   ├── base_crawler.py          # Base crawler class
│   ├── static_crawler.py        # Crawler cho trang tĩnh
│   ├── dynamic_crawler.py       # Crawler cho trang JS
│   └── crawlers/
│       ├── __init__.py
│       ├── vnexpress.py         # VnExpress crawler
│       ├── zingnews.py          # ZingNews crawler
│       ├── tuoitre.py           # Tuổi Trẻ crawler
│       └── dantri.py            # Dân Trí crawler
├── utils/
│   ├── __init__.py
│   ├── api_client.py            # X-Wise API client
│   ├── content_cleaner.py       # Làm sạch nội dung
│   ├── url_normalizer.py        # Chuẩn hóa URL
│   ├── rate_limiter.py          # Rate limiting
│   ├── robots_checker.py        # Kiểm tra robots.txt
│   └── logger.py                # Logging setup
├── scheduler/
│   ├── __init__.py
│   ├── job_scheduler.py         # APScheduler setup
│   └── tasks.py                 # Định nghĩa tasks
├── storage/
│   ├── __init__.py
│   ├── cache.py                 # Redis cache
│   └── duplicate_checker.py     # Kiểm tra duplicate
├── tests/
│   ├── __init__.py
│   ├── test_crawlers.py
│   └── test_api_client.py
├── logs/                        # Thư mục logs
├── .env.example                 # Environment template
├── .env                         # Environment variables (gitignore)
├── requirements.txt             # Python dependencies
├── main.py                      # Entry point
└── README.md                    # Hướng dẫn sử dụng
```

---

## ⚙️ Cấu Hình

### 1. Environment Variables (.env)

```bash
# X-Wise API Configuration
XWISE_API_BASE_URL=https://backend-dev-cms-staging.up.railway.app
XWISE_JWT_TOKEN=your_jwt_token_here

# Crawler Configuration
CRAWLER_USER_AGENT=XwiseNewsCrawler/1.0 (+https://x-wise.io; contact@x-wise.io)
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3
CRAWLER_RETRY_DELAY=5

# Rate Limiting (requests per minute)
RATE_LIMIT_VNEXPRESS=30
RATE_LIMIT_ZINGNEWS=30
RATE_LIMIT_TUOITRE=30
RATE_LIMIT_DANTRI=30

# Redis Configuration (Optional)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Scheduler Configuration
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Ho_Chi_Minh

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/crawler.log
LOG_ROTATION=10 MB
LOG_RETENTION=30 days

# Proxy Configuration (Optional)
PROXY_ENABLED=false
PROXY_HTTP=
PROXY_HTTPS=

# Notification (Optional)
SLACK_WEBHOOK_URL=
EMAIL_NOTIFICATION=false
EMAIL_SMTP_HOST=
EMAIL_SMTP_PORT=
EMAIL_FROM=
EMAIL_TO=
```

### 2. Domain Configuration (JSON)

#### config/domains/vnexpress.json
```json
{
    "domain": "vnexpress.net",
    "name": "VnExpress",
    "enabled": true,
    "crawler_type": "static",
    "category_mapping": {
        "thoi-su": "POLITICS",
        "the-gioi": "WORLD",
        "kinh-doanh": "BUSINESS",
        "giai-tri": "ENTERTAINMENT",
        "the-thao": "SPORTS",
        "phap-luat": "LAW",
        "giao-duc": "EDUCATION",
        "suc-khoe": "HEALTH",
        "doi-song": "LIFESTYLE",
        "du-lich": "TRAVEL",
        "khoa-hoc": "SCIENCE",
        "so-hoa": "TECH",
        "xe": "AUTO",
        "y-kien": "OPINION",
        "tam-su": "STORIES"
    },
    "list_page": {
        "url_pattern": "https://vnexpress.net/{category}",
        "selectors": {
            "article_links": "article.item-news h3.title-news a",
            "pagination": "div.pagination a"
        }
    },
    "detail_page": {
        "selectors": {
            "title": "h1.title-detail",
            "summary": "p.description",
            "content": "article.fck_detail",
            "thumbnail": "meta[property='og:image']",
            "published_date": "span.date",
            "category": "ul.breadcrumb li:last-child a",
            "tags": "div.tags a",
            "author": "p.author_mail strong"
        },
        "remove_elements": [
            "div.box_comment",
            "div.box_tinlienquan",
            "div.ads",
            "script",
            "iframe"
        ]
    },
    "rate_limit": {
        "requests_per_minute": 30,
        "delay_between_requests": 2
    },
    "schedule": {
        "cron": "0 */2 * * *",
        "description": "Chạy mỗi 2 giờ"
    }
}
```

#### config/domains/zingnews.json
```json
{
    "domain": "zingnews.vn",
    "name": "ZingNews",
    "enabled": true,
    "crawler_type": "dynamic",
    "category_mapping": {
        "thoi-su": "POLITICS",
        "the-gioi": "WORLD",
        "kinh-doanh-tai-chinh": "BUSINESS",
        "giai-tri": "ENTERTAINMENT",
        "the-thao": "SPORTS",
        "phap-luat": "LAW",
        "giao-duc": "EDUCATION",
        "suc-khoe": "HEALTH",
        "doi-song": "LIFESTYLE",
        "du-lich": "TRAVEL",
        "cong-nghe": "TECH",
        "oto-xe-may": "AUTO"
    },
    "list_page": {
        "url_pattern": "https://zingnews.vn/{category}",
        "selectors": {
            "article_links": "article.article-item h2 a",
            "pagination": "div.pagination a"
        }
    },
    "detail_page": {
        "selectors": {
            "title": "h1.the-article-title",
            "summary": "p.the-article-summary",
            "content": "div.the-article-body",
            "thumbnail": "meta[property='og:image']",
            "published_date": "span.the-article-publish",
            "category": "nav.breadcrumb li:last-child a",
            "tags": "div.the-article-tags a"
        },
        "remove_elements": [
            "div.inner-article",
            "div.ads",
            "script",
            "iframe"
        ]
    },
    "rate_limit": {
        "requests_per_minute": 30,
        "delay_between_requests": 2
    },
    "schedule": {
        "cron": "15 */2 * * *",
        "description": "Chạy mỗi 2 giờ, lệch 15 phút"
    }
}
```

---

## 💻 Code Implementation

### 1. Base Crawler Class

#### engine/base_crawler.py
```python
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


class BaseCrawler(ABC):
    """Base class cho tất cả crawler"""
    
    def __init__(self, config: Dict, api_client):
        """
        Args:
            config: Domain configuration từ JSON
            api_client: X-Wise API client instance
        """
        self.config = config
        self.api_client = api_client
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
            'User-Agent': self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        logger.info(f"Initialized {self.name} crawler")
    
    def _get_user_agent(self) -> str:
        """Get User-Agent từ env hoặc default"""
        import os
        return os.getenv('CRAWLER_USER_AGENT', 
                        f'XwiseNewsCrawler/1.0 (+https://x-wise.io; contact@x-wise.io)')
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """
        Fetch HTML content từ URL với retry logic
        
        Args:
            url: URL cần fetch
            retries: Số lần retry
            
        Returns:
            HTML content hoặc None nếu fail
        """
        # Check robots.txt
        if not self.robots_checker.can_fetch(url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        for attempt in range(retries):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.get(
                    url,
                    timeout=int(os.getenv('CRAWLER_TIMEOUT', 30))
                )
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
                delay = int(os.getenv('CRAWLER_RETRY_DELAY', 5))
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
        if not self.config.get('enabled', True):
            logger.warning(f"{self.name} crawler is disabled")
            return
        
        logger.info(f"Starting {self.name} crawler")
        
        # Get categories to crawl
        if categories is None:
            categories = list(self.config['category_mapping'].keys())
        
        total_articles = 0
        successful_articles = 0
        
        for category in categories:
            logger.info(f"Processing category: {category}")
            
            # Get article links
            article_links = self.crawl_list_page(category)
            
            for link in article_links:
                # Crawl article
                article_data = self.crawl_article(link)
                
                if article_data:
                    # Map category
                    xwise_category = self.config['category_mapping'].get(category)
                    article_data['category_code'] = xwise_category
                    
                    # Push to X-Wise
                    success = self.api_client.create_news(article_data)
                    
                    if success:
                        successful_articles += 1
                    
                    total_articles += 1
        
        logger.info(
            f"{self.name} crawler finished: "
            f"{successful_articles}/{total_articles} articles pushed successfully"
        )
```

---

### 2. Static Crawler (cho trang HTML tĩnh)

#### engine/static_crawler.py
```python
"""
Static Crawler
Xử lý các trang web render HTML tĩnh (server-side)
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger
from engine.base_crawler import BaseCrawler


class StaticCrawler(BaseCrawler):
    """Crawler cho trang web tĩnh"""
    
    def extract_article_links(self, html: str, base_url: str) -> List[str]:
        """Extract article links từ list page"""
        soup = BeautifulSoup(html, 'lxml')
        
        selector = self.config['list_page']['selectors']['article_links']
        links = []
        
        for element in soup.select(selector):
            href = element.get('href')
            if href:
                # Convert to absolute URL
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        return links
    
    def extract_article_data(self, html: str, url: str) -> Optional[Dict]:
        """Extract article data từ detail page"""
        soup = BeautifulSoup(html, 'lxml')
        selectors = self.config['detail_page']['selectors']
        
        try:
            # Extract title
            title_elem = soup.select_one(selectors['title'])
            if not title_elem:
                logger.warning(f"No title found: {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract summary
            summary_elem = soup.select_one(selectors.get('summary', ''))
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # Extract content
            content_elem = soup.select_one(selectors['content'])
            if not content_elem:
                logger.warning(f"No content found: {url}")
                return None
            
            # Remove unwanted elements
            for remove_selector in self.config['detail_page'].get('remove_elements', []):
                for elem in content_elem.select(remove_selector):
                    elem.decompose()
            
            content = str(content_elem)
            
            # Extract thumbnail
            thumbnail = ''
            if 'thumbnail' in selectors:
                thumb_elem = soup.select_one(selectors['thumbnail'])
                if thumb_elem:
                    thumbnail = thumb_elem.get('content') or thumb_elem.get('src', '')
            
            # Extract published date
            published_date = None
            if 'published_date' in selectors:
                date_elem = soup.select_one(selectors['published_date'])
                if date_elem:
                    published_date = date_elem.get_text(strip=True)
            
            # Extract tags
            tags = []
            if 'tags' in selectors:
                tag_elems = soup.select(selectors['tags'])
                tags = [tag.get_text(strip=True) for tag in tag_elems]
            
            # Extract author
            author = ''
            if 'author' in selectors:
                author_elem = soup.select_one(selectors['author'])
                if author_elem:
                    author = author_elem.get_text(strip=True)
            
            return {
                'title': title,
                'summary': summary,
                'content': content,
                'thumbnail': thumbnail,
                'published_date': published_date,
                'tags': tags,
                'author': author
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data from {url}: {e}")
            return None
```

---

*Tài liệu tiếp tục ở phần 2...*


### 3. Dynamic Crawler (cho trang JavaScript-rendered)

#### engine/dynamic_crawler.py
```python
"""
Dynamic Crawler
Xử lý các trang web render bằng JavaScript (client-side)
Sử dụng Playwright để render trang trước khi extract
"""

from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger
from engine.base_crawler import BaseCrawler
import time


class DynamicCrawler(BaseCrawler):
    """Crawler cho trang web động (JavaScript-rendered)"""
    
    def __init__(self, config: Dict, api_client):
        super().__init__(config, api_client)
        self.playwright = None
        self.browser = None
    
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def fetch_page_dynamic(self, url: str, wait_selector: str = None) -> Optional[str]:
        """
        Fetch page với Playwright, đợi JavaScript render
        
        Args:
            url: URL cần fetch
            wait_selector: CSS selector để đợi load xong
            
        Returns:
            HTML content sau khi render
        """
        if not self.browser:
            logger.error("Browser not initialized. Use context manager.")
            return None
        
        # Check robots.txt
        if not self.robots_checker.can_fetch(url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        try:
            page = self.browser.new_page()
            page.set_extra_http_headers({
                'User-Agent': self._get_user_agent()
            })
            
            logger.debug(f"Loading page with Playwright: {url}")
            
            # Navigate to page
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for specific selector if provided
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=10000)
            else:
                # Default wait for body
                page.wait_for_selector('body', timeout=10000)
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get HTML content
            html = page.content()
            
            page.close()
            
            logger.success(f"Successfully fetched with Playwright: {url}")
            return html
            
        except Exception as e:
            logger.error(f"Error fetching page with Playwright: {e}")
            return None
    
    def extract_article_links(self, html: str, base_url: str) -> List[str]:
        """Extract article links từ list page"""
        soup = BeautifulSoup(html, 'lxml')
        
        selector = self.config['list_page']['selectors']['article_links']
        links = []
        
        for element in soup.select(selector):
            href = element.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        return links
    
    def extract_article_data(self, html: str, url: str) -> Optional[Dict]:
        """Extract article data từ detail page"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Try to extract from JSON-LD first (schema.org)
        json_ld_data = self._extract_from_json_ld(soup)
        if json_ld_data:
            logger.info("Extracted data from JSON-LD")
            return json_ld_data
        
        # Fallback to HTML selectors
        return self._extract_from_html(soup, url)
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract article data từ JSON-LD (schema.org/Article)
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article data hoặc None
        """
        import json
        
        try:
            # Find JSON-LD script tag
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Check if it's an Article
                    if isinstance(data, dict) and data.get('@type') in ['Article', 'NewsArticle']:
                        return {
                            'title': data.get('headline', ''),
                            'summary': data.get('description', ''),
                            'content': data.get('articleBody', ''),
                            'thumbnail': data.get('image', {}).get('url', '') if isinstance(data.get('image'), dict) else data.get('image', ''),
                            'published_date': data.get('datePublished', ''),
                            'author': data.get('author', {}).get('name', '') if isinstance(data.get('author'), dict) else '',
                            'tags': data.get('keywords', '').split(',') if isinstance(data.get('keywords'), str) else []
                        }
                        
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            logger.debug(f"No valid JSON-LD found: {e}")
        
        return None
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Extract article data từ HTML selectors"""
        selectors = self.config['detail_page']['selectors']
        
        try:
            # Extract title
            title_elem = soup.select_one(selectors['title'])
            if not title_elem:
                logger.warning(f"No title found: {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract summary
            summary_elem = soup.select_one(selectors.get('summary', ''))
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # Extract content
            content_elem = soup.select_one(selectors['content'])
            if not content_elem:
                logger.warning(f"No content found: {url}")
                return None
            
            # Remove unwanted elements
            for remove_selector in self.config['detail_page'].get('remove_elements', []):
                for elem in content_elem.select(remove_selector):
                    elem.decompose()
            
            content = str(content_elem)
            
            # Extract thumbnail
            thumbnail = ''
            if 'thumbnail' in selectors:
                thumb_elem = soup.select_one(selectors['thumbnail'])
                if thumb_elem:
                    thumbnail = thumb_elem.get('content') or thumb_elem.get('src', '')
            
            # Extract published date
            published_date = None
            if 'published_date' in selectors:
                date_elem = soup.select_one(selectors['published_date'])
                if date_elem:
                    published_date = date_elem.get_text(strip=True)
            
            # Extract tags
            tags = []
            if 'tags' in selectors:
                tag_elems = soup.select(selectors['tags'])
                tags = [tag.get_text(strip=True) for tag in tag_elems]
            
            # Extract author
            author = ''
            if 'author' in selectors:
                author_elem = soup.select_one(selectors['author'])
                if author_elem:
                    author = author_elem.get_text(strip=True)
            
            return {
                'title': title,
                'summary': summary,
                'content': content,
                'thumbnail': thumbnail,
                'published_date': published_date,
                'tags': tags,
                'author': author
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data from {url}: {e}")
            return None
    
    def crawl_list_page(self, category: str) -> List[str]:
        """Override để sử dụng Playwright"""
        url_pattern = self.config['list_page']['url_pattern']
        list_url = url_pattern.format(category=category)
        
        logger.info(f"Crawling list page with Playwright: {list_url}")
        
        # Use Playwright to fetch
        html = self.fetch_page_dynamic(
            list_url,
            wait_selector=self.config['list_page']['selectors']['article_links']
        )
        
        if not html:
            return []
        
        article_links = self.extract_article_links(html, list_url)
        
        # Normalize URLs
        normalized_links = [
            self.url_normalizer.normalize(link) 
            for link in article_links
        ]
        
        logger.info(f"Found {len(normalized_links)} articles in {category}")
        return normalized_links
    
    def crawl_article(self, url: str) -> Optional[Dict]:
        """Override để sử dụng Playwright"""
        logger.info(f"Crawling article with Playwright: {url}")
        
        # Use Playwright to fetch
        html = self.fetch_page_dynamic(
            url,
            wait_selector=self.config['detail_page']['selectors']['content']
        )
        
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
```

---

### 4. Utility Classes

#### utils/api_client.py
```python
"""
X-Wise API Client
Xử lý tất cả API calls tới CMS X-Wise
"""

import os
import requests
from typing import Dict, Optional, List
from loguru import logger
import time


class XWiseAPIClient:
    """Client để tương tác với X-Wise CMS API"""
    
    def __init__(self):
        self.base_url = os.getenv('XWISE_API_BASE_URL', 
                                   'https://backend-dev-cms-staging.up.railway.app')
        self.jwt_token = os.getenv('XWISE_JWT_TOKEN')
        
        if not self.jwt_token:
            raise ValueError("XWISE_JWT_TOKEN not found in environment variables")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        })
        
        # Cache categories
        self._categories_cache = None
        
        logger.info(f"Initialized X-Wise API Client: {self.base_url}")
    
    def get_categories(self) -> List[Dict]:
        """
        Lấy danh sách categories từ X-Wise
        
        Returns:
            List of category dictionaries
        """
        if self._categories_cache:
            return self._categories_cache
        
        try:
            url = f"{self.base_url}/cms/wise/categories/by-parent/NEWS"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self._categories_cache = data.get('data', [])
            
            logger.info(f"Loaded {len(self._categories_cache)} categories")
            return self._categories_cache
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        Download image từ URL và upload lên X-Wise
        
        Args:
            image_url: URL của ảnh cần upload
            
        Returns:
            Attachment ID hoặc None
        """
        try:
            # Download image
            logger.debug(f"Downloading image: {image_url}")
            img_response = requests.get(image_url, timeout=30, stream=True)
            img_response.raise_for_status()
            
            # Get filename from URL
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename:
                filename = 'image.jpg'
            
            # Upload to X-Wise
            url = f"{self.base_url}/cms/wise/attachment/upload"
            files = {
                'file': (filename, img_response.content, img_response.headers.get('content-type', 'image/jpeg'))
            }
            
            # Remove Content-Type header for multipart/form-data
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            
            upload_response = requests.post(url, files=files, headers=headers, timeout=60)
            upload_response.raise_for_status()
            
            data = upload_response.json()
            attachment_id = data.get('data', {}).get('id')
            
            if attachment_id:
                logger.success(f"Uploaded image: {attachment_id}")
                return attachment_id
            else:
                logger.warning("No attachment ID in response")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image {image_url}: {e}")
            return None
    
    def create_news(self, article_data: Dict) -> bool:
        """
        Tạo tin tức mới trên X-Wise
        
        Args:
            article_data: Dictionary chứa dữ liệu bài viết
                - title: str (required)
                - content: str (required)
                - summary: str (optional)
                - category_code: str (required)
                - thumbnail: str (optional, URL)
                - source_url: str (optional, for duplicate check)
                - source_name: str (optional, for logging)
                
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Validate required fields
            if not article_data.get('title'):
                logger.error("Missing required field: title")
                return False
            
            if not article_data.get('content'):
                logger.error("Missing required field: content")
                return False
            
            if not article_data.get('category_code'):
                logger.error("Missing required field: category_code")
                return False
            
            # Check duplicate using cache
            from storage.duplicate_checker import DuplicateChecker
            duplicate_checker = DuplicateChecker()
            
            source_url = article_data.get('source_url')
            if source_url and duplicate_checker.is_crawled(source_url):
                logger.info(f"Article already crawled: {source_url}")
                return False
            
            # Upload thumbnail if exists
            attachment_ids = []
            if article_data.get('thumbnail'):
                attachment_id = self.upload_image(article_data['thumbnail'])
                if attachment_id:
                    attachment_ids.append(attachment_id)
            
            # Add source info to content as HTML comment (for traceability)
            content = article_data['content']
            if source_url:
                source_name = article_data.get('source_name', 'Unknown')
                content += f'\n<!-- Source: {source_name} | URL: {source_url} -->'
            
            # Prepare payload
            payload = {
                'title': article_data['title'][:1000],  # Max 1000 chars
                'content': content[:50000],  # Max 50000 chars
                'status': 'ACTIVE',
                'category_code': article_data['category_code'],
                'attachments': attachment_ids
            }
            
            # Create news
            url = f"{self.base_url}/cms/wise/news"
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            news_id = data.get('data', {}).get('id')
            
            if news_id:
                # Mark as crawled in cache
                if source_url:
                    duplicate_checker.mark_crawled(source_url, news_id)
                
                logger.success(f"Created news: {news_id} - {article_data['title'][:50]}...")
                return True
            else:
                logger.warning("No news ID in response")
                return False
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error_data = e.response.json()
                logger.error(f"Validation error: {error_data}")
            elif e.response.status_code == 401:
                logger.error("Authentication failed. Check JWT token.")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Error creating news: {e}")
            return False
    
    def check_duplicate(self, source_url: str) -> bool:
        """
        Kiểm tra xem bài viết đã tồn tại chưa
        
        Note: Sử dụng Redis cache để check duplicate vì database không có trường source_url
        
        Args:
            source_url: URL nguồn của bài viết
            
        Returns:
            True nếu đã tồn tại, False nếu chưa
        """
        from storage.duplicate_checker import DuplicateChecker
        duplicate_checker = DuplicateChecker()
        return duplicate_checker.is_crawled(source_url)
```

#### utils/content_cleaner.py
```python
"""
Content Cleaner
Làm sạch và chuẩn hóa nội dung HTML
"""

from bs4 import BeautifulSoup
import re
from loguru import logger


class ContentCleaner:
    """Làm sạch nội dung HTML"""
    
    def __init__(self):
        # Danh sách các class/id thường chứa quảng cáo
        self.ad_patterns = [
            r'ad[s]?[-_]',
            r'advertisement',
            r'banner',
            r'sponsor',
            r'promo',
            r'commercial'
        ]
        
        # Danh sách các tag không mong muốn
        self.unwanted_tags = [
            'script', 'style', 'iframe', 'noscript',
            'embed', 'object', 'applet'
        ]
    
    def clean(self, html: str) -> str:
        """
        Làm sạch HTML content
        
        Args:
            html: Raw HTML content
            
        Returns:
            Cleaned HTML content
        """
        if not html:
            return ''
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove unwanted tags
            for tag_name in self.unwanted_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove elements with ad-related class/id
            for pattern in self.ad_patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                
                # Remove by class
                for tag in soup.find_all(class_=regex):
                    tag.decompose()
                
                # Remove by id
                for tag in soup.find_all(id=regex):
                    tag.decompose()
            
            # Remove empty paragraphs
            for p in soup.find_all('p'):
                if not p.get_text(strip=True):
                    p.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Additional text cleaning
            cleaned_html = self._clean_text(cleaned_html)
            
            return cleaned_html
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return html
    
    def _clean_text(self, html: str) -> str:
        """Làm sạch text trong HTML"""
        # Remove multiple spaces
        html = re.sub(r'\s+', ' ', html)
        
        # Remove spaces before punctuation
        html = re.sub(r'\s+([.,;:!?])', r'\1', html)
        
        # Remove multiple line breaks
        html = re.sub(r'\n\s*\n', '\n\n', html)
        
        return html.strip()
```

#### utils/url_normalizer.py
```python
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
```

#### utils/rate_limiter.py
```python
"""
Rate Limiter
Giới hạn số request per minute
"""

import time
from collections import deque
from loguru import logger


class RateLimiter:
    """Rate limiter sử dụng sliding window"""
    
    def __init__(self, requests_per_minute: int = 30):
        """
        Args:
            requests_per_minute: Số request tối đa mỗi phút
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.requests = deque()
    
    def wait_if_needed(self):
        """Đợi nếu đã vượt quá rate limit"""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window_size:
            self.requests.popleft()
        
        # Check if we need to wait
        if len(self.requests) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.requests[0]
            wait_time = self.window_size - (now - oldest_request)
            
            if wait_time > 0:
                logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                
                # Clean up again after waiting
                now = time.time()
                while self.requests and self.requests[0] < now - self.window_size:
                    self.requests.popleft()
        
        # Record this request
        self.requests.append(time.time())
```

#### utils/robots_checker.py
```python
"""
Robots.txt Checker
Kiểm tra robots.txt trước khi crawl
"""

from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
from loguru import logger
import requests


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
```

#### utils/logger.py
```python
"""
Logger Setup
Cấu hình logging cho toàn bộ hệ thống
"""

import os
import sys
from loguru import logger


def setup_logger():
    """Setup logger với rotation và retention"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv('LOG_LEVEL', 'INFO'),
        colorize=True
    )
    
    # File handler
    log_file = os.getenv('LOG_FILE', 'logs/crawler.log')
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=os.getenv('LOG_LEVEL', 'INFO'),
        rotation=os.getenv('LOG_ROTATION', '10 MB'),
        retention=os.getenv('LOG_RETENTION', '30 days'),
        compression='zip'
    )
    
    logger.info("Logger initialized")
```

---

*Tài liệu tiếp tục ở phần 3...*


### 5. Scheduler

#### scheduler/job_scheduler.py
```python
"""
Job Scheduler
Quản lý lịch chạy crawler định kỳ
"""

import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from scheduler.tasks import crawl_domain


class CrawlerScheduler:
    """Scheduler cho crawler jobs"""
    
    def __init__(self):
        timezone = os.getenv('SCHEDULER_TIMEZONE', 'Asia/Ho_Chi_Minh')
        self.scheduler = BlockingScheduler(timezone=timezone)
        logger.info(f"Initialized scheduler with timezone: {timezone}")
    
    def add_job(self, domain_config: dict):
        """
        Thêm job cho một domain
        
        Args:
            domain_config: Domain configuration dictionary
        """
        if not domain_config.get('enabled', True):
            logger.info(f"Skipping disabled domain: {domain_config['name']}")
            return
        
        schedule = domain_config.get('schedule', {})
        cron_expr = schedule.get('cron')
        
        if not cron_expr:
            logger.warning(f"No schedule defined for {domain_config['name']}")
            return
        
        # Parse cron expression
        # Format: minute hour day month day_of_week
        parts = cron_expr.split()
        if len(parts) != 5:
            logger.error(f"Invalid cron expression: {cron_expr}")
            return
        
        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            timezone=self.scheduler.timezone
        )
        
        job_id = f"crawl_{domain_config['domain']}"
        
        self.scheduler.add_job(
            crawl_domain,
            trigger=trigger,
            args=[domain_config],
            id=job_id,
            name=f"Crawl {domain_config['name']}",
            replace_existing=True
        )
        
        logger.info(
            f"Added job: {domain_config['name']} - "
            f"Schedule: {schedule.get('description', cron_expr)}"
        )
    
    def start(self):
        """Start scheduler"""
        if not os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true':
            logger.warning("Scheduler is disabled")
            return
        
        logger.info("Starting scheduler...")
        logger.info(f"Jobs: {len(self.scheduler.get_jobs())}")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")
    
    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        logger.info(f"Scheduled jobs ({len(jobs)}):")
        for job in jobs:
            logger.info(f"  - {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")
```

#### scheduler/tasks.py
```python
"""
Scheduler Tasks
Định nghĩa các task được scheduler gọi
"""

from loguru import logger
from utils.api_client import XWiseAPIClient
from engine.static_crawler import StaticCrawler
from engine.dynamic_crawler import DynamicCrawler


def crawl_domain(domain_config: dict):
    """
    Task crawl một domain
    
    Args:
        domain_config: Domain configuration dictionary
    """
    logger.info(f"Starting scheduled crawl for {domain_config['name']}")
    
    try:
        # Initialize API client
        api_client = XWiseAPIClient()
        
        # Choose crawler type
        crawler_type = domain_config.get('crawler_type', 'static')
        
        if crawler_type == 'dynamic':
            # Use context manager for Playwright
            with DynamicCrawler(domain_config, api_client) as crawler:
                crawler.run()
        else:
            # Static crawler
            crawler = StaticCrawler(domain_config, api_client)
            crawler.run()
        
        logger.success(f"Completed scheduled crawl for {domain_config['name']}")
        
    except Exception as e:
        logger.error(f"Error in scheduled crawl for {domain_config['name']}: {e}")
        # TODO: Send notification (email/slack)
```

---

### 6. Storage & Caching

#### storage/cache.py
```python
"""
Redis Cache
Cache để tránh crawl duplicate và lưu trữ tạm
"""

import os
import redis
from typing import Optional
from loguru import logger
import json


class RedisCache:
    """Redis cache wrapper"""
    
    def __init__(self):
        redis_url = os.getenv('REDIS_URL')
        
        if redis_url:
            self.client = redis.from_url(redis_url, decode_responses=True)
        else:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', '127.0.0.1'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
        
        try:
            self.client.ping()
            logger.info("Connected to Redis")
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
```

#### storage/duplicate_checker.py
```python
"""
Duplicate Checker
Kiểm tra bài viết đã được crawl chưa
"""

from storage.cache import RedisCache
from loguru import logger
import hashlib


class DuplicateChecker:
    """Kiểm tra duplicate articles"""
    
    def __init__(self):
        self.cache = RedisCache()
        self.prefix = "crawler:article:"
        self.ttl = 30 * 24 * 60 * 60  # 30 days
    
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
```

---

### 7. Domain-Specific Crawlers

#### engine/crawlers/vnexpress.py
```python
"""
VnExpress Crawler
Crawler chuyên biệt cho VnExpress.net
"""

from engine.static_crawler import StaticCrawler
from loguru import logger


class VnExpressCrawler(StaticCrawler):
    """Crawler cho VnExpress.net"""
    
    def __init__(self, api_client):
        # Load config
        import json
        with open('config/domains/vnexpress.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        super().__init__(config, api_client)
        logger.info("Initialized VnExpress crawler")
    
    # Có thể override các method nếu cần custom logic
    # Ví dụ: xử lý đặc biệt cho VnExpress
```

#### engine/crawlers/zingnews.py
```python
"""
ZingNews Crawler
Crawler chuyên biệt cho ZingNews.vn
"""

from engine.dynamic_crawler import DynamicCrawler
from loguru import logger


class ZingNewsCrawler(DynamicCrawler):
    """Crawler cho ZingNews.vn"""
    
    def __init__(self, api_client):
        # Load config
        import json
        with open('config/domains/zingnews.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        super().__init__(config, api_client)
        logger.info("Initialized ZingNews crawler")
    
    # Có thể override các method nếu cần custom logic
```

---

### 8. Main Entry Point

#### main.py
```python
"""
Main Entry Point
Khởi động crawler system
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Setup logger
from utils.logger import setup_logger
setup_logger()

from scheduler.job_scheduler import CrawlerScheduler
from utils.api_client import XWiseAPIClient
from engine.static_crawler import StaticCrawler
from engine.dynamic_crawler import DynamicCrawler


def load_domain_configs():
    """Load tất cả domain configurations"""
    config_dir = Path('config/domains')
    configs = []
    
    for config_file in config_dir.glob('*.json'):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                configs.append(config)
                logger.info(f"Loaded config: {config['name']}")
        except Exception as e:
            logger.error(f"Error loading {config_file}: {e}")
    
    return configs


def run_once(domain_name: str = None):
    """
    Chạy crawler một lần (không dùng scheduler)
    
    Args:
        domain_name: Tên domain cần crawl, None = all domains
    """
    logger.info("Running crawler in one-time mode")
    
    # Load configs
    configs = load_domain_configs()
    
    # Filter by domain name if specified
    if domain_name:
        configs = [c for c in configs if c['domain'] == domain_name or c['name'] == domain_name]
        if not configs:
            logger.error(f"Domain not found: {domain_name}")
            return
    
    # Initialize API client
    api_client = XWiseAPIClient()
    
    # Run crawlers
    for config in configs:
        if not config.get('enabled', True):
            logger.info(f"Skipping disabled domain: {config['name']}")
            continue
        
        logger.info(f"Crawling {config['name']}...")
        
        try:
            crawler_type = config.get('crawler_type', 'static')
            
            if crawler_type == 'dynamic':
                with DynamicCrawler(config, api_client) as crawler:
                    crawler.run()
            else:
                crawler = StaticCrawler(config, api_client)
                crawler.run()
                
        except Exception as e:
            logger.error(f"Error crawling {config['name']}: {e}")


def run_scheduler():
    """Chạy crawler với scheduler"""
    logger.info("Running crawler in scheduler mode")
    
    # Load configs
    configs = load_domain_configs()
    
    # Initialize scheduler
    scheduler = CrawlerScheduler()
    
    # Add jobs
    for config in configs:
        scheduler.add_job(config)
    
    # List jobs
    scheduler.list_jobs()
    
    # Start scheduler
    scheduler.start()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='X-Wise News Crawler')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduler'],
        default='scheduler',
        help='Run mode: once (one-time) or scheduler (continuous)'
    )
    parser.add_argument(
        '--domain',
        type=str,
        help='Domain to crawl (only for once mode)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("X-Wise News Crawler System")
    logger.info("=" * 60)
    
    try:
        if args.mode == 'once':
            run_once(args.domain)
        else:
            run_scheduler()
            
    except KeyboardInterrupt:
        logger.info("Crawler stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Cài Đặt

```bash
# Clone repository
git clone <repository-url>
cd news-crawler

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright browsers (nếu cần crawl trang JS)
playwright install chromium
```

### 2. Cấu Hình

```bash
# Copy .env.example sang .env
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
nano .env
```

**Quan trọng:** Cần cấu hình `XWISE_JWT_TOKEN` để kết nối với API X-Wise.

### 3. Chạy Crawler

#### Chạy một lần (test)
```bash
# Crawl tất cả domains
python main.py --mode once

# Crawl một domain cụ thể
python main.py --mode once --domain vnexpress.net
```

#### Chạy với scheduler (production)
```bash
# Chạy scheduler (chạy liên tục theo lịch)
python main.py --mode scheduler

# Hoặc dùng nohup để chạy background
nohup python main.py --mode scheduler > crawler.log 2>&1 &
```

### 4. Kiểm Tra Logs

```bash
# Xem logs realtime
tail -f logs/crawler.log

# Tìm lỗi
grep ERROR logs/crawler.log

# Xem thống kê
grep "Successfully" logs/crawler.log | wc -l
```

---

## 📊 Monitoring & Alerting

### 1. Log Monitoring

Logs được lưu tại `logs/crawler.log` với các level:
- **DEBUG**: Chi tiết request/response
- **INFO**: Thông tin chung
- **SUCCESS**: Thành công
- **WARNING**: Cảnh báo
- **ERROR**: Lỗi

### 2. Notification Setup (Optional)

#### Slack Webhook
```python
# Thêm vào .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Trong code (utils/notifier.py)
import requests

def send_slack_alert(message: str):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={'text': message})
```

#### Email Alert
```python
# Thêm vào .env
EMAIL_NOTIFICATION=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=admin@x-wise.io

# Sử dụng trong error handler
```

---

## 🔒 Bảo Mật & Best Practices

### 1. Environment Variables
- **KHÔNG BAO GIỜ** commit file `.env` vào git
- Sử dụng `.env.example` làm template
- Rotate JWT token định kỳ

### 2. Rate Limiting
- Tuân thủ `robots.txt`
- Không vượt quá rate limit của từng domain
- Sử dụng delay giữa các request

### 3. Error Handling
- Retry với exponential backoff
- Log chi tiết lỗi
- Graceful degradation

### 4. Resource Management
- Close connections properly
- Use context managers cho Playwright
- Limit concurrent requests

---

## 🧪 Testing

### Unit Tests
```bash
# Chạy tests
pytest tests/

# Với coverage
pytest --cov=engine --cov=utils tests/
```

### Test Một Domain
```python
# test_vnexpress.py
from engine.crawlers.vnexpress import VnExpressCrawler
from utils.api_client import XWiseAPIClient

def test_vnexpress_crawler():
    api_client = XWiseAPIClient()
    crawler = VnExpressCrawler(api_client)
    
    # Test crawl một bài
    article_data = crawler.crawl_article('https://vnexpress.net/...')
    assert article_data is not None
    assert 'title' in article_data
    assert 'content' in article_data
```

---

## 📈 Scaling & Optimization

### 1. Distributed Crawling
```python
# Sử dụng Celery cho distributed tasks
from celery import Celery

app = Celery('crawler', broker='redis://localhost:6379/0')

@app.task
def crawl_article_task(url, config):
    # Crawl logic
    pass
```

### 2. Database Storage
```python
# Thay vì chỉ push API, có thể lưu vào DB trước
# Sau đó có worker riêng push lên X-Wise
# => Tăng reliability, có thể retry
```

### 3. Proxy Rotation
```python
# Sử dụng proxy pool để tránh bị block
PROXIES = [
    'http://proxy1:port',
    'http://proxy2:port',
]

# Rotate trong session
```

---

## 🐛 Troubleshooting

### Lỗi thường gặp

#### 1. 403 Forbidden
```
Nguyên nhân: Website block crawler
Giải pháp:
- Kiểm tra User-Agent
- Sử dụng proxy
- Giảm rate limit
- Thêm delay giữa requests
```

#### 2. Selector không tìm thấy element
```
Nguyên nhân: Website thay đổi layout
Giải pháp:
- Kiểm tra lại selector trong config
- Sử dụng browser DevTools để tìm selector mới
- Update config file
```

#### 3. JWT Token expired
```
Nguyên nhân: Token hết hạn
Giải pháp:
- Login lại vào CMS X-Wise
- Lấy token mới
- Update .env
```

#### 4. Playwright timeout
```
Nguyên nhân: Trang load chậm
Giải pháp:
- Tăng timeout trong config
- Kiểm tra network
- Sử dụng wait_for_selector phù hợp
```

---

## 📝 Ghi Chú Quan Trọng

### Điều Chỉnh Theo Hệ Thống X-Wise

1. **Database Schema**: Crawler SỬ DỤNG SCHEMA HIỆN TẠI, không thêm trường mới:
   - Thông tin `source_url`, `source_name` lưu trong **Redis cache** để check duplicate
   - Có thể embed source info vào cuối `content` dưới dạng HTML comment nếu cần trace
   - TTL cache: 90 ngày (configurable)

2. **Duplicate Check**: Sử dụng Redis cache thay vì database:
   - Key pattern: `crawler:article:<md5_hash_of_url>`
   - Value: `news_id` (UUID từ X-Wise)
   - Fast lookup, không cần query database
   - Nếu Redis clear, có thể crawl lại (acceptable trade-off)

3. **Category Mapping**: Cần tạo categories trong X-Wise trước:
   ```sql
   INSERT INTO category (code, name, parent_code, status) VALUES
   ('TECH', 'Công nghệ', 'NEWS', 'ACTIVE'),
   ('BUSINESS', 'Kinh doanh', 'NEWS', 'ACTIVE'),
   ('SPORTS', 'Thể thao', 'NEWS', 'ACTIVE'),
   ...
   ```

4. **Authentication**: JWT token cần được refresh định kỳ hoặc sử dụng service account với token không expire.

---

## 🎯 Roadmap

### Phase 1: MVP (Hiện tại)
- ✅ Base crawler framework
- ✅ Static & Dynamic crawlers
- ✅ API integration
- ✅ Scheduler
- ✅ Basic error handling

### Phase 2: Enhancement
- ⬜ Duplicate detection với database
- ⬜ Content similarity check
- ⬜ Auto category classification (ML)
- ⬜ Image optimization
- ⬜ Multi-language support

### Phase 3: Scale
- ⬜ Distributed crawling với Celery
- ⬜ Kubernetes deployment
- ⬜ Monitoring dashboard
- ⬜ Auto-scaling
- ⬜ A/B testing cho selectors

---

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs tại `logs/crawler.log`
2. Xem phần Troubleshooting
3. Liên hệ team X-Wise

---

**Tài liệu được tạo bởi**: Kiro AI Assistant  
**Ngày**: 2026-02-10  
**Version**: 1.0.0
