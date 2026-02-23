# 🔧 Điều Chỉnh Cần Thiết Cho CMS X-Wise

Tài liệu này liệt kê các thay đổi cần thực hiện trên hệ thống CMS X-Wise để tích hợp hoàn chỉnh với News Crawler.

**LƯU Ý QUAN TRỌNG**: Crawler sẽ SỬ DỤNG SCHEMA HIỆN TẠI, KHÔNG thêm/sửa trường trong database. Duplicate check sẽ dùng Redis cache.

---

## 📊 1. Chiến Lược Duplicate Check (Không Sửa Database)

### Sử dụng Redis Cache

Vì không thêm trường `source_url` vào database, crawler sẽ:

1. **Lưu mapping trong Redis**:
   ```
   Key: crawler:article:<md5_hash_of_url>
   Value: news_id (UUID từ X-Wise)
   TTL: 90 days
   ```

2. **Check duplicate trước khi crawl**:
   - Hash URL nguồn
   - Check trong Redis cache
   - Nếu tồn tại → Skip
   - Nếu không → Crawl và tạo mới

3. **Embed source info trong content** (optional, cho traceability):
   ```html
   <!-- Source: VnExpress | URL: https://vnexpress.net/article-123.html -->
   ```

### Ưu điểm:
- ✅ Không cần sửa database
- ✅ Fast lookup với Redis
- ✅ TTL tự động cleanup
- ✅ Có thể trace nguồn qua HTML comment

### Nhược điểm:
- ⚠️ Nếu Redis bị clear, sẽ crawl lại (có thể duplicate)
- ⚠️ Không query được từ database

---

## 🔌 2. API Endpoints (Không Cần Thay Đổi)

Crawler sẽ sử dụng API hiện tại, KHÔNG cần thêm endpoint mới:

### A. Tạo Tin Tức (Đã Có)
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

### B. Upload Ảnh (Đã Có)
```http
POST /cms/wise/attachment/upload
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

file: <binary>
```

### C. Lấy Categories (Đã Có)
```http
GET /cms/wise/categories/by-parent/NEWS
Authorization: Bearer <JWT_TOKEN>
```

**Kết luận**: KHÔNG CẦN thay đổi backend API!

---

## 📂 3. Categories Setup (Cần Thiết)

### Tạo Categories Cho News

```sql
-- File: wise-cms-backend/migrations/seed-news-categories.sql

-- Tạo parent category
INSERT INTO category (id, code, name, parent_code, status, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'NEWS', 'Tin tức', NULL, 'ACTIVE', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

-- Tạo sub-categories
INSERT INTO category (id, code, name, parent_code, status, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'POLITICS', 'Thời sự', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'WORLD', 'Thế giới', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'BUSINESS', 'Kinh doanh', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'ENTERTAINMENT', 'Giải trí', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'SPORTS', 'Thể thao', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'LAW', 'Pháp luật', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'EDUCATION', 'Giáo dục', 'NEWS', 'ACTIVE', NOW(), NOW()),
  (gen_random_uuid(), 'HEALTH', 'Sức khỏe', 'NEWS', 'ACTIVE', NOW(), NOW()),
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

### Script Chạy Migration

```bash
# File: wise-cms-backend/scripts/run-news-migrations.sh

#!/bin/bash

# Load environment variables
source .env

# Run migrations
psql -h $DB_WISE_HOST -p $DB_WISE_PORT -U $DB_WISE_USER -d $DB_WISE_NAME << EOF
\i migrations/add-news-source-fields.sql
\i migrations/seed-news-categories.sql
EOF

echo "Migrations completed successfully!"
```

---

## 🔐 4. Authentication & Authorization (Cần Thiết)

### A. Tạo Service Account cho Crawler

```typescript
// File: wise-cms-backend/src/auth/dto/create-service-account.dto.ts

export class CreateServiceAccountDto {
  @IsString()
  name: string;

  @IsString()
  description: string;

  @IsArray()
  permissions: string[];
}
```

### B. Generate Long-lived Token

```typescript
// File: wise-cms-backend/src/auth/services/auth.service.ts

async generateServiceToken(serviceAccountId: string): Promise<string> {
  const payload = {
    sub: serviceAccountId,
    type: 'service',
    permissions: ['news:create', 'attachment:upload']
  };

  // Token không expire hoặc expire sau 1 năm
  return this.jwtService.sign(payload, {
    expiresIn: '365d'
  });
}
```

### C. Script Tạo Token

```bash
# File: wise-cms-backend/scripts/generate-crawler-token.ts

import { NestFactory } from '@nestjs/core';
import { AppModule } from '../src/app.module';
import { AuthService } from '../src/auth/services/auth.service';

async function bootstrap() {
  const app = await NestFactory.createApplicationContext(AppModule);
  const authService = app.get(AuthService);

  const token = await authService.generateServiceToken('crawler-service');
  
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

Chạy script:
```bash
cd wise-cms-backend
npm run ts-node scripts/generate-crawler-token.ts
```

---

## 📝 5. Logging & Monitoring (Optional - Không Bắt Buộc)

Crawler tự quản lý logs trong file `logs/crawler.log`. Nếu muốn centralized logging:

### Option: Log vào file và monitor bằng external tools
- Sử dụng ELK Stack (Elasticsearch, Logstash, Kibana)
- Hoặc Grafana Loki
- Hoặc CloudWatch Logs (AWS)

**Không cần thêm table hoặc API endpoint mới trong X-Wise backend.**

---

## 🚀 6. Deployment Checklist

### Backend Changes (Tối Thiểu)

- [ ] Seed categories cho NEWS (nếu chưa có)
- [ ] Tạo service account và generate JWT token cho crawler
- [ ] Verify API endpoints hiện tại hoạt động đúng
- [ ] Setup Redis cho crawler (có thể dùng Redis hiện tại hoặc riêng)

### Crawler Setup

- [ ] Clone crawler repository
- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Cài đặt Playwright (`playwright install chromium`)
- [ ] Cấu hình `.env` với JWT token và Redis
- [ ] Test crawl một domain (`python main.py --mode once --domain vnexpress.net`)
- [ ] Verify data trong database X-Wise
- [ ] Verify Redis cache hoạt động
- [ ] Setup scheduler (`python main.py --mode scheduler`)
- [ ] Configure monitoring (logs)
- [ ] Deploy crawler service (Docker hoặc systemd)

### Monitoring

- [ ] Setup log rotation (loguru tự động)
- [ ] Configure alerts (Slack/Email - optional)
- [ ] Monitor error rates trong logs
- [ ] Track duplicate rates trong Redis
- [ ] Monitor Redis memory usage

---

## 📊 7. Testing Checklist

### Unit Tests

```bash
# Backend
cd wise-cms-backend
npm run test

# Crawler
cd news-crawler
pytest tests/
```

### Integration Tests

```bash
# Test API endpoints
curl -X POST https://backend-dev-cms-staging.up.railway.app/cms/wise/news \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "content": "<p>Test content</p>",
    "category_code": "TECH",
    "source_url": "https://test.com/article-123",
    "source_name": "Test Source"
  }'

# Test duplicate check
curl -X GET "https://backend-dev-cms-staging.up.railway.app/cms/wise/news/check-duplicate?source_url=https://test.com/article-123" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### End-to-End Test

```bash
# Chạy crawler test
python main.py --mode once --domain vnexpress.net

# Kiểm tra database (xem tin tức mới tạo)
psql -h $DB_WISE_HOST -U $DB_WISE_USER -d $DB_WISE_NAME -c "SELECT id, title, category_code, created_at FROM news ORDER BY created_at DESC LIMIT 10;"

# Kiểm tra Redis cache
redis-cli
> KEYS crawler:article:*
> GET crawler:article:<hash>
```

---

## 🔄 8. Rollback Plan

Nếu có vấn đề, rollback theo thứ tự:

### 1. Stop Crawler
```bash
# Stop scheduler
pkill -f "python main.py"

# Or stop Docker container
docker stop xwise-news-crawler
```

### 2. Clear Redis Cache (nếu cần)
```bash
# Connect to Redis
redis-cli

# Clear crawler cache
KEYS crawler:article:*
# Hoặc flush all (cẩn thận!)
# FLUSHDB
```

### 3. Rollback Backend Code (nếu có thay đổi)
```bash
cd wise-cms-backend
git revert <commit-hash>
npm run build
pm2 restart all
```

---

## 📞 Support & Contact

Nếu gặp vấn đề trong quá trình triển khai:

1. Kiểm tra logs: `logs/crawler.log`
2. Xem database migrations: `migrations/`
3. Test API endpoints với Postman
4. Liên hệ team X-Wise

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-10  
**Author**: Kiro AI Assistant
