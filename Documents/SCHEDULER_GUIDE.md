# 🕐 Scheduler Mode - Hướng Dẫn Sử Dụng

## 🎯 Tổng Quan

Scheduler mode cho phép crawler tự động chạy theo lịch mà không cần can thiệp thủ công. Crawler sẽ:
- ✅ Chạy initial crawl ngay khi khởi động
- ✅ Tự động crawl theo lịch đã cấu hình
- ✅ Chạy liên tục cho đến khi bạn dừng lại

---

## 🚀 Cách Khởi Động

### Linux/Mac

```bash
cd Crawler
./start_crawler.sh
```

### Windows

```cmd
cd Crawler
start_crawler.bat
```

### Manual

```bash
cd Crawler
python main.py --mode scheduler
```

---

## ⚙️ Cấu Hình Lịch Crawl

Mỗi domain có lịch riêng trong file config. Ví dụ `config/domains/vnexpress.json`:

```json
{
    "schedule": {
        "cron": "0 */2 * * *",
        "description": "Chạy mỗi 2 giờ"
    }
}
```

### Cron Format

```
minute hour day month weekday
```

### Ví Dụ

| Cron | Mô Tả |
|------|-------|
| `0 */2 * * *` | Mỗi 2 giờ |
| `0 */3 * * *` | Mỗi 3 giờ |
| `0 */4 * * *` | Mỗi 4 giờ |
| `0 * * * *` | Mỗi giờ |
| `0 8 * * *` | Hàng ngày lúc 8:00 |
| `0 0 * * *` | Hàng ngày lúc 00:00 |

---

## 📊 Lịch Hiện Tại

| Domain | Schedule | Status |
|--------|----------|--------|
| VnExpress | Mỗi 2 giờ | ✅ Enabled |
| Coin68 | Mỗi 3 giờ | ⚠️ Disabled (robots.txt) |
| Tạp Chí Bitcoin | Mỗi 3 giờ | ⚠️ Disabled (robots.txt) |
| Cointelegraph VN | Mỗi 4 giờ | ⚠️ Disabled (robots.txt) |
| Genk | Mỗi 2 giờ | ⚠️ Disabled (404) |
| ICTNews | Mỗi 2 giờ | ⚠️ Disabled (selector issue) |

**Hiện tại chỉ VnExpress đang active.**

---

## 📝 Log Output

Khi chạy scheduler, bạn sẽ thấy:

```
============================================================
X-Wise News Crawler System
============================================================
Running crawler in scheduler mode
Crawler will run automatically based on schedule configuration
Press Ctrl+C to stop

Loaded config: VnExpress
Connected to database: wise_local@127.0.0.1

Scheduled VnExpress: Every 2 hours - Chạy mỗi 2 giờ

============================================================
Running initial crawl for all domains...
============================================================

Crawling VnExpress...
Successfully extracted: Article Title...
Created news: uuid - Article Title...

============================================================
Scheduler started. Waiting for next scheduled run...
============================================================
```

---

## 🛑 Dừng Crawler

Nhấn `Ctrl+C` để dừng scheduler:

```
^C
Crawler stopped by user
```

---

## 🔧 Enable/Disable Domains

Để enable/disable một domain, edit file config:

```json
{
    "domain": "vnexpress.net",
    "name": "VnExpress",
    "enabled": true,  // false để disable
    ...
}
```

---

## 📊 Monitor Crawler

### Check Logs

```bash
# Real-time logs
tail -f logs/crawler.log

# Last 100 lines
tail -100 logs/crawler.log
```

### Check Database

```bash
cd ../wise-cms-backend
node test-db-connection.js
```

### Check Redis Cache

```bash
redis-cli
> KEYS crawler:article:*
> DBSIZE
```

---

## 🐛 Troubleshooting

### Scheduler Không Chạy

**Kiểm tra:**
1. Database connection OK?
2. Redis connection OK?
3. Domain configs có lỗi không?

```bash
python test_setup.py
```

### Không Crawl Được Bài Mới

**Nguyên nhân:**
- Bài đã được crawl (duplicate detection)
- Selector không đúng
- Website thay đổi cấu trúc

**Giải pháp:**
```bash
# Check logs
tail -f logs/crawler.log

# Test crawl thủ công
python main.py --mode once --domain vnexpress.net
```

### Memory/CPU Cao

**Giải pháp:**
- Giảm số lượng domains active
- Tăng delay giữa các requests
- Giảm `MAX_ARTICLES_PER_CATEGORY` trong `.env`

---

## 💡 Best Practices

### 1. Chạy Trong Screen/Tmux

```bash
# Start screen session
screen -S crawler

# Run crawler
cd Crawler
./start_crawler.sh

# Detach: Ctrl+A, D
# Reattach: screen -r crawler
```

### 2. Chạy Như Service (Systemd)

Tạo file `/etc/systemd/system/xwise-crawler.service`:

```ini
[Unit]
Description=X-Wise News Crawler
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Crawler
ExecStart=/path/to/Crawler/venv/bin/python main.py --mode scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable và start:
```bash
sudo systemctl enable xwise-crawler
sudo systemctl start xwise-crawler
sudo systemctl status xwise-crawler
```

### 3. Monitor với Logs

```bash
# Rotate logs tự động (đã config trong logger)
# Max size: 10MB
# Retention: 30 days
```

---

## 📈 Performance Tips

### 1. Điều Chỉnh Rate Limit

File `.env`:
```env
RATE_LIMIT_VNEXPRESS=30  # requests/minute
CRAWLER_TIMEOUT=30       # seconds
CRAWLER_MAX_RETRIES=3
```

### 2. Giới Hạn Articles

```env
MAX_ARTICLES_PER_CATEGORY=50  # Giảm xuống nếu cần
```

### 3. Redis Memory

```bash
# Check Redis memory
redis-cli INFO memory

# Clear old cache nếu cần
redis-cli FLUSHDB
```

---

## ✅ Checklist Trước Khi Chạy Production

- [ ] Database connection OK
- [ ] Redis connection OK
- [ ] Test crawl thành công
- [ ] Logs directory exists
- [ ] Disk space đủ
- [ ] Monitor setup (optional)
- [ ] Backup database
- [ ] Document lịch crawl

---

**Status:** ✅ READY TO USE  
**Recommendation:** Chạy trong screen/tmux hoặc systemd service  
**Last Updated:** 10/02/2026
