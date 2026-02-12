# Thumbnail Storage - Current Implementation & Options

## Hiện Tại: Thumbnail Được Lưu Như Thế Nào?

### ❌ KHÔNG lưu vào bảng `attachment`

Thumbnail hiện tại được **embed trực tiếp vào HTML content** của bảng `news`:

```python
# In db_client.py - create_news()
if article_data.get('thumbnail'):
    thumbnail_html = f'<img src="{article_data["thumbnail"]}" alt="thumbnail" style="max-width:100%"/><br/>'
    content = thumbnail_html + content
```

### Kết Quả Trong Database

**Bảng `news`:**
```sql
id: "uuid-123"
title: "Tiêu đề bài viết"
content: '<img src="https://example.com/image.jpg" alt="thumbnail" style="max-width:100%"/><br/>
          <p>Nội dung bài viết...</p>
          <!-- Source: VnExpress | URL: https://vnexpress.net/... -->'
category_code: "NEWS_TECH"
status: "ACTIVE"
```

**Bảng `attachment`:**
- Không có record nào được tạo

---

## Schema Bảng Attachment

```typescript
@Entity('attachment')
export class Attachment {
  id: string;                    // UUID (PK)
  url?: string;                  // URL của file/image
  object_type?: string;          // Loại object (e.g., 'NEWS', 'BLOG')
  object_id?: string;            // ID của object (e.g., news_id)
  created_at?: Date;             // Ngày tạo
  status: string;                // Status (e.g., 'ACTIVE')
  file_name?: string;            // Tên file
  extension?: string;            // Extension (e.g., 'jpg', 'png')
}
```

---

## Option 1: Giữ Nguyên (Embed vào Content) ✅ ĐANG DÙNG

### Ưu Điểm
✅ Đơn giản, không cần thêm logic phức tạp
✅ Không cần quan tâm foreign key constraints
✅ Thumbnail luôn đi kèm với content
✅ Dễ migrate và backup

### Nhược Điểm
❌ Không thể query riêng thumbnail
❌ Không thể quản lý attachment độc lập
❌ Khó thay đổi thumbnail sau này
❌ Không có metadata về file (size, extension, etc.)

### Khi Nào Nên Dùng
- Crawler đơn giản, chỉ cần hiển thị thumbnail
- Không cần quản lý attachment riêng
- Không cần thay đổi thumbnail sau khi crawl

---

## Option 2: Lưu Vào Bảng Attachment 🆕 RECOMMENDED

### Cách Hoạt Động

1. **Crawl article** → Lấy thumbnail URL
2. **Tạo news record** → Lưu vào bảng `news`
3. **Tạo attachment record** → Lưu thumbnail vào bảng `attachment`
   - `object_type` = 'NEWS'
   - `object_id` = news_id
   - `url` = thumbnail_url
   - `status` = 'ACTIVE'

### Implementation

```python
def create_news_with_attachment(self, article_data: Dict) -> bool:
    """
    Tạo tin tức mới và lưu thumbnail vào attachment table
    """
    conn = None
    try:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 1. Create news record
        news_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO news (id, title, content, status, category_code, created_at, reaction_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            news_id,
            article_data['title'][:500],
            article_data['content'],  # Content KHÔNG có thumbnail
            'ACTIVE',
            article_data['category_code'],
            datetime.now(),
            0
        ))
        
        # 2. Create attachment record for thumbnail
        if article_data.get('thumbnail'):
            attachment_id = str(uuid.uuid4())
            thumbnail_url = article_data['thumbnail']
            
            # Extract file info from URL
            file_name = thumbnail_url.split('/')[-1]
            extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
            
            cursor.execute("""
                INSERT INTO attachment (id, url, object_type, object_id, created_at, status, file_name, extension)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                attachment_id,
                thumbnail_url,
                'NEWS',
                news_id,
                datetime.now(),
                'ACTIVE',
                file_name,
                extension
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating news with attachment: {e}")
        return False
    finally:
        if conn:
            conn.close()
```

### Ưu Điểm
✅ Quản lý attachment độc lập
✅ Có thể query thumbnail riêng
✅ Có metadata đầy đủ (file_name, extension)
✅ Dễ thay đổi/xóa thumbnail
✅ Chuẩn database design
✅ Frontend có thể load thumbnail riêng

### Nhược Điểm
❌ Phức tạp hơn một chút
❌ Cần 2 INSERT queries
❌ Cần transaction để đảm bảo consistency

### Khi Nào Nên Dùng
- Cần quản lý attachment riêng biệt
- Cần thay đổi thumbnail sau này
- Cần metadata về file
- Hệ thống lớn, cần chuẩn database design

---

## Option 3: Hybrid Approach (Cả Hai) 🔄

### Cách Hoạt Động
1. Lưu thumbnail vào bảng `attachment` (primary)
2. Embed thumbnail vào content (fallback/cache)

### Ưu Điểm
✅ Có cả 2 cách truy cập
✅ Fallback nếu attachment bị xóa
✅ Tương thích với cả frontend cũ và mới

### Nhược Điểm
❌ Duplicate data
❌ Phức tạp nhất
❌ Cần sync khi update

---

## Recommendation 💡

### Nếu Hệ Thống Đơn Giản
→ **Giữ nguyên Option 1** (embed vào content)

### Nếu Hệ Thống Chuyên Nghiệp
→ **Chuyển sang Option 2** (lưu vào attachment table)

### Nếu Đang Migrate
→ **Dùng Option 3** tạm thời, sau đó chuyển sang Option 2

---

## Migration Plan (Nếu Chuyển Sang Option 2)

### Bước 1: Update db_client.py
```python
# Thêm method mới
def create_news_with_attachment(self, article_data: Dict) -> bool:
    # Implementation như trên
    pass
```

### Bước 2: Update base_crawler.py
```python
# Thay đổi từ:
success = self.db_client.create_news(article_data)

# Sang:
success = self.db_client.create_news_with_attachment(article_data)
```

### Bước 3: Test
```bash
python main.py --mode once --domain vnexpress
```

### Bước 4: Verify Database
```sql
-- Check news
SELECT id, title, LEFT(content, 100) FROM news ORDER BY created_at DESC LIMIT 5;

-- Check attachments
SELECT id, url, object_type, object_id, file_name FROM attachment WHERE object_type = 'news' ORDER BY created_at DESC LIMIT 5;
```

### Bước 5: Update Frontend (Nếu Cần)
Frontend cần query attachment để lấy thumbnail:
```typescript
// Get news with thumbnail
const news = await newsRepository.findOne({
  where: { id: newsId },
  relations: ['attachments'] // Nếu có relation
});

// Hoặc query riêng
const thumbnail = await attachmentRepository.findOne({
  where: { 
    object_type: 'NEWS',
    object_id: newsId 
  }
});
```

---

## Kết Luận

**Hiện tại:** Thumbnail được embed vào HTML content (Option 1)

**Nên chuyển sang:** Lưu vào bảng attachment (Option 2) nếu:
- Cần quản lý attachment chuyên nghiệp
- Cần thay đổi thumbnail sau này
- Cần metadata về file

Bạn muốn tôi implement Option 2 không? 🤔
