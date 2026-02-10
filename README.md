# 🗞️ News Crawler

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

Hệ thống crawler tự động thu thập tin tức từ các trang báo Việt Nam và lưu vào database.

## ✨ Features

- 🕐 **Scheduler Mode** - Tự động crawl theo lịch
- 🔄 **Duplicate Detection** - Redis cache với TTL 90 ngày
- 🗄️ **Direct Database** - Kết nối trực tiếp PostgreSQL
- 🤖 **robots.txt Compliance** - Tôn trọng quy tắc crawl
- ⚡ **Rate Limiting** - Kiểm soát tốc độ request
- 📝 **Structured Logging** - Logs với rotation tự động
- 🔧 **Easy Configuration** - JSON-based domain configs
- 🚀 **Production Ready** - Tested và verified

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone git@github.com:DuongCoder04/Crawler-News.git
cd Crawler-News
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your database credentials
nano .env
```

### 4. Test Setup

```bash
python test_setup.py
```

Expected output:
```
✅ Database connection: PASS
✅ Redis connection: PASS
✅ Categories loaded: PASS
```

### 5. Run Crawler

**Scheduler Mode (Recommended):**
```bash
# Linux/Mac
./start_crawler.sh

# Windows
start_crawler.bat

# Manual
python main.py --mode scheduler
```

**One-time Mode:**
```bash
# Crawl all domains
python main.py --mode once

# Crawl specific domain
python main.py --mode once --domain vnexpress.net

# Crawl blockchain news only
python crawl_blockchain.py
```

## 📊 Active Sources

| Source | Schedule | Categories | Status |
|--------|----------|------------|--------|
| **VnExpress** | Every 2 hours | 13 categories | ✅ **ACTIVE** |

## 📁 Project Structure

```
Crawler-News/
├── config/
│   ├── settings.py              # Global settings
│   └── domains/
│       └── vnexpress.json       # Domain configurations
├── engine/
│   ├── base_crawler.py          # Base crawler class
│   └── static_crawler.py        # Static HTML crawler
├── storage/
│   ├── cache.py                 # Redis cache manager
│   └── duplicate_checker.py     # Duplicate detection
├── utils/
│   ├── db_client.py             # PostgreSQL client
│   ├── content_cleaner.py       # HTML content cleaner
│   ├── url_normalizer.py        # URL normalization
│   ├── rate_limiter.py          # Rate limiting
│   ├── robots_checker.py        # robots.txt checker
│   └── logger.py                # Logging setup
├── logs/                        # Log files (auto-created)
├── main.py                      # Entry point
├── crawl_blockchain.py          # Blockchain crawler
├── start_crawler.sh             # Startup script (Linux/Mac)
├── start_crawler.bat            # Startup script (Windows)
└── test_setup.py                # Setup verification
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Database
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=wise_local

# Redis
REDIS_ENABLED=true
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Crawler
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3
MAX_ARTICLES_PER_CATEGORY=50
CACHE_TTL=7776000  # 90 days
```

### Schedule Configuration

Edit `config/domains/vnexpress.json`:

```json
{
    "schedule": {
        "cron": "0 */2 * * *",
        "description": "Chạy mỗi 2 giờ"
    }
}
```

**Cron Examples:**
- `0 */1 * * *` - Every hour
- `0 */2 * * *` - Every 2 hours
- `0 */3 * * *` - Every 3 hours
- `0 8 * * *` - Daily at 8:00 AM

## 📖 Documentation

- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Setup status & verification
- **[SCHEDULER_GUIDE.md](SCHEDULER_GUIDE.md)** - Scheduler mode guide
- **[CRAWLER_IMPLEMENTATION_COMPLETE.md](CRAWLER_IMPLEMENTATION_COMPLETE.md)** - Implementation details
- **[BLOCKCHAIN_NEWS_GUIDE.md](BLOCKCHAIN_NEWS_GUIDE.md)** - Blockchain sources guide
- **[QUICK_RUN.md](QUICK_RUN.md)** - Quick start commands

## 🔍 Monitoring

### Check Logs

```bash
# Real-time logs
tail -f logs/crawler.log

# Last 100 lines
tail -100 logs/crawler.log

# Search for errors
grep ERROR logs/crawler.log
```

### Check Database

```bash
# Verify news records
psql -U postgres -d wise_local -c "SELECT COUNT(*) FROM news;"
```

### Check Redis Cache

```bash
redis-cli KEYS crawler:article:*
redis-cli DBSIZE
```

## 🐛 Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
pg_isready -h 127.0.0.1 -p 5432

# Check credentials in .env
cat .env | grep DB_
```

### Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Start Redis if needed
redis-server
```

### No New Articles

This is normal behavior - duplicate detection is working:
```
INFO | Article already crawled: https://...
```

To test with fresh data:
```bash
# Clear Redis cache
redis-cli FLUSHDB
```

## 💡 Production Deployment

### Option 1: Systemd Service (Recommended)

Create `/etc/systemd/system/xwise-crawler.service`:

```ini
[Unit]
Description=News Crawler
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Crawler-News
ExecStart=/path/to/Crawler-News/venv/bin/python main.py --mode scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable xwise-crawler
sudo systemctl start xwise-crawler
sudo systemctl status xwise-crawler
```

### Option 2: Screen/Tmux

```bash
# Start screen session
screen -S crawler

# Run crawler
cd Crawler-News && ./start_crawler.sh

# Detach: Ctrl+A, D
# Reattach: screen -r crawler
```

## 📈 Performance

### Resource Usage

- **Memory:** < 100MB
- **CPU:** < 5% (idle), ~20% (crawling)
- **Disk:** ~10MB logs (auto-rotate)
- **Network:** ~1-2 MB per crawl

### Crawl Statistics

```
Domain: VnExpress
Schedule: Every 2 hours
Articles per run: 2-5 new articles
Success rate: 100%
Execution time: ~6 seconds
```

## 🔮 Roadmap

### Phase 2
- [ ] JavaScript rendering with Playwright
- [ ] RSS feed integration
- [ ] More news sources
- [ ] Email/Slack notifications
- [ ] Monitoring dashboard

### Phase 3
- [ ] ML-based categorization
- [ ] Sentiment analysis
- [ ] Image optimization
- [ ] CDN integration
- [ ] REST API endpoints

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**DuongCoder04**

- GitHub: [@DuongCoder04](https://github.com/DuongCoder04)
- Repository: [Crawler-News](https://github.com/DuongCoder04/Crawler-News)

## 🙏 Acknowledgments

- Built for CMS
- Powered by Python, PostgreSQL, and Redis
- Inspired by modern web scraping best practices

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** February 10, 2026

⭐ Star this repo if you find it useful!
