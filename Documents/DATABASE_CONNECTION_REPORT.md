# 📊 Database Connection Report

**Date**: 2026-02-10  
**Environment**: Local Development

---

## ✅ Connection Status

### 1. X-Wise Local Database (Primary for News Crawler)

```
Host: 127.0.0.1:5432
Database: wise_local
User: postgres
PostgreSQL Version: 18.1
```

**Status**: ✅ **CONNECTED & READY**

**Tables**: 84 tables found

**News System**:
- ✅ `news` table exists (0 records - ready for crawler)
- ✅ `category` table exists with **17 NEWS categories**
- ✅ `attachment` table exists (for images)

**Categories Seeded**:
```
📁 NEWS (Parent)
  ├─ POLITICS - Thời sự
  ├─ WORLD - Thế giới
  ├─ BUSINESS - Kinh doanh
  ├─ ENTERTAINMENT - Giải trí
  ├─ SPORTS - Thể thao
  ├─ LAW - Pháp luật
  ├─ EDUCATION - Giáo dục
  ├─ HEALTH - Sức khỏe
  ├─ LIFESTYLE - Đời sống
  ├─ TRAVEL - Du lịch
  ├─ SCIENCE - Khoa học
  ├─ TECH - Công nghệ
  ├─ AUTO - Xe
  ├─ REALESTATE - Nhà đất
  ├─ CULTURE - Văn hóa
  ├─ OPINION - Ý kiến
  └─ CHARITY - Từ thiện
```

---

### 2. X-Core Database

```
Host: trolley.proxy.rlwy.net:11347
Database: x_core
User: postgres
PostgreSQL Version: 17.6
```

**Status**: ✅ **CONNECTED**

**Note**: This is a separate database for X-Core system (not used for news)

---

## 🎯 Ready for News Crawler

### ✅ Checklist

- [x] Database connection successful
- [x] `news` table exists
- [x] `category` table exists
- [x] `attachment` table exists
- [x] NEWS categories seeded (17 categories)
- [x] PostgreSQL 18.1 running
- [x] Redis available (127.0.0.1:6379)

### 📝 Next Steps

1. **Generate JWT Token** for crawler authentication
   ```bash
   cd wise-cms-backend
   # Create and run generate-crawler-token.ts script
   ```

2. **Setup News Crawler**
   ```bash
   cd ../news-crawler
   pip install -r requirements.txt
   playwright install chromium
   cp .env.example .env
   # Edit .env with JWT token
   ```

3. **Test Crawler**
   ```bash
   python main.py --mode once --domain vnexpress.net
   ```

4. **Verify Data**
   ```bash
   node test-db-connection.js
   # Should show news records > 0
   ```

---

## 🔧 Maintenance Scripts Created

### 1. `test-db-connection.js`
Test all database connections and verify tables

```bash
node test-db-connection.js
```

### 2. `seed-categories-v2.js`
Seed NEWS categories (already run successfully)

```bash
node seed-categories-v2.js
```

### 3. `seed-news-categories.sql`
SQL version of category seeding

```bash
psql -h 127.0.0.1 -U postgres -d wise_local -f seed-news-categories.sql
```

---

## 📊 Database Schema (Relevant Tables)

### `news` Table
```sql
CREATE TABLE news (
    id UUID PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    created_at DATE,
    reaction_count INT DEFAULT 0,
    status TEXT,
    category_code VARCHAR(100)
);
```

### `category` Table
```sql
CREATE TABLE category (
    id UUID PRIMARY KEY,
    code VARCHAR(255),
    name VARCHAR(255),
    parent_code VARCHAR(255),
    status VARCHAR(255),
    created_at DATE,
    updated_at DATE
);
```

### `attachment` Table
```sql
CREATE TABLE attachment (
    id UUID PRIMARY KEY,
    url VARCHAR(255),
    object_type VARCHAR(255),
    object_id VARCHAR(255),
    created_at DATE,
    status VARCHAR(255),
    file_name VARCHAR(255),
    extension VARCHAR(255)
);
```

---

## 🚀 System Ready

Your X-Wise CMS backend is now **READY** for the News Crawler integration!

**Database**: ✅ Connected  
**Tables**: ✅ Verified  
**Categories**: ✅ Seeded  
**Next**: Generate JWT Token & Setup Crawler

---

**Report Generated**: 2026-02-10  
**Tool**: test-db-connection.js
