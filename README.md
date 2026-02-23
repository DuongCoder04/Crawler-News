# X-Wise News Crawler System 🗞️

Automated news crawler system for X-Wise CMS with CDN integration, scheduler, and multi-source support.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

## ✨ Features

- 🕷️ **Multi-Source Crawler** - VnExpress, Coin68, và nhiều nguồn khác
- ⏰ **Scheduler Mode** - Tự động crawl theo lịch
- 🎨 **Beautiful Console** - Colored output với stats tracking
- 📦 **CDN Integration** - Upload thumbnails lên 0x2labs CDN
- 💾 **Direct Database** - Kết nối trực tiếp PostgreSQL
- 🔄 **Duplicate Detection** - Redis cache để tránh trùng lặp
- 🤖 **Robots.txt Compliant** - Tuân thủ robots.txt
- 🚀 **Rate Limiting** - Tránh overload source websites
- 📊 **Statistics Tracking** - Real-time stats và reporting

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Redis server
- 0x2labs CDN API key

### Installation

```bash
# Clone repository
git clone https://github.com/DuongCoder04/Crawler-News.git
cd Crawler-News/Crawler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```bash
# Database
DB_WISE_HOST=your_host
DB_WISE_PORT=5432
DB_WISE_USER=postgres
DB_WISE_PASS=your_password
DB_WISE_NAME=wise_local

# CDN
CDN_UPLOAD_URL=https://upload.0x2labs.com/upload
CDN_API_KEY=your_api_key
CDN_BUCKET=images

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Run Crawler

```bash
# One-time crawl
python main.py --mode once --domain vnexpress

# Scheduler mode (continuous)
python main.py --mode scheduler

# All domains
python main.py --mode once
```

## 📖 Documentation

Comprehensive documentation available in [Documents/](Documents/) folder:

- **[Quick Start Guide](Documents/QUICK_RUN.md)** - Get started quickly
- **[System Design](Documents/NEWS_CRAWLER_SYSTEM_DESIGN.md)** - Architecture overview
- **[Scheduler Guide](Documents/SCHEDULER_GUIDE.md)** - Scheduler configuration
- **[CDN Upload](Documents/CDN_UPLOAD_IMPLEMENTATION.md)** - CDN integration
- **[Full Documentation Index](Documents/README.md)** - All documentation

## 🏗️ Architecture

```
┌─────────────────┐
│  Crawler        │
│  (main.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Static/Dynamic │
│  Crawler Engine │
└────────┬────────┘
         │
         ├──────────────┐
         ▼              ▼
┌─────────────┐  ┌─────────────┐
│  Download   │  │  Extract    │
│  Content    │  │  Data       │
└──────┬──────┘  └──────┬──────┘
       │                │
       └────────┬───────┘
                ▼
       ┌─────────────────┐
       │  Upload to CDN  │
       │  (0x2labs)      │
       └────────┬────────┘
                ▼
       ┌─────────────────┐
       │  Save to DB     │
       │  + Attachment   │
       └─────────────────┘
```

## 📊 Database Schema

### News Table
```sql
CREATE TABLE news (
    id UUID PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    category_code VARCHAR(255),
    status VARCHAR(255),
    created_at TIMESTAMP,
    reaction_count INTEGER
);
```

### Attachment Table
```sql
CREATE TABLE attachment (
    id UUID PRIMARY KEY,
    url VARCHAR(255),           -- CDN URL
    object_type VARCHAR(255),   -- 'news' (lowercase)
    object_id VARCHAR(255),     -- news.id
    file_name VARCHAR(255),
    extension VARCHAR(255),
    status VARCHAR(255),
    created_at TIMESTAMP
);
```

## 🎯 Supported Sources

| Source | Status | Categories | Schedule |
|--------|--------|-----------|----------|
| VnExpress | ✅ Active | 6 categories | Every 2 hours |
| Coin68 | ⚠️ Disabled | Blockchain | - |
| Tạp Chí Bitcoin | ⚠️ Disabled | Blockchain | - |
| Genk | ⚠️ Disabled | Tech | - |
| ICTNews | ⚠️ Disabled | Tech | - |

## 🔧 Configuration

### Domain Config Example

```json
{
  "name": "VnExpress",
  "domain": "vnexpress.net",
  "enabled": true,
  "crawler_type": "static",
  "list_page": {
    "url_pattern": "https://vnexpress.net/{category}",
    "selectors": {
      "article_links": "article.item-news h3.title-news a"
    }
  },
  "detail_page": {
    "selectors": {
      "title": "h1.title-detail",
      "content": "article.fck_detail",
      "thumbnail": "meta[property='og:image']"
    }
  },
  "category_mapping": {
    "thoi-su": "NEWS_POLITICS",
    "suc-khoe": "NEWS_HEALTH"
  },
  "rate_limit": {
    "requests_per_minute": 30
  },
  "schedule": {
    "cron": "0 */2 * * *",
    "description": "Every 2 hours"
  }
}
```

## 📈 Statistics

Real-time statistics during crawling:

```
📊 Statistics for VnExpress:
  ✓ New articles:      252
  ⊘ Duplicates:        214
  Σ Total processed:   467

💾 Database: 456 total articles
```

## 🛠️ Development

### Project Structure

```
Crawler/
├── config/              # Configuration files
│   ├── domains/        # Domain-specific configs
│   └── settings.py     # Global settings
├── engine/             # Crawler engines
│   ├── base_crawler.py
│   └── static_crawler.py
├── storage/            # Storage utilities
│   ├── cache.py
│   └── duplicate_checker.py
├── utils/              # Utilities
│   ├── cdn_uploader.py
│   ├── db_client.py
│   ├── console.py
│   └── logger.py
├── Documents/          # Documentation
├── main.py            # Entry point
└── requirements.txt   # Dependencies
```

### Testing

```bash
# Test CDN upload
python test_cdn_upload.py

# Verify database
python verify_cdn_attachments.py

# Test specific domain
python main.py --mode once --domain vnexpress
```

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check database credentials in .env
# Verify PostgreSQL is running
psql -h localhost -U postgres -d wise_local
```

**2. Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

**3. CDN Upload Failed**
```bash
# Verify API key in .env
# Test with curl:
curl -X POST https://upload.0x2labs.com/upload \
  -H "X-API-Key: your_key" \
  -F "file=@test.jpg" \
  -F "bucket=images"
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

- **Repository:** https://github.com/DuongCoder04/Crawler-News
- **Issues:** https://github.com/DuongCoder04/Crawler-News/issues

## 🙏 Acknowledgments

- VnExpress for news content
- 0x2labs for CDN services
- X-Wise CMS team

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-12  
**Status:** Production Ready ✅
