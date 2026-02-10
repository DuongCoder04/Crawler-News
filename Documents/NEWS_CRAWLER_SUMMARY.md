# 📋 Tóm Tắt: News Crawler cho CMS X-Wise

## ✅ Điều Chỉnh Theo Yêu Cầu

### Không Sửa Database Schema

Crawler đã được thiết kế để **SỬ DỤNG SCHEMA HIỆN TẠI** của CMS X-Wise, không thêm/sửa bất kỳ trường nào trong database.

---

## 🔑 Giải Pháp Duplicate Check

### Sử dụng Redis Cache

Thay vì thêm trường `source_url` vào database, crawler sử dụng Redis để track:

```
Key: crawler:article:<md5_hash_of_url>
Value: news_id (UUID từ X-Wise)
TTL: 90 days
```

**Ưu điểm:**
- ✅ Không cần sửa database
- ✅ Fast lookup với O(1) complexity
- ✅ TTL tự động cleanup
- ✅ Có thể scale với Redis Cluster

**Trade-off:**
- ⚠️ Nếu Redis bị clear, có thể crawl lại (acceptable)
- ⚠️ Không query được từ database (nhưng có thể trace qua HTML comment)

---

## 📊 Traceability (Optional)

Nếu cần trace nguồn bài viết, crawler sẽ embed thông tin vào cuối `content`:

```html
<!-- Source: VnExpress | URL: https://vnexpress.net/article-123.html -->
```

Điều này cho phép:
- Biết bài viết từ nguồn nào
- Không duplicate nếu crawl lại
- Không ảnh hưởng hiển thị (HTML comment)

---

## 🔧 Thay Đổi Cần Thiết Trên X-Wise Backend

### 1. Seed Categories (Bắt Buộc)

Chạy SQL để tạo categories cho NEWS:

```sql
-- File: wise-cms-backend/migrations/seed-news-categories.sql

INSERT INTO category (id, code, name, parent_code, status, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'NEWS', 'Tin tức', NULL, 'ACTIVE', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

INSERT INTO category (id, code, name, parent_code, status, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'POLITICS', 'Thời sự', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'WORLD', 'Thế giới', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'BUSINESS', 'Kinh doanh', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'ENTERTAINMENT', 'Giải trí', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'SPORTS', 'Thể thao', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'LAW', 'Pháp luật', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'EDUCATION', 'Giáo dục', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'HEALTH', 'Sức khỏe', 'NEWS', 'ACTIVE', NOW(), NOW'),
  (gen_random_uuid(), 'LIFESTYLE', 'Đời sống', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'TRAVEL', 'Du lịch', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'SCIENCE', 'Khoa học', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'TECH', 'Công nghệ', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'AUTO', 'Xe', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'REALESTATE', 'Nhà đất', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'CULTURE', 'Văn hóa', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'OPINION', 'Ý kiến', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'CHARITY', 'Từ thiện', 'NEWS', 'ACTIVE', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;
```

### 2. Generate JWT Token (Bắt Buộc)

Tạo service account token cho crawler:

```typescript
// File: wise-cms-backend/scripts/generate-crawler-token.ts

import { NestFactory } from '@nestjs/core';
import { AppModule } from '../src/app.module';
import { JwtService } from '@nestjs/jwt';

async function bootstrap() {
  const app = await NestFactory.createApplicationContext(AppModule);
  const jwtService = app.get(JwtService);

  const payload = {
    sub: 'crawler-service',
    type: 'service',
    permissions: ['news:create', 'attachment:upload']
  };

  // Token expire sau 1 năm
  const token = jwtService.sign(payload, { expiresIn: '365d' });
  
  console.log('='.repeat(60));
  console.log('Crawler Service Token:');
  console.log(token);
  console.log('='.repeat(60));
  console.log('Add this to crawler .env file:');
  console.log(`XWISE_JWT_TOKEN=${token}`);
  console.log('='.repeat(60));

  await app.close();
}

bootstrap();
```

Chạy:
```bash
cd wise-cms-backend
npm run ts-node scripts/generate-crawler-token.ts
```

### 3. API Endpoints (Không Cần Thay Đổi)

Crawler sử dụng API hiện có:
- ✅ `POST /cms/wise/news` - Tạo tin tức
- ✅ `POST /cms/wise/attachment/upload` - Upload ảnh
- ✅ `GET /cms/wise/categories/by-parent/NEWS` - Lấy categories

**Không cần thêm endpoint mới!**

---

## 🚀 Setup Crawler

### 1. Cài Đặt

```bash
# Clone repository
git clone <repository-url>
cd news-crawler

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright
playwright install chromium
```

### 2. Cấu Hình

```bash
# Copy .env.example
cp .env.example .env

# Chỉnh sửa .env
nano .env
```

**Quan trọng**: Cần cấu hình:
- `XWISE_JWT_TOKEN` - Token từ bước 2 ở trên
- `REDIS_HOST`, `REDIS_PORT` - Redis connection (có thể dùng Redis hiện tại của X-Wise)

### 3. Test

```bash
# Test crawl VnExpress
python main.py --mode once --domain vnexpress.net

# Kiểm tra database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
  -c "SELECT id, title, category_code, created_at FROM news ORDER BY created_at DESC LIMIT 10;"

# Kiểm tra Redis cache
redis-cli
> KEYS crawler:article:*
```

### 4. Production

```bash
# Chạy với scheduler
python main.py --mode scheduler

# Hoặc dùng Docker
docker-compose up -d
```

---

## 📁 Files Đã Tạo

1. **NEWS_CRAWLER_SYSTEM_DESIGN.md** - Tài liệu kiến trúc và code chi tiết
2. **NEWS_CRAWLER_README.md** - Hướng dẫn sử dụng
3. **NEWS_CRAWLER_XWISE_ADJUSTMENTS.md** - Các thay đổi cần thiết cho X-Wise
4. **NEWS_CRAWLER_REQUIREMENTS.txt** - Python dependencies
5. **NEWS_CRAWLER_ENV_EXAMPLE.txt** - Environment variables template
6. **NEWS_CRAWLER_TUOITRE_CONFIG.json** - Config mẫu cho Tuổi Trẻ
7. **NEWS_CRAWLER_DANTRI_CONFIG.json** - Config mẫu cho Dân Trí
8. **NEWS_CRAWLER_DOCKERFILE.txt** - Docker configuration
9. **NEWS_CRAWLER_DOCKER_COMPOSE.yml** - Docker Compose setup
10. **NEWS_CRAWLER_SUMMARY.md** - File này

---

## ✨ Highlights

### Không Cần Sửa Database
- ✅ Sử dụng schema hiện tại
- ✅ Redis cache cho duplicate check
- ✅ HTML comment cho traceability

### Không Cần Thêm API
- ✅ Sử dụng endpoints hiện có
- ✅ Không cần backend code changes
- ✅ Chỉ cần JWT token

### Chỉ Cần Setup
- ✅ Seed categories (1 lần)
- ✅ Generate JWT token (1 lần)
- ✅ Setup Redis (nếu chưa có)
- ✅ Deploy crawler

---

## 🎯 Next Steps

1. **Review tài liệu** trong `NEWS_CRAWLER_SYSTEM_DESIGN.md`
2. **Seed categories** vào database X-Wise
3. **Generate JWT token** cho crawler
4. **Setup crawler** theo `NEWS_CRAWLER_README.md`
5. **Test với VnExpress** trước
6. **Monitor logs** và adjust config
7. **Add thêm domains** khi stable

---

## 📞 Support

Nếu có vấn đề:
1. Xem logs: `logs/crawler.log`
2. Check Redis: `redis-cli KEYS crawler:*`
3. Verify API: Test với Postman
4. Xem troubleshooting trong `NEWS_CRAWLER_SYSTEM_DESIGN.md`

---

**Version**: 1.0.0 (No Database Changes)  
**Last Updated**: 2026-02-10  
**Author**: Kiro AI Assistant
