# Trạng Thái Các Domain Crawler

Cập nhật: 12/02/2026

## Domains Đang Hoạt Động ✅

### 1. VnExpress (vnexpress.net)
- **Trạng thái**: ✅ Hoạt động tốt
- **Enabled**: true
- **Số categories**: 13
- **Ghi chú**: Crawler chính, hoạt động ổn định

### 2. Dân Trí (dantri.com.vn)
- **Trạng thái**: ✅ Hoạt động tốt
- **Enabled**: true
- **Số categories**: 12
- **Ghi chú**: Crawl thành công, có lỗi upload thumbnail (403 Forbidden từ CDN) nhưng bài viết vẫn được lưu

### 3. Thanh Niên (thanhnien.vn)
- **Trạng thái**: ⚙️ Mới thêm
- **Enabled**: true
- **Số categories**: 13
- **Ghi chú**: Cần test

### 4. Zing News (zingnews.vn)
- **Trạng thái**: ⚙️ Mới thêm
- **Enabled**: true
- **Số categories**: 12
- **Ghi chú**: Cần test

### 5. VietnamNet (vietnamnet.vn)
- **Trạng thái**: ⚙️ Mới thêm
- **Enabled**: true
- **Số categories**: 13
- **Ghi chú**: Cần test

### 6. Tuổi Trẻ (tuoitre.vn)
- **Trạng thái**: ⚠️ Selector không đúng
- **Enabled**: true
- **Số categories**: 13
- **Ghi chú**: Fetch thành công nhưng không tìm thấy bài viết (selector cần update)

## Domains Bị Tắt ❌

### 1. Cointelegraph Vietnam (vi.cointelegraph.com)
- **Trạng thái**: ❌ Bị chặn bởi robots.txt
- **Enabled**: false
- **Lý do**: Blocked by robots.txt

### 2. ICTNews (ictnews.vn)
- **Trạng thái**: ❌ Selector không đúng
- **Enabled**: false
- **Lý do**: Không tìm thấy bài viết

### 3. Coin68 (coin68.com)
- **Trạng thái**: ❌ Bị chặn bởi robots.txt
- **Enabled**: false
- **Lý do**: Blocked by robots.txt

### 4. Genk (genk.vn)
- **Trạng thái**: ❌ URL không tồn tại
- **Enabled**: false
- **Lý do**: 404 Not Found cho tất cả categories

### 5. Tạp Chí Bitcoin (tapchibitcoin.io)
- **Trạng thái**: ❌ Bị chặn bởi robots.txt
- **Enabled**: false
- **Lý do**: Blocked by robots.txt

### 6. Blockchain News VN (blockchain.news)
- **Trạng thái**: ❌ URL không tồn tại
- **Enabled**: false
- **Lý do**: 404 Not Found cho tất cả categories

## Thống Kê

- **Tổng số domains**: 12
- **Đang hoạt động**: 6
- **Bị tắt**: 6
- **Cần kiểm tra**: 4 (Thanh Niên, Zing News, VietnamNet, Tuổi Trẻ)

## Category Mapping

Tất cả domains đều map về các categories chuẩn:

- `POLITICS` - Chính trị, thời sự
- `WORLD` - Thế giới
- `BUSINESS` - Kinh doanh
- `CULTURE` - Văn hóa
- `EDUCATION` - Giáo dục
- `HEALTH` - Sức khỏe
- `SPORTS` - Thể thao
- `ENTERTAINMENT` - Giải trí
- `LAW` - Pháp luật
- `TRAVEL` - Du lịch
- `TECH` - Công nghệ
- `AUTO` - Ô tô, xe máy
- `LIFESTYLE` - Đời sống
- `SCIENCE` - Khoa học
- `REALESTATE` - Bất động sản

## Vấn Đề Cần Giải Quyết

### 1. Thumbnail Upload (Dân Trí)
- **Vấn đề**: CDN của Dân Trí trả về 403 Forbidden khi download ảnh
- **Giải pháp**: Cần thêm headers hoặc referer khi download ảnh
- **Ưu tiên**: Trung bình (bài viết vẫn được lưu)

### 2. Selector Không Đúng (Tuổi Trẻ)
- **Vấn đề**: Selector không match với HTML structure
- **Giải pháp**: Cần inspect HTML và update selector
- **Ưu tiên**: Cao

### 3. Robots.txt Blocking
- **Vấn đề**: Một số site chặn crawler
- **Giải pháp**: Tôn trọng robots.txt, không crawl
- **Ưu tiên**: N/A (không thể giải quyết)

## Khuyến Nghị

1. **Ưu tiên crawl**: VnExpress, Dân Trí (đã hoạt động tốt)
2. **Test tiếp**: Thanh Niên, Zing News, VietnamNet
3. **Fix selector**: Tuổi Trẻ
4. **Bỏ qua**: Các site bị chặn bởi robots.txt

## Rate Limiting

Tất cả domains đều có rate limiting:
- **Requests per minute**: 30
- **Delay between requests**: 2 seconds

## Schedule

Tất cả domains đều chạy:
- **Cron**: `0 */2 * * *` (mỗi 2 giờ)
- **Mode**: Scheduler hoặc One-time

## Content Cleaning

Tất cả bài viết đều được xử lý qua ContentCleaner:
- ✅ Loại bỏ video tags
- ✅ Loại bỏ video containers
- ✅ Chuẩn hóa font và styling
- ✅ Loại bỏ quảng cáo
- ✅ Loại bỏ scripts và iframes
