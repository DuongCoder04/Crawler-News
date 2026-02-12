# Cải Tiến Content Cleaning

## Tổng Quan

Đã cập nhật `ContentCleaner` để loại bỏ video và chuẩn hóa định dạng nội dung tin tức trước khi lưu vào database.

## Các Tính Năng Mới

### 1. Loại Bỏ Video

#### Video Tags
Tự động loại bỏ các thẻ HTML liên quan đến video:
- `<video>` - HTML5 video tag
- `<audio>` - HTML5 audio tag
- `<source>` - Video/audio source
- `<track>` - Video subtitles/captions
- `<iframe>` - Embedded videos (YouTube, Vimeo, etc.)
- `<embed>` - Flash/plugin embeds
- `<object>` - Object embeds

#### Video Containers
Tự động phát hiện và loại bỏ các container chứa video dựa trên class/id:
- `video-*` - Video containers
- `player-*` - Media players
- `media-player` - Media player wrappers
- `youtube` - YouTube embeds
- `vimeo` - Vimeo embeds
- `dailymotion` - Dailymotion embeds

### 2. Chuẩn Hóa Font và Styling

#### Loại Bỏ Inline Styles
Tự động loại bỏ các style inline ảnh hưởng đến hiển thị:
- `font-family` - Loại font chữ
- `font-size` - Cỡ chữ
- `line-height` - Khoảng cách dòng
- `color` - Màu chữ

#### Loại Bỏ Font Tags
- Loại bỏ thẻ `<font>` cũ
- Loại bỏ attributes: `size`, `color`, `face`

#### Giữ Lại Styles Quan Trọng
Chỉ giữ lại các style cần thiết cho layout:
- `text-align` - Căn lề (left, center, right, justify)

### 3. Làm Sạch Nội Dung Khác

Vẫn giữ nguyên các chức năng làm sạch cũ:
- Loại bỏ scripts và styles
- Loại bỏ quảng cáo
- Loại bỏ comments HTML
- Loại bỏ paragraphs rỗng
- Chuẩn hóa khoảng trắng

## Cấu Hình

### File: `Crawler/utils/content_cleaner.py`

```python
class ContentCleaner:
    def __init__(self):
        # Unwanted tags (bao gồm video)
        self.unwanted_tags = [
            'script', 'style', 'iframe', 'noscript',
            'embed', 'object', 'applet', 'video', 'audio',
            'source', 'track'
        ]
        
        # Cấu hình font chuẩn (có thể tùy chỉnh)
        self.standard_font = 'Arial, sans-serif'
        self.standard_font_size = '16px'
        self.standard_line_height = '1.6'
```

## Cách Sử Dụng

### Tự Động
Content cleaner được tích hợp sẵn trong crawler pipeline:

```python
# Trong base_crawler.py
def crawl_article(self, url: str) -> Optional[Dict]:
    # ... fetch và extract data ...
    
    # Clean content tự động
    article_data['content'] = self.content_cleaner.clean(
        article_data['content']
    )
    
    return article_data
```

### Thủ Công
Có thể sử dụng trực tiếp:

```python
from utils.content_cleaner import ContentCleaner

cleaner = ContentCleaner()
cleaned_html = cleaner.clean(raw_html)
```

## Testing

### Chạy Test Suite

```bash
cd Crawler
python test_content_cleaner.py
```

### Test Cases

1. **Test Video Removal** - Loại bỏ video tags
2. **Test Video Container Removal** - Loại bỏ video containers
3. **Test Font Normalization** - Chuẩn hóa font và styling
4. **Test Complete Cleaning** - Test tổng hợp

### Kết Quả Mong Đợi

```
✓ Video removed: True
✓ Iframe removed: True
✓ Script removed: True
✓ Advertisement removed: True
✓ Font-family removed: True
✓ Font-size removed: True
✓ Text-align preserved: True
✓ Empty paragraphs removed: True
```

## Ví Dụ

### Input HTML

```html
<div class="article-content">
    <h1 style="font-family: Arial; font-size: 32px;">Tiêu đề</h1>
    
    <p style="font-size: 16px;">Nội dung bài viết.</p>
    
    <video controls>
        <source src="video.mp4" type="video/mp4">
    </video>
    
    <iframe src="https://www.youtube.com/embed/xyz"></iframe>
    
    <p style="text-align: center; font-size: 14px;">Đoạn căn giữa</p>
</div>
```

### Output HTML

```html
<div class="article-content">
    <h1>Tiêu đề</h1>
    
    <p>Nội dung bài viết.</p>
    
    <p style="text-align: center">Đoạn căn giữa</p>
</div>
```

## Lợi Ích

### 1. Giảm Kích Thước Database
- Loại bỏ video embeds giảm đáng kể kích thước content
- Loại bỏ inline styles giảm dung lượng lưu trữ

### 2. Hiển Thị Đồng Nhất
- Font và cỡ chữ được kiểm soát bởi CSS của frontend
- Không bị ảnh hưởng bởi styling từ nguồn gốc

### 3. Tránh Lỗi
- Loại bỏ scripts và iframes tránh lỗi bảo mật
- Loại bỏ embeds tránh lỗi CORS và mixed content

### 4. Tối Ưu Performance
- Content nhẹ hơn, load nhanh hơn
- Không cần load external video players

### 5. Tuân Thủ Bản Quyền
- Không lưu trữ video từ nguồn khác
- Chỉ lưu nội dung text và hình ảnh

## Tùy Chỉnh

### Thêm Video Patterns

Nếu cần loại bỏ thêm video containers:

```python
# Trong content_cleaner.py, method clean()
video_patterns = [
    r'video[-_]?',
    r'player[-_]?',
    r'media[-_]?player',
    r'youtube',
    r'vimeo',
    r'dailymotion',
    r'tiktok',  # Thêm mới
    r'facebook[-_]?video'  # Thêm mới
]
```

### Giữ Lại Thêm Styles

Nếu cần giữ lại thêm styles:

```python
# Trong _normalize_styling(), phần normalize paragraphs
important_styles = []
if 'text-align' in style.lower():
    # ... existing code ...
if 'margin' in style.lower():  # Thêm mới
    margin_match = re.search(r'margin:\s*([^;]+)', style, re.IGNORECASE)
    if margin_match:
        important_styles.append(f'margin: {margin_match.group(1).strip()}')
```

### Cấu Hình Font Chuẩn

Thay đổi font mặc định:

```python
def __init__(self):
    # Cấu hình font và cỡ chữ chuẩn
    self.standard_font = 'Roboto, sans-serif'  # Thay đổi
    self.standard_font_size = '18px'  # Thay đổi
    self.standard_line_height = '1.8'  # Thay đổi
```

## Lưu Ý

1. **BeautifulSoup Parser**: Sử dụng `lxml` parser cho hiệu suất tốt nhất
2. **HTML Wrapper**: Output sẽ có `<html><body>` wrapper, có thể strip nếu cần
3. **Text-align**: Chỉ giữ lại text-align, các styles khác bị loại bỏ
4. **Video Links**: Chỉ loại bỏ embeds, không loại bỏ text links đến video

## Troubleshooting

### Video Vẫn Còn

Kiểm tra xem video có nằm trong container với class/id đặc biệt không:

```python
# Thêm pattern vào video_patterns
video_patterns.append(r'custom[-_]?video[-_]?class')
```

### Styles Quan Trọng Bị Mất

Thêm vào danh sách important_styles:

```python
# Trong _normalize_styling()
if 'your-style' in style.lower():
    important_styles.append(...)
```

### Performance Issues

Nếu xử lý chậm với HTML lớn:

```python
# Sử dụng html.parser thay vì lxml
soup = BeautifulSoup(html, 'html.parser')
```

## Changelog

### Version 2.0 (2024-02-12)
- ✅ Thêm loại bỏ video tags (video, audio, source, track)
- ✅ Thêm loại bỏ video containers (class/id patterns)
- ✅ Thêm chuẩn hóa font và styling
- ✅ Giữ lại text-align cho layout
- ✅ Thêm test suite đầy đủ

### Version 1.0 (Previous)
- Loại bỏ scripts, styles, iframes
- Loại bỏ quảng cáo
- Loại bỏ comments và empty paragraphs
- Chuẩn hóa khoảng trắng

## Liên Hệ

Nếu có vấn đề hoặc đề xuất cải tiến, vui lòng tạo issue hoặc pull request.
