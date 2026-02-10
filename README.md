# 🗞️ X-Wise News Crawler

Hệ thống crawler tự động thu thập tin tức từ các trang báo tiếng Việt và đẩy vào CMS X-Wise.

## 🚀 Quick Start

### 1. Cài Đặt

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu Hình

```bash
# File .env đã có sẵn với database config
# Kiểm tra và điều chỉnh nếu cần
nano .env
```

Database config mặc định:
```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=123456789
DB_NAME=wise_local
```

### 3. Test Setup

```bash
python test_setup.py
```

### 4. Chạy Crawler

```bash
# Test crawl VnExpress
python main.py --mode once --domain vnexpress.net

# Xem logs
tail -f logs/crawler.log
```

## 📁 Cấu Trúc

```
Crawler/
├── config/
│   ├── settings.py              # Cấu hình chung
│   └── domains/
│       └── vnexpress.json       # Config VnExpress
├── engine/
│   ├── base_crawler.py          # Base crawler
│   └── static_crawler.py        # Static crawler
├── utils/
│   ├── db_client.py             # Database client (PostgreSQL)
│   ├── content_cleaner.py       # Làm sạch nội dung
│   ├── url_normalizer.py        # Chuẩn hóa URL
│   ├── rate_limiter.py          # Rate limiting
│   ├── robots_checker.py        # Kiểm tra robots.txt
│   └── logger.py                # Logging
├── storage/
│   ├── cache.py                 # Redis cache
│   └── duplicate_checker.py     # Check duplicate
├── logs/                        # Log files
├── .env                         # Environment config
├── requirements.txt             # Dependencies
├── main.py                      # Entry point
└── README.md                    # This file
```

## 🔧 Cấu Hình Domain

File `config/domains/vnexpress.json`:

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
    ...
}
```

## 📊 Monitoring

```bash
# Xem logs realtime
tail -f logs/crawler.log

# Tìm lỗi
grep ERROR logs/crawler.log

# Thống kê thành công
grep "Successfully" logs/crawler.log | wc -l
```

## 🐛 Troubleshooting

### Lỗi: No module named 'psycopg2'
```bash
# Cài đặt psycopg2
pip install psycopg2-binary
```

### Lỗi: Database connection refused
```bash
# Kiểm tra PostgreSQL đang chạy
nc -zv 127.0.0.1 5432

# Kiểm tra credentials trong .env
cat .env | grep DB_
```

### Lỗi: Redis connection refused
```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Or disable Redis in .env
REDIS_ENABLED=false
```

## 📝 Thêm Domain Mới

1. Tạo file `config/domains/newsite.json`
2. Tìm selectors bằng browser DevTools
3. Test: `python main.py --mode once --domain newsite.vn`

## 📞 Support

Xem tài liệu chi tiết trong folder `Documents/`
