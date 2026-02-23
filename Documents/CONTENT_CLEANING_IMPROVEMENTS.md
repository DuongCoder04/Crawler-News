# Content Cleaning Improvements

## Tổng quan
Đã cải thiện content cleaner để xử lý nội dung từ các nguồn tin, đặc biệt là Dân Trí.

## Các cải thiện chính

### 1. Định dạng nội dung
- ✅ Loại bỏ khoảng trống lớn giữa các đoạn văn
- ✅ Loại bỏ ngắt dòng dài (nhiều hơn 2 line breaks)
- ✅ Loại bỏ &nbsp; và các ký tự whitespace không cần thiết
- ✅ Chuẩn hóa khoảng trắng trong paragraphs

### 2. Xử lý đặc biệt cho Dân Trí
- ✅ Loại bỏ avatar tác giả (ảnh nhỏ 24x24, 36x36)
- ✅ Loại bỏ tên tác giả và link đến trang tác giả
- ✅ Loại bỏ thời gian đăng bài
- ✅ Loại bỏ "(Dân trí) -" prefix ở đầu nội dung

### 3. Xử lý ảnh
- ✅ Convert lazy loading images (data-src, data-original) thành src thực
- ✅ Loại bỏ ảnh không có src hợp lệ
- ✅ Loại bỏ ảnh avatar (ảnh nhỏ)
- ✅ Giữ lại ảnh nội dung chính

### 4. Loại bỏ elements không mong muốn
- ✅ Video và audio elements
- ✅ Quảng cáo và banner
- ✅ Social share buttons
- ✅ Related articles
- ✅ Comments section

## Cấu trúc code

### ContentCleaner class
```python
def clean(self, html: str, source_name: str = '') -> str
```
- Nhận thêm parameter `source_name` để xử lý đặc biệt cho từng nguồn
- Gọi `_clean_dantri_specific()` nếu là Dân Trí

### Methods mới
1. `_clean_dantri_specific(soup)` - Xử lý đặc biệt cho Dân Trí
2. `_fix_images(soup)` - Fix lazy loading images
3. `_remove_empty_elements(soup)` - Loại bỏ elements rỗng

## Kết quả

### Trước khi cải thiện
- Nội dung có nhiều khoảng trống lớn
- Xuất hiện avatar tác giả, tên, thời gian
- Có "(Dân trí) -" ở đầu nội dung
- Ảnh không hiển thị (lazy loading)

### Sau khi cải thiện
- Nội dung gọn gàng, dễ đọc
- Không còn thông tin tác giả
- Không còn "(Dân trí) -" prefix
- Ảnh hiển thị bình thường

## Test results

### Test với URL mẫu
```
URL: https://dantri.com.vn/thoi-su/ha-noi-khong-xin-tien-khi-xay-dung-luat-thu-do-20260223082458443.htm

Original length: 8818 chars
Cleaned length: 5732 chars
Reduction: 35.0%

✓ '(Dân trí)' prefix removed
✓ Found 2 images (content images only, avatar removed)
✓ No excessive line breaks
```

## Files thay đổi

1. `utils/content_cleaner.py` - Cải thiện logic cleaning
2. `engine/base_crawler.py` - Truyền source_name vào cleaner
3. `config/domains/dantri.json` - Thêm remove_elements

## Sử dụng

Crawler tự động áp dụng các cải thiện này khi crawl:

```bash
# Crawl Dantri
python main.py --mode once --domain dantri.com.vn

# Crawl tất cả domains
python main.py --mode once
```

## Ghi chú

- Content cleaning được áp dụng cho tất cả domains
- Xử lý đặc biệt chỉ áp dụng cho Dân Trí (có thể mở rộng cho các nguồn khác)
- Ảnh thumbnail từ Dantri có thể không download được do CDN protection (không ảnh hưởng đến việc lưu tin)
