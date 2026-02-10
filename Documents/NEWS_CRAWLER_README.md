# 🗞️ X-Wise News Crawler System

Hệ thống crawler tự động thu thập tin tức từ các trang báo tiếng Việt và đẩy vào CMS X-Wise.

## 📋 Tổng Quan

Crawler này được thiết kế để:
- Thu thập tin tức từ nhiều nguồn báo Việt Nam (VnExpress, ZingNews, Tuổi Trẻ, Dân Trí, v.v.)
- Tự động trích xuất và chuẩn hóa nội dung
- Tích hợp với CMS X-Wise qua REST API
- Chạy định kỳ theo lịch cấu hình
- Xử lý lỗi và logging chi tiết

## 🚀 Quick Start

### 1. Cài Đặt

```bash
# Clone repository
git clone <repository-url>
cd news-crawler

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright (nếu cần crawl trang JS)
playwright install chromium
```

### 2. Cấu Hình

```bash
# Copy file .env mẫu
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
nano .env
```

**Quan trọng**: Cần cấu hình `XWISE_JWT_TOKEN` để kết nối với API X-Wise.

### 3. Chạy Crawler

```bash
# Test crawl một domain
python main.py --mode once --domain vnexpress.net

# Chạy tất cả domains một lần
python main.py --mode once

# Chạy với scheduler (production)
python main.py --mode scheduler
```

## 📁 Cấu Trúc Dự Án

```
news-crawler/
├── config/
│   ├── settings.py              # Cấu hình chung
│   └── domains/                 # Cấu hình từng domain
│       ├── vnexpress.json
│       ├── zingnews.json
│       ├── tuoitre.json
│       └── dantri.json
├── engine/
│   ├── base_crawler.py          # Base crawler class
│   ├── static_crawler.py        # Crawler cho trang tĩnh
│   ├── dynamic_crawler.py       # Crawler cho trang JS
│   └── crawlers/                # Domain-specific crawlers
│       ├── vnexpress.py
│       ├── zingnews.py
│       ├── tuoitre.py
│       └── dantri.py
├── utils/
│   ├── api_client.py            # X-Wise API client
│   ├── content_cleaner.py       # Làm sạch nội dung
│   ├── url_normalizer.py        # Chuẩn hóa URL
│   ├── rate_limiter.py          # Rate limiting
│   ├── robots_checker.py        # Kiểm tra robots.txt
│   └── logger.py                # Logging setup
├── scheduler/
│   ├── job_scheduler.py         # APScheduler setup
│   └── tasks.py                 # Định nghĩa tasks
├── storage/
│   ├── cache.py                 # Redis cache
│   └── duplicate_checker.py     # Kiểm tra duplicate
├── tests/                       # Unit tests
├── logs/                        # Log files
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── main.py                      # Entry point
└── README.md                    # This file
```

## ⚙️ Cấu Hình Domain

Mỗi domain có file JSON riêng trong `config/domains/`:

```json
{
    "domain": "vnexpress.net",
    "name": "VnExpress",
    "enabled": true,
    "crawler_type": "static",
    "category_mapping": {
        "thoi-su": "POLITICS",
        "kinh-doanh": "BUSINESS",
        ...
    },
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
            ...
        }
    },
    "rate_limit": {
        "requests_per_minute": 30
    },
    "schedule": {
        "cron": "0 */2 * * *",
        "description": "Chạy mỗi 2 giờ"
    }
}
```

## 🔧 API X-Wise

### Endpoints Sử Dụng

#### 1. Tạo Tin Tức
```http
POST /cms/wise/news
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "title": "string",
    "content": "string (HTML)",
    "status": "ACTIVE",
    "category_code": "string",
    "attachments": ["uuid1", "uuid2"]
}
```

#### 2. Upload Ảnh
```http
POST /cms/wise/attachment/upload
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

file: <binary>
```

#### 3. Lấy Categories
```http
GET /cms/wise/categories/by-parent/NEWS
Authorization: Bearer <JWT_TOKEN>
```

## 📊 Monitoring

### Xem Logs

```bash
# Realtime logs
tail -f logs/crawler.log

# Tìm lỗi
grep ERROR logs/crawler.log

# Thống kê thành công
grep "Successfully" logs/crawler.log | wc -l
```

### Log Levels

- **DEBUG**: Chi tiết request/response
- **INFO**: Thông tin chung
- **SUCCESS**: Thành công
- **WARNING**: Cảnh báo
- **ERROR**: Lỗi

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest tests/

# Với coverage
pytest --cov=engine --cov=utils tests/

# Test một file cụ thể
pytest tests/test_crawlers.py -v
```

## 🐛 Troubleshooting

### Lỗi 403 Forbidden
```
Nguyên nhân: Website block crawler
Giải pháp:
- Kiểm tra User-Agent
- Giảm rate limit
- Sử dụng proxy
```

### Selector không tìm thấy
```
Nguyên nhân: Website thay đổi layout
Giải pháp:
- Inspect element trên browser
- Update selector trong config JSON
```

### JWT Token expired
```
Nguyên nhân: Token hết hạn
Giải pháp:
- Login lại CMS X-Wise
- Lấy token mới
- Update .env
```

## 📝 Thêm Domain Mới

### Bước 1: Tạo Config File

Tạo file `config/domains/newsite.json`:

```json
{
    "domain": "newsite.vn",
    "name": "New Site",
    "enabled": true,
    "crawler_type": "static",
    "category_mapping": {...},
    "list_page": {...},
    "detail_page": {...},
    "rate_limit": {...},
    "schedule": {...}
}
```

### Bước 2: Tìm Selectors

1. Mở trang web trong browser
2. Inspect element (F12)
3. Tìm CSS selector cho:
   - Article links trong list page
   - Title, content, thumbnail trong detail page

### Bước 3: Test

```bash
python main.py --mode once --domain newsite.vn
```

### Bước 4: Thêm vào Scheduler

Config đã có `schedule`, crawler sẽ tự động chạy theo lịch.

## 🔒 Bảo Mật

- ✅ Không commit file `.env`
- ✅ Sử dụng environment variables
- ✅ Tuân thủ `robots.txt`
- ✅ Rate limiting
- ✅ Rotate JWT token định kỳ

## 📈 Performance Tips

1. **Sử dụng Redis cache** để tránh crawl duplicate
2. **Giới hạn số bài** mỗi lần crawl: `MAX_ARTICLES_PER_CATEGORY`
3. **Chạy distributed** với Celery nếu cần scale
4. **Monitor memory** khi crawl nhiều domain

## 🚢 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["python", "main.py", "--mode", "scheduler"]
```

```bash
docker build -t xwise-crawler .
docker run -d --env-file .env xwise-crawler
```

### Systemd Service

```ini
[Unit]
Description=X-Wise News Crawler
After=network.target

[Service]
Type=simple
User=crawler
WorkingDirectory=/opt/news-crawler
ExecStart=/opt/news-crawler/venv/bin/python main.py --mode scheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📞 Support

- **Documentation**: Xem file `NEWS_CRAWLER_SYSTEM_DESIGN.md`
- **Issues**: Kiểm tra logs tại `logs/crawler.log`
- **Contact**: Team X-Wise

## 📄 License

Proprietary - X-Wise Global

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-10
