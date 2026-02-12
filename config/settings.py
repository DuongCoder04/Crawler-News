"""
Global Settings
Cấu hình chung cho toàn bộ crawler system
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'wise_local')

# Crawler Configuration
CRAWLER_USER_AGENT = os.getenv('CRAWLER_USER_AGENT', 'XwiseNewsCrawler/1.0')
CRAWLER_TIMEOUT = int(os.getenv('CRAWLER_TIMEOUT', 30))
CRAWLER_MAX_RETRIES = int(os.getenv('CRAWLER_MAX_RETRIES', 3))
CRAWLER_RETRY_DELAY = int(os.getenv('CRAWLER_RETRY_DELAY', 5))

# Redis Configuration
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Scheduler Configuration
SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'Asia/Ho_Chi_Minh')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/crawler.log')
LOG_ROTATION = os.getenv('LOG_ROTATION', '10 MB')
LOG_RETENTION = os.getenv('LOG_RETENTION', '30 days')

# Advanced Configuration
MAX_ARTICLES_PER_CATEGORY = int(os.getenv('MAX_ARTICLES_PER_CATEGORY', 50))
CACHE_TTL = int(os.getenv('CACHE_TTL', 7776000))  # 90 days
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# CDN Configuration
CDN_UPLOAD_URL = os.getenv('CDN_UPLOAD_URL', 'https://upload.0x2labs.com/upload')
CDN_API_KEY = os.getenv('CDN_API_KEY', '')
CDN_BUCKET = os.getenv('CDN_BUCKET', 'images')
