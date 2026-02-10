# 🔗 Blockchain News Crawler - Quick Guide

## 🚀 Cách Sử Dụng Nhanh

### Crawl Tin Blockchain/Crypto

```bash
cd Crawler

# Chạy script chuyên dụng
python crawl_blockchain.py
```

Script này sẽ:
- ✅ Crawl tin từ VnExpress - Số Hóa (blockchain, crypto, fintech, tech)
- ✅ Tự động check duplicate
- ✅ Lưu vào database với category TECH
- ✅ Log kết quả chi tiết

---

## 📊 Kết Quả Mong Đợi

```
2026-02-10 12:19:02 | INFO | Blockchain News Crawler
2026-02-10 12:19:02 | INFO | Loading VnExpress configuration...
2026-02-10 12:19:02 | INFO | Connecting to database...
2026-02-10 12:19:02 | SUCCESS | Connected to database: wise_local@127.0.0.1
2026-02-10 12:19:02 | INFO | Starting crawler...
2026-02-10 12:19:03 | SUCCESS | Successfully extracted: Elon Musk: 'Ưu tiên xây thành phố trên Mặt Trăng...
2026-02-10 12:19:03 | SUCCESS | Created news: 58ed50ab-d08d-4d2c-9888-5f1104bb11dc
2026-02-10 12:19:03 | SUCCESS | Blockchain news crawl completed!
```

---

## 🔧 Cấu Hình

### Nguồn Tin

**VnExpress - Số Hóa**
- URL: https://vnexpress.net/so-hoa
- Category: TECH
- Bao gồm: Blockchain, Crypto, Fintech, AI, Tech

### Rate Limit

- 30 requests/minute
- 2 seconds delay between requests
- Max 50 articles per run

### Duplicate Detection

- Redis cache với TTL 90 ngày
- Check URL trước khi crawl
- Tự động skip nếu đã crawl

---

## 📝 Các Nguồn Tin Khác

### Đã Cấu Hình (Cần Test)

1. **Genk** - `config/domains/genk.json`
   ```bash
   python main.py --mode once --domain genk.vn
   ```

2. **ICTNews** - `config/domains/ictnews.json`
   ```bash
   python main.py --mode once --domain ictnews.vn
   ```

### Bị Chặn (Không Thể Crawl)

- ⚠️ Coin68 - Blocked by robots.txt
- ⚠️ Tạp Chí Bitcoin - Blocked by robots.txt

---

## 🔄 Chạy Định Kỳ

### Cron Job (Recommended)

```bash
# Chạy mỗi 2 giờ
0 */2 * * * cd /path/to/Crawler && python crawl_blockchain.py >> logs/blockchain_cron.log 2>&1
```

### Manual Run

```bash
# Chạy một lần
python crawl_blockchain.py

# Xem logs
tail -f logs/crawler.log
```

---

## 📊 Kiểm Tra Kết Quả

### Check Database

```bash
cd ../wise-cms-backend
node test-db-connection.js
```

### Check Logs

```bash
tail -f logs/crawler.log
```

### Check Redis Cache

```bash
redis-cli
> KEYS crawler:article:*
> GET crawler:article:<hash>
```

---

## 🐛 Troubleshooting

### Không Crawl Được Bài Mới

**Nguyên nhân:** Bài đã được crawl trước đó

**Giải pháp:**
```bash
# Check Redis cache
redis-cli KEYS crawler:article:*

# Xóa cache nếu cần test lại
redis-cli FLUSHDB
```

### Database Connection Failed

**Giải pháp:**
```bash
# Check PostgreSQL
pg_isready -h 127.0.0.1 -p 5432

# Check .env
cat .env | grep DB_
```

### Redis Connection Failed

**Giải pháp:**
```bash
# Check Redis
redis-cli ping

# Start Redis if needed
redis-server
```

---

## 📚 Tài Liệu Liên Quan

- [BLOCKCHAIN_NEWS_GUIDE.md](BLOCKCHAIN_NEWS_GUIDE.md) - Hướng dẫn chi tiết
- [BLOCKCHAIN_NEWS_SUMMARY.md](BLOCKCHAIN_NEWS_SUMMARY.md) - Tổng kết
- [CRAWLER_IMPLEMENTATION_COMPLETE.md](CRAWLER_IMPLEMENTATION_COMPLETE.md) - Implementation report

---

## 💡 Tips

1. **Chạy định kỳ** - Setup cron job để tự động crawl
2. **Monitor logs** - Check logs thường xuyên
3. **Backup database** - Backup trước khi test
4. **Test trước** - Test với 1-2 bài trước khi chạy full

---

**Status:** ✅ READY TO USE  
**Last Updated:** 10/02/2026  
**Recommendation:** Chạy mỗi 2 giờ với cron job
