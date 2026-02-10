# 📰 Hướng Dẫn Thêm Tin Tức Blockchain

## 🎯 Tổng Quan

Tài liệu này hướng dẫn cách thêm nguồn tin tức blockchain/cryptocurrency vào hệ thống crawler.

---

## 🔧 Các Nguồn Tin Đã Cấu Hình

### 1. VnExpress - Số Hóa ✅ WORKING
- **Domain:** vnexpress.net
- **Category:** so-hoa (bao gồm tin blockchain, crypto, fintech)
- **Status:** ✅ Đã test thành công
- **Mapping:** TECH category

### 2. Coin68 ⚠️ BLOCKED
- **Domain:** coin68.com
- **Status:** ⚠️ Bị chặn bởi robots.txt
- **Note:** Không thể crawl

### 3. Tạp Chí Bitcoin ⚠️ BLOCKED
- **Domain:** tapchibitcoin.io
- **Status:** ⚠️ Bị chặn bởi robots.txt
- **Note:** Không thể crawl

### 4. Genk 📝 CONFIGURED
- **Domain:** genk.vn
- **Categories:** cong-nghe, blockchain, crypto, startup
- **Status:** 📝 Đã config, cần test selector

### 5. ICTNews 📝 CONFIGURED
- **Domain:** ictnews.vn
- **Categories:** cong-nghe, blockchain, fintech, startup
- **Status:** 📝 Đã config, cần điều chỉnh selector

---

## 🚀 Cách Crawl Tin Blockchain

### Option 1: Sử Dụng VnExpress (Recommended ✅)

VnExpress có mục "Số hóa" bao gồm tin công nghệ, blockchain, crypto:

```bash
cd Crawler

# Crawl tất cả tin từ VnExpress (bao gồm blockchain)
python main.py --mode once --domain vnexpress.net

# Hoặc chỉ crawl category công nghệ
python -c "
from engine.static_crawler import StaticCrawler
from utils.db_client import DatabaseClient
import json

with open('config/domains/vnexpress.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

db_client = DatabaseClient()

# Chỉ crawl category 'so-hoa' (công nghệ/blockchain)
config['category_mapping'] = {'so-hoa': 'TECH'}

crawler = StaticCrawler(config, db_client)
crawler.run()
"
```

### Option 2: Thêm Nguồn Tin Mới

#### Bước 1: Tìm Nguồn Tin Cho Phép Crawl

Kiểm tra robots.txt trước:
```bash
curl https://example.com/robots.txt
```

Tìm dòng:
```
User-agent: *
Disallow:
```

Nếu `Disallow:` trống hoặc không chặn category bạn cần → OK để crawl

#### Bước 2: Tạo Config File

Tạo file `config/domains/your-domain.json`:

```json
{
    "domain": "example.com",
    "name": "Example News",
    "enabled": true,
    "crawler_type": "static",
    "description": "Tin tức blockchain",
    "category_mapping": {
        "blockchain": "TECH",
        "crypto": "TECH",
        "bitcoin": "TECH",
        "defi": "TECH",
        "nft": "TECH"
    },
    "list_page": {
        "url_pattern": "https://example.com/{category}",
        "selectors": {
            "article_links": "article h3 a, article h2 a",
            "pagination": "div.pagination a"
        }
    },
    "detail_page": {
        "selectors": {
            "title": "h1.article-title",
            "summary": "div.article-summary",
            "content": "div.article-content",
            "thumbnail": "meta[property='og:image']",
            "published_date": "time.published",
            "category": "span.category a",
            "tags": "div.tags a",
            "author": "span.author"
        },
        "remove_elements": [
            "div.comments",
            "div.ads",
            "script",
            "iframe"
        ]
    },
    "rate_limit": {
        "requests_per_minute": 20,
        "delay_between_requests": 3
    }
}
```

#### Bước 3: Tìm Đúng CSS Selectors

**Cách 1: Sử dụng Browser DevTools**

1. Mở trang web trong Chrome/Firefox
2. Nhấn F12 → Elements/Inspector
3. Click vào element bạn muốn select
4. Copy selector:
   - Chrome: Right-click → Copy → Copy selector
   - Firefox: Right-click → Copy → CSS Selector

**Cách 2: Test Selector với Python**

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com/blockchain"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Test selector
articles = soup.select("article h3 a")
print(f"Found {len(articles)} articles")

for article in articles[:5]:
    print(f"- {article.get('href')}: {article.text.strip()}")
```

#### Bước 4: Test Crawler

```bash
python main.py --mode once --domain example.com
```

Kiểm tra logs:
```bash
tail -f logs/crawler.log
```

---

## 📋 Checklist Thêm Nguồn Mới

- [ ] Kiểm tra robots.txt cho phép crawl
- [ ] Tạo config file với đúng domain
- [ ] Tìm đúng CSS selectors cho:
  - [ ] Article links trên list page
  - [ ] Title trên detail page
  - [ ] Content trên detail page
  - [ ] Thumbnail image
- [ ] Map categories sang X-Wise categories
- [ ] Test crawl với 1-2 articles
- [ ] Verify data trong database
- [ ] Enable trong production

---

## 🎯 Nguồn Tin Blockchain Khuyến Nghị

### Nguồn Tiếng Việt

1. **VnExpress - Số Hóa** ✅
   - URL: https://vnexpress.net/so-hoa
   - Ưu điểm: Cho phép crawl, tin uy tín
   - Nhược điểm: Không chuyên blockchain

2. **Genk** 📝
   - URL: https://genk.vn
   - Ưu điểm: Nhiều tin công nghệ, blockchain
   - Nhược điểm: Cần điều chỉnh selector

3. **ICTNews** 📝
   - URL: https://ictnews.vn
   - Ưu điểm: Chuyên tin ICT, có mục blockchain
   - Nhược điểm: Cần điều chỉnh selector

### Nguồn Tiếng Anh (Nếu Cần)

1. **CoinDesk**
   - URL: https://www.coindesk.com
   - Note: Cần check robots.txt

2. **Cointelegraph**
   - URL: https://cointelegraph.com
   - Note: Có phiên bản tiếng Việt

3. **Decrypt**
   - URL: https://decrypt.co
   - Note: Chuyên blockchain/crypto

---

## 🔍 Troubleshooting

### Vấn Đề 1: Bị Chặn Bởi robots.txt

**Triệu chứng:**
```
WARNING | Blocked by robots.txt: https://...
```

**Giải pháp:**
- Tôn trọng robots.txt
- Tìm nguồn tin khác
- Hoặc liên hệ chủ website xin phép

### Vấn Đề 2: Không Tìm Thấy Articles

**Triệu chứng:**
```
INFO | Found 0 articles in category
```

**Giải pháp:**
1. Kiểm tra URL category có đúng không
2. Kiểm tra CSS selector:
   ```python
   # Test selector
   soup.select("article h3 a")  # Thử selector khác
   ```
3. Kiểm tra trang có render bằng JavaScript không
   - Nếu có → Cần dùng Playwright (Phase 2)

### Vấn Đề 3: Content Bị Thiếu

**Triệu chứng:**
- Title OK nhưng content trống
- Hoặc content có nhiều ads/scripts

**Giải pháp:**
1. Kiểm tra selector cho content
2. Thêm elements cần remove vào `remove_elements`
3. Test với BeautifulSoup:
   ```python
   content = soup.select_one("div.article-content")
   # Remove unwanted elements
   for ad in content.select("div.ads"):
       ad.decompose()
   ```

---

## 📊 Kết Quả Hiện Tại

```bash
# Check database
cd ../wise-cms-backend
node test-db-connection.js
```

Expected output:
```
📰 News table: 30+ records
   - VnExpress: 29 articles (general news)
   - VnExpress Tech: 1 article (blockchain/tech)
```

---

## 🔮 Kế Hoạch Tương Lai

### Phase 2: JavaScript Rendering
- Sử dụng Playwright để crawl trang render bằng JS
- Hỗ trợ các trang blockchain hiện đại

### Phase 3: RSS Feed Integration
- Crawl từ RSS feed thay vì HTML
- Nhanh hơn và ổn định hơn

### Phase 4: API Integration
- Sử dụng API chính thức nếu có
- Ví dụ: CoinGecko API, CoinMarketCap API

---

## 💡 Tips

1. **Ưu tiên nguồn tin cho phép crawl**
   - Kiểm tra robots.txt trước
   - Tôn trọng rate limit

2. **Test selector kỹ trước khi chạy**
   - Dùng browser DevTools
   - Test với Python script nhỏ

3. **Monitor logs thường xuyên**
   - Check errors
   - Điều chỉnh selector khi cần

4. **Backup config**
   - Git commit sau mỗi thay đổi
   - Document selector reasoning

---

## 📞 Support

Nếu cần thêm nguồn tin blockchain:

1. Cung cấp URL trang tin
2. Kiểm tra robots.txt
3. Tôi sẽ giúp tạo config và test

---

**Status:** 📝 Document Complete  
**Last Updated:** 10/02/2026  
**Next:** Điều chỉnh selector cho Genk/ICTNews hoặc thêm nguồn mới
