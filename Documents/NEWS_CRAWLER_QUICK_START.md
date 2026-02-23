# ⚡ Quick Start Guide - News Crawler

## 📋 Checklist Triển Khai

### Phase 1: Chuẩn Bị Backend X-Wise (30 phút)

- [ ] **Seed Categories**
  ```bash
  cd wise-cms-backend
  psql -h $DB_WISE_HOST -p $DB_WISE_PORT -U $DB_WISE_USER -d $DB_WISE_NAME < migrations/seed-news-categories.sql
  ```

- [ ] **Generate JWT Token**
  ```bash
  cd wise-cms-backend
  # Tạo file scripts/generate-crawler-token.ts (xem NEWS_CRAWLER_XWISE_ADJUSTMENTS.md)
  npm run ts-node scripts/generate-crawler-token.ts
  # Copy token vào notepad
  ```

- [ ] **Verify Redis**
  ```bash
  redis-cli ping
  # Nếu chưa có Redis, cài đặt:
  # docker run -d -p 6379:6379 redis:7-alpine
  ```

### Phase 2: Setup Crawler (20 phút)

- [ ] **Clone & Install**
  ```bash
  mkdir news-crawler
  cd news-crawler
  
  # Copy tất cả files NEWS_CRAWLER_* vào đây
  # Tạo cấu trúc thư mục theo NEWS_CRAWLER_SYSTEM_DESIGN.md
  
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  playwright install chromium
  ```

- [ ] **Cấu Hình .env**
  ```bash
  cp .env.example .env
  nano .env
  
  # Điền:
  # XWISE_JWT_TOKEN=<token từ phase 1>
  # XWISE_API_BASE_URL=https://backend-dev-cms-staging.up.railway.app
  # REDIS_HOST=127.0.0.1
  # REDIS_PORT=6379
  ```

- [ ] **Tạo Config Files**
  ```bash
  mkdir -p config/domains
  # Copy vnexpress.json, zingnews.json, tuoitre.json, dantri.json vào config/domains/
  ```

### Phase 3: Test (15 phút)

- [ ] **Test API Connection**
  ```bash
  # Test với curl
  curl -X GET "https://backend-dev-cms-staging.up.railway.app/cms/wise/categories/by-parent/NEWS" \
    -H "Authorization: Bearer $XWISE_JWT_TOKEN"
  
  # Phải trả về list categories
  ```

- [ ] **Test Crawl Một Bài**
  ```bash
  python main.py --mode once --domain vnexpress.net
  
  # Xem logs
  tail -f logs/crawler.log
  ```

- [ ] **Verify Database**
  ```bash
  psql -h $DB_WISE_HOST -U $DB_WISE_USER -d $DB_WISE_NAME \
    -c "SELECT id, title, category_code, created_at FROM news ORDER BY created_at DESC LIMIT 5;"
  ```

- [ ] **Verify Redis Cache**
  ```bash
  redis-cli
  > KEYS crawler:article:*
  > GET crawler:article:<hash>
  ```

### Phase 4: Production (10 phút)

- [ ] **Chạy Scheduler**
  ```bash
  # Test scheduler trước
  python main.py --mode scheduler
  # Ctrl+C để stop
  
  # Chạy background
  nohup python main.py --mode scheduler > crawler.log 2>&1 &
  
  # Hoặc dùng Docker
  docker-compose up -d
  ```

- [ ] **Monitor**
  ```bash
  # Xem logs
  tail -f logs/crawler.log
  
  # Check process
  ps aux | grep "python main.py"
  
  # Check Redis
  redis-cli INFO stats
  ```

---

## 🔥 Troubleshooting Nhanh

### Lỗi: 401 Unauthorized
```bash
# JWT token sai hoặc expired
# Generate lại token và update .env
```

### Lỗi: Category not found
```bash
# Chưa seed categories
# Chạy lại migration seed-news-categories.sql
```

### Lỗi: Redis connection refused
```bash
# Redis chưa chạy
docker run -d -p 6379:6379 redis:7-alpine
```

### Lỗi: Selector not found
```bash
# Website thay đổi layout
# Update selector trong config/domains/<domain>.json
# Dùng browser DevTools để tìm selector mới
```

### Lỗi: 403 Forbidden từ website
```bash
# Website block crawler
# Giảm rate_limit trong config
# Thêm delay_between_requests
# Hoặc sử dụng proxy
```

---

## 📊 Monitoring Commands

```bash
# Xem số bài đã crawl hôm nay
psql -h $DB_WISE_HOST -U $DB_WISE_USER -d $DB_WISE_NAME \
  -c "SELECT COUNT(*) FROM news WHERE created_at::date = CURRENT_DATE;"

# Xem số bài theo category
psql -h $DB_WISE_HOST -U $DB_WISE_USER -d $DB_WISE_NAME \
  -c "SELECT category_code, COUNT(*) FROM news GROUP BY category_code ORDER BY COUNT(*) DESC;"

# Xem cache size trong Redis
redis-cli
> DBSIZE
> INFO memory

# Xem logs errors
grep ERROR logs/crawler.log | tail -20

# Xem logs success
grep "Successfully" logs/crawler.log | wc -l
```

---

## 🎯 Expected Results

Sau khi chạy thành công:

- ✅ Mỗi 2 giờ crawler tự động chạy
- ✅ Mỗi lần crawl ~20-50 bài/domain
- ✅ Duplicate rate < 5% (nhờ Redis cache)
- ✅ Success rate > 90%
- ✅ Logs không có ERROR liên tục

---

## 📞 Quick Help

| Vấn đề | File tham khảo |
|--------|----------------|
| Kiến trúc tổng thể | `NEWS_CRAWLER_SYSTEM_DESIGN.md` |
| Hướng dẫn chi tiết | `NEWS_CRAWLER_README.md` |
| Thay đổi backend | `NEWS_CRAWLER_XWISE_ADJUSTMENTS.md` |
| Tóm tắt | `NEWS_CRAWLER_SUMMARY.md` |
| Config mẫu | `NEWS_CRAWLER_*_CONFIG.json` |

---

**Estimated Total Time**: ~75 phút  
**Difficulty**: Medium  
**Prerequisites**: Python 3.9+, PostgreSQL, Redis
