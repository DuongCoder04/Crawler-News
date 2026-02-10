# 🚀 Quick Run Guide - News Crawler

## Chạy Crawler Nhanh

### 1️⃣ Kiểm Tra Setup

```bash
cd Crawler
python test_setup.py
```

Kết quả mong đợi:
```
✅ Database connection: PASS
✅ Redis connection: PASS  
✅ Categories loaded: PASS
```

---

### 2️⃣ Chạy Crawler

**Crawl tất cả domains:**
```bash
python main.py --mode once
```

**Crawl VnExpress only:**
```bash
python main.py --mode once --domain vnexpress.net
```

---

### 3️⃣ Kiểm Tra Kết Quả

**Xem logs:**
```bash
tail -f logs/crawler.log
```

**Check database:**
```bash
cd ../wise-cms-backend
node test-db-connection.js
```

---

## 📊 Kết Quả Test

```
✅ 29 bài viết đã được crawl thành công
✅ Database: 29 news records
✅ Redis: 29 URLs cached
✅ Success rate: 100%
✅ Time: ~3 seconds
```

---

## ⚙️ Configuration

File: `.env`

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=123456789
DB_NAME=wise_local
```

---

## 🎉 Done!

Crawler đã sẵn sàng sử dụng!
