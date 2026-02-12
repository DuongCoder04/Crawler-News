# CDN Upload Implementation - Complete ✅

## Tổng Quan
Đã implement tính năng upload thumbnail lên CDN 0x2labs và lưu link vào bảng `attachment`.

## Luồng Hoạt Động

```
1. Crawler lấy article với thumbnail URL
   ↓
2. Download image từ source URL
   ↓
3. Upload image lên CDN 0x2labs
   ↓
4. Nhận CDN URL response
   ↓
5. Insert news vào database
   ↓
6. Insert attachment với CDN URL vào database
```

## Files Đã Tạo/Cập Nhật

### 1. `utils/cdn_uploader.py` (NEW)
**CDN Uploader Class** với các methods:
- `download_image(image_url)` - Download image từ URL với proper headers
- `upload_to_cdn(image_url)` - Upload lên CDN
- `upload_with_retry(image_url, retries=3)` - Upload với retry logic
- `get_filename_from_url(url)` - Extract filename

**Features:**
✅ Download image với User-Agent và Referer headers
✅ Upload lên CDN với API key authentication
✅ Retry logic (3 attempts)
✅ Error handling và logging
✅ Extract filename và extension

### 2. `config/settings.py` (UPDATED)
Thêm CDN configuration:
```python
CDN_UPLOAD_URL = os.getenv('CDN_UPLOAD_URL', 'https://upload.0x2labs.com/upload')
CDN_API_KEY = os.getenv('CDN_API_KEY', '')
CDN_BUCKET = os.getenv('CDN_BUCKET', 'images')
```

### 3. `.env` (UPDATED)
Thêm CDN credentials:
```bash
CDN_UPLOAD_URL=https://upload.0x2labs.com/upload
CDN_API_KEY=Hanoimualarung@290714Vietnam
CDN_BUCKET=images
```

### 4. `.env.example` (UPDATED)
Template cho CDN config

### 5. `utils/db_client.py` (UPDATED)
**Method `create_news()` đã được update:**

```python
# Old: Embed thumbnail vào content
content = '<img src="thumbnail_url"/>' + content

# New: Upload lên CDN và lưu vào attachment table
cdn_data = cdn_uploader.upload_with_retry(thumbnail_url)
if cdn_data:
    # Insert vào attachment table
    INSERT INTO attachment (id, url, object_type, object_id, ...)
    VALUES (uuid, cdn_url, 'NEWS', news_id, ...)
```

**Attachment Record Structure:**
```python
{
    'id': 'uuid',
    'url': 'https://cdn.0x2labs.com/images/xxx.jpg',  # CDN URL
    'object_type': 'news',
    'object_id': 'news_id',
    'created_at': datetime.now(),
    'status': 'ACTIVE',
    'file_name': 'xxx.jpg',
    'extension': 'jpg'
}
```

### 6. `test_cdn_upload.py` (NEW)
Test script để verify CDN upload functionality

## CDN API Specification

### Request
```bash
curl -X POST https://upload.0x2labs.com/upload \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@image.jpg" \
  -F "bucket=images"
```

### Response (Success)
```json
{
  "success": true,
  "data": {
    "key": "1766658650748-64082ed360698098.jpg",
    "bucket": "images",
    "url": "https://cdn.0x2labs.com/images/1766658650748-64082ed360698098.jpg",
    "size": 224147,
    "mimetype": "image/jpeg"
  }
}
```

### Response (Error)
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

## Database Schema

### Bảng `attachment`
```sql
CREATE TABLE attachment (
    id UUID PRIMARY KEY,
    url VARCHAR(255),              -- CDN URL
    object_type VARCHAR(255),      -- 'news'
    object_id VARCHAR(255),        -- news.id
    created_at TIMESTAMP,
    status VARCHAR(255),           -- 'ACTIVE'
    file_name VARCHAR(255),        -- 'xxx.jpg'
    extension VARCHAR(255)         -- 'jpg'
);
```

### Bảng `news`
```sql
CREATE TABLE news (
    id UUID PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,                  -- KHÔNG có thumbnail embed
    category_code VARCHAR(255),
    status VARCHAR(255),
    created_at TIMESTAMP,
    reaction_count INTEGER
);
```

## Testing

### Test CDN Upload
```bash
cd Crawler
python test_cdn_upload.py
```

### Expected Output (Success)
```
✅ Upload successful!

CDN Data:
  - Key:      1766658650748-64082ed360698098.jpg
  - Bucket:   images
  - URL:      https://cdn.0x2labs.com/images/xxx.jpg
  - Size:     224147 bytes
  - MimeType: image/jpeg
```

### Current Issue ⚠️
**401 Unauthorized** khi upload lên CDN

**Possible Causes:**
1. API Key không đúng
2. API Key format không đúng
3. Header format không đúng
4. API endpoint đã thay đổi

**Next Steps:**
1. ✅ Verify API key với curl command
2. ✅ Check API documentation
3. ✅ Test với Postman/Insomnia
4. ✅ Update API key trong `.env` nếu cần

## Verify API Key

### Test với curl:
```bash
curl -X POST https://upload.0x2labs.com/upload \
  -H "X-API-Key: Hanoimualarung@290714Vietnam" \
  -F "file=@test.jpg" \
  -F "bucket=images"
```

### Nếu thành công:
- API key đúng → Continue với crawler
- Nếu 401 → API key sai, cần update

### Nếu thất bại:
1. Check API documentation
2. Contact 0x2labs support
3. Verify API key permissions
4. Check bucket name

## Error Handling

### Trong Code
```python
# Nếu CDN upload fail, crawler vẫn tiếp tục
try:
    cdn_data = cdn_uploader.upload_with_retry(thumbnail_url)
    if cdn_data:
        # Create attachment record
        ...
    else:
        logger.warning("Failed to upload thumbnail to CDN")
        # Continue without thumbnail
except Exception as e:
    logger.error(f"Error uploading thumbnail: {e}")
    # Continue without thumbnail - don't fail the whole operation
```

### Behavior
- ✅ News vẫn được tạo nếu CDN upload fail
- ✅ Attachment chỉ được tạo nếu CDN upload success
- ✅ Không block crawler nếu CDN có vấn đề
- ✅ Log errors để debug

## Advantages

### So với Embed vào Content
✅ Quản lý attachment độc lập
✅ Có metadata đầy đủ (size, mimetype, filename)
✅ Dễ thay đổi/xóa thumbnail
✅ Chuẩn database design
✅ Frontend có thể load thumbnail riêng
✅ CDN caching và performance tốt hơn
✅ Không phụ thuộc vào source website

### CDN Benefits
✅ Fast loading với CDN
✅ Không lo source image bị xóa
✅ Bandwidth tiết kiệm
✅ Image optimization
✅ Global distribution

## Frontend Integration

### Query News với Thumbnail
```typescript
// Option 1: Query riêng attachment
const thumbnail = await attachmentRepository.findOne({
  where: { 
    object_type: 'NEWS',
    object_id: newsId,
    status: 'ACTIVE'
  }
});

// Option 2: Join query
const news = await newsRepository
  .createQueryBuilder('news')
  .leftJoinAndSelect('attachment', 'att', 'att.object_id = news.id AND att.object_type = :type', { type: 'news' })
  .where('news.id = :id', { id: newsId })
  .getOne();
```

### Display Thumbnail
```html
<img src="{{ thumbnail.url }}" alt="{{ news.title }}" />
```

## Next Steps

### 1. Verify API Key ⚠️ URGENT
```bash
# Test với curl command
curl -X POST https://upload.0x2labs.com/upload \
  -H "X-API-Key: YOUR_ACTUAL_API_KEY" \
  -F "file=@test.jpg" \
  -F "bucket=images"
```

### 2. Update API Key (Nếu Cần)
```bash
# Update trong .env
CDN_API_KEY=your_correct_api_key_here
```

### 3. Test Lại
```bash
python test_cdn_upload.py
```

### 4. Run Crawler
```bash
python main.py --mode once --domain vnexpress
```

### 5. Verify Database
```sql
-- Check attachments
SELECT id, url, object_type, object_id, file_name 
FROM attachment 
WHERE object_type = 'news' 
ORDER BY created_at DESC 
LIMIT 10;

-- Check news without embedded thumbnail
SELECT id, title, LEFT(content, 200) 
FROM news 
ORDER BY created_at DESC 
LIMIT 5;
```

## Rollback Plan

Nếu CDN không hoạt động, có thể rollback về embed thumbnail:

```python
# In db_client.py - create_news()
# Comment out CDN upload code
# Uncomment old embed code:
if article_data.get('thumbnail'):
    thumbnail_html = f'<img src="{article_data["thumbnail"]}"/><br/>'
    content = thumbnail_html + content
```

## Kết Luận

✅ **Implementation Complete** - Code đã sẵn sàng
⚠️ **API Key Issue** - Cần verify API key
🔄 **Ready to Test** - Sau khi fix API key

**Bạn cần làm gì tiếp theo:**
1. Verify API key với curl command
2. Update API key trong `.env` nếu cần
3. Run `python test_cdn_upload.py` để test
4. Nếu success → Run crawler
5. Nếu vẫn fail → Check với 0x2labs support

Bạn có API key chính xác không? Hoặc cần tôi giúp gì thêm? 🤔
