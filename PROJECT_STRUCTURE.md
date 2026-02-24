# X-Wise News Crawler - Project Structure

## 📁 Cấu trúc thư mục

```
Crawler-News/
├── config/                      # Cấu hình
│   ├── domains/                 # Cấu hình từng domain
│   │   ├── dantri.json         # ✓ Enabled
│   │   ├── thanhnien.json      # ✓ Enabled
│   │   ├── tuoitre.json        # ✓ Enabled
│   │   ├── vietnamnet.json     # ✓ Enabled
│   │   ├── vnexpress.json      # ✓ Enabled
│   │   ├── zingnews.json       # ✓ Enabled
│   │   ├── blockchainnews-vn.json  # ✗ Disabled
│   │   ├── coin68.json         # ✗ Disabled
│   │   ├── cointelegraph-vn.json   # ✗ Disabled
│   │   ├── genk.json           # ✗ Disabled
│   │   ├── ictnews.json        # ✗ Disabled
│   │   └── tapchibitcoin.json  # ✗ Disabled
│   ├── settings.py             # Global settings
│   └── __init__.py
│
├── engine/                      # Crawler engines
│   ├── base_crawler.py         # Base crawler class
│   ├── static_crawler.py       # Static HTML crawler
│   └── __init__.py
│
├── storage/                     # Storage & caching
│   ├── cache.py                # Redis cache
│   ├── duplicate_checker.py   # Check duplicate articles
│   └── __init__.py
│
├── utils/                       # Utilities
│   ├── api_client.py           # API client (deprecated)
│   ├── cdn_uploader.py         # Upload images to CDN
│   ├── console.py              # Console output formatting
│   ├── content_cleaner.py      # Clean HTML content
│   ├── db_client.py            # PostgreSQL database client
│   ├── logger.py               # Logging setup
│   ├── rate_limiter.py         # Rate limiting
│   ├── robots_checker.py       # Check robots.txt
│   ├── url_normalizer.py       # Normalize URLs
│   └── __init__.py
│
├── Documents/                   # Documentation
│   ├── CONTENT_CLEANING_IMPROVEMENTS.md  # Content cleaning guide
│   └── QUICK_RUN.md            # Quick start guide
│
├── logs/                        # Log files
│   └── crawler.log
│
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore rules
├── LICENSE                      # License file
├── main.py                      # Main entry point
├── README.md                    # Project README
├── requirements.txt             # Python dependencies
├── start_crawler.bat            # Windows start script
├── start_crawler.sh             # Linux/Mac start script
└── test_setup.py                # Setup test script
```

## 🚀 Core Files

### Main Entry Point
- **main.py** - Main crawler application with CLI interface

### Configuration
- **.env** - Environment variables (database, CDN, Redis)
- **config/settings.py** - Global settings loader
- **config/domains/*.json** - Domain-specific configurations

### Crawler Engine
- **engine/base_crawler.py** - Base crawler with common functionality
- **engine/static_crawler.py** - Static HTML crawler implementation

### Storage & Database
- **storage/cache.py** - Redis caching for duplicate checking
- **storage/duplicate_checker.py** - Check if article already crawled
- **utils/db_client.py** - PostgreSQL database operations

### Content Processing
- **utils/content_cleaner.py** - Clean and format HTML content
  - Remove unwanted elements (ads, scripts, etc.)
  - Fix lazy loading images
  - Remove links
  - Special handling for Dân Trí (remove title, category, author info)

### Utilities
- **utils/cdn_uploader.py** - Upload images to 0x2labs CDN
- **utils/console.py** - Beautiful console output
- **utils/logger.py** - Logging configuration
- **utils/rate_limiter.py** - Rate limiting for requests
- **utils/robots_checker.py** - Respect robots.txt
- **utils/url_normalizer.py** - Normalize URLs

## 📊 Active Domains (6)

1. **Dân Trí** (dantri.com.vn)
2. **Thanh Niên** (thanhnien.vn)
3. **Tuổi Trẻ** (tuoitre.vn)
4. **VietnamNet** (vietnamnet.vn)
5. **VnExpress** (vnexpress.net)
6. **Zing News** (zingnews.vn)

## 🔧 Usage

### One-time crawl
```bash
# Crawl all enabled domains
python main.py --mode once

# Crawl specific domain
python main.py --mode once --domain vnexpress.net
```

### Scheduler mode
```bash
# Run with automatic scheduling
python main.py --mode scheduler
```

### Windows
```cmd
start_crawler.bat
```

### Linux/Mac
```bash
./start_crawler.sh
```

## 📝 Key Features

### Content Cleaning
- Remove H1 title (already saved separately)
- Remove all links (convert to plain text)
- Remove category tags (THỜI SỰ, etc.)
- Remove author info (avatar, name, "Thực hiện:")
- Remove "(Dân trí) -" prefix
- Fix lazy loading images
- Remove ads, videos, social share buttons
- Normalize whitespace and formatting

### Database
- Direct PostgreSQL connection
- Store news with title, content, category, thumbnail
- Upload thumbnails to CDN
- Duplicate checking via Redis cache

### Rate Limiting
- Respect robots.txt
- Configurable requests per minute
- Retry logic with exponential backoff

## 🗑️ Cleaned Files

### Removed test files (16 files):
- test_content_cleaning.py
- test_category_tag.py
- test_new_html.py
- test_dantri_structure.py
- test_dantri_selector.py
- test_cdn_upload.py
- test_link_removal.py
- test_final_content.py
- test_content_cleaner.py
- test_dantri_content.py
- test_title_removal.py
- check_domains.py
- verify_cdn_attachments.py
- new.html
- crawl_blockchain.py
- main_old.py

### Removed documentation files (29 files):
- All redundant implementation/completion reports
- All duplicate README files
- Docker-related files (not using Docker)
- Blockchain-specific guides (not needed)
- Duplicate config files (moved to config/domains/)
- Git summaries and status reports

### Kept essential documents (2 files):
- Documents/CONTENT_CLEANING_IMPROVEMENTS.md - Content cleaning guide
- Documents/QUICK_RUN.md - Quick start guide

## 📦 Dependencies

See `requirements.txt` for full list. Key dependencies:
- requests, httpx - HTTP clients
- beautifulsoup4, lxml - HTML parsing
- psycopg2-binary - PostgreSQL
- redis - Caching
- loguru - Logging
- APScheduler - Scheduling
