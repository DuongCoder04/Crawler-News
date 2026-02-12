# 🎨 Console Output Guide

## 📋 Tổng Quan

Crawler đã được nâng cấp với console output đẹp mắt, dễ đọc với colors và formatting.

---

## ✨ Features

### 1. Banner
```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🗞️  X-WISE NEWS CRAWLER SYSTEM  🗞️                  ║
║                                                                   ║
║                    Automated News Collection                      ║
║                         Version 1.0.0                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 2. Headers & Subheaders
```
▶ One-Time Crawl Mode
------------------------------------------------------------
```

### 3. Status Messages

**Success (Green ✓):**
```
✓ Connected to database: wise_local@127.0.0.1
```

**Error (Red ✗):**
```
✗ Failed to connect to database
```

**Warning (Yellow ⚠):**
```
⚠ Skipping disabled domain: Coin68
```

**Info (Blue ℹ):**
```
ℹ Loaded 7 domain configurations
```

### 4. Crawling Status

**Domain Crawling (Magenta 🕷️):**
```
🕷️  Crawling: VnExpress
```

**Article Status:**
```
  📰 [NEW] Đề xuất chuyến bay chậm 3 giờ...
  📄 [SKIP] Linh vật ngựa trên cả nước...
```

### 5. Statistics

```
📊 Statistics for VnExpress:
  ✓ New articles:      2
  ⊘ Duplicates:        42
  Σ Total processed:   44
```

### 6. Schedule Information

```
⏰ VnExpress: Every 2 hours - Chạy mỗi 2 giờ
```

### 7. Database Info

```
💾 Database: 32 total articles
```

### 8. Waiting Status

```
⏳ Scheduler running... Press Ctrl+C to stop
Checking for scheduled jobs every minute...
```

---

## 🎨 Color Scheme

| Element | Color | Icon |
|---------|-------|------|
| Success | Green | ✓ |
| Error | Red | ✗ |
| Warning | Yellow | ⚠ |
| Info | Blue | ℹ |
| Crawling | Magenta | 🕷️ |
| New Article | Green | 📰 |
| Duplicate | Yellow | 📄 |
| Statistics | Cyan | 📊 |
| Schedule | Cyan | ⏰ |
| Database | Cyan | 💾 |
| Waiting | Cyan | ⏳ |

---

## 📸 Screenshots

### One-Time Mode

```
╔═══════════════════════════════════════════════════════════════════╗
║              🗞️  X-WISE NEWS CRAWLER SYSTEM  🗞️                  ║
╚═══════════════════════════════════════════════════════════════════╝

▶ One-Time Crawl Mode
------------------------------------------------------------
ℹ Loaded 7 domain configurations
✓ Connected to database: wise_local@127.0.0.1

🕷️  Crawling: VnExpress
  📰 [NEW] Đề xuất chuyến bay chậm 3 giờ...
  📄 [SKIP] Linh vật ngựa trên cả nước...
  📰 [NEW] Làng cá nướng Cửa Lò tất bật vụ Tết...

📊 Statistics for VnExpress:
  ✓ New articles:      2
  ⊘ Duplicates:        42
  Σ Total processed:   44

────────────────────────────────────────────────────────────────────
▶ Crawl Summary
------------------------------------------------------------
✓ New articles: 2
ℹ Duplicates skipped: 42

💾 Database: 32 total articles
```

### Scheduler Mode

```
╔═══════════════════════════════════════════════════════════════════╗
║              🗞️  X-WISE NEWS CRAWLER SYSTEM  🗞️                  ║
╚═══════════════════════════════════════════════════════════════════╝

▶ Scheduler Mode
------------------------------------------------------------
ℹ Crawler will run automatically based on schedule configuration
⚠ Press Ctrl+C to stop

✓ Connected to database: wise_local@127.0.0.1

▶ Scheduling Jobs
------------------------------------------------------------
⏰ VnExpress: Every 2 hours - Chạy mỗi 2 giờ
✓ Scheduled 1 crawler(s)

────────────────────────────────────────────────────────────────────
▶ Initial Crawl
------------------------------------------------------------
🕷️  Crawling: VnExpress
...

────────────────────────────────────────────────────────────────────
⏳ Scheduler running... Press Ctrl+C to stop
Checking for scheduled jobs every minute...
```

---

## 🔧 Technical Details

### Console Utility Class

File: `utils/console.py`

**Methods:**
- `header(text)` - Print header với border
- `subheader(text)` - Print subheader
- `success(text)` - Success message (green)
- `error(text)` - Error message (red)
- `warning(text)` - Warning message (yellow)
- `info(text)` - Info message (blue)
- `crawling(domain)` - Crawling status
- `article(title, status)` - Article info
- `stats(domain, new, duplicate, total)` - Statistics
- `schedule_info(domain, schedule)` - Schedule info
- `database_info(count)` - Database info
- `waiting()` - Waiting message
- `banner()` - Application banner

### Dependencies

```python
from colorama import Fore, Back, Style, init
```

**Installation:**
```bash
pip install colorama
```

---

## 💡 Usage Examples

### In Your Code

```python
from utils.console import Console

# Print banner
Console.banner()

# Print header
Console.header("X-Wise News Crawler")

# Print subheader
Console.subheader("Starting Crawl")

# Print success
Console.success("Connected to database")

# Print error
Console.error("Failed to connect")

# Print warning
Console.warning("Skipping disabled domain")

# Print info
Console.info("Loaded 7 configurations")

# Print crawling status
Console.crawling("VnExpress")

# Print article
Console.article("Article Title", "new")  # or "skip"

# Print statistics
Console.stats("VnExpress", new=2, duplicate=42, total=44)

# Print schedule info
Console.schedule_info("VnExpress", "Every 2 hours")

# Print database info
Console.database_info(32)

# Print separator
Console.separator()

# Print waiting message
Console.waiting()
```

---

## 🎯 Benefits

### Before (Plain Text)
```
2026-02-10 12:03:16 | INFO | Running crawler in one-time mode
2026-02-10 12:03:16 | INFO | Loaded config: VnExpress
2026-02-10 12:03:16 | INFO | Connected to database: wise_local@127.0.0.1
2026-02-10 12:03:16 | INFO | Crawling VnExpress...
2026-02-10 12:03:16 | SUCCESS | Created news: uuid - Title...
```

### After (Formatted & Colored)
```
╔═══════════════════════════════════════════════════════════════════╗
║              🗞️  X-WISE NEWS CRAWLER SYSTEM  🗞️                  ║
╚═══════════════════════════════════════════════════════════════════╝

▶ One-Time Crawl Mode
------------------------------------------------------------
ℹ Loaded 7 domain configurations
✓ Connected to database: wise_local@127.0.0.1

🕷️  Crawling: VnExpress
  📰 [NEW] Article Title...
```

**Improvements:**
- ✅ Dễ đọc hơn
- ✅ Phân biệt rõ ràng các loại message
- ✅ Visual feedback tốt hơn
- ✅ Professional appearance
- ✅ Easier to spot errors/warnings

---

## 🔄 Backward Compatibility

- ✅ Logs vẫn được ghi vào file như cũ
- ✅ Console output chỉ ảnh hưởng terminal
- ✅ Không ảnh hưởng đến functionality
- ✅ Có thể disable colors nếu cần

### Disable Colors (If Needed)

```python
# In utils/console.py
init(autoreset=True, strip=True)  # Strip colors
```

Or set environment variable:
```bash
export NO_COLOR=1
```

---

## 📝 Notes

- Colors work on most modern terminals
- Windows: Requires Windows 10+ or colorama
- Linux/Mac: Works out of the box
- Logs file: Plain text (no colors)
- Terminal: Colored output

---

**Status:** ✅ Implemented  
**Version:** 1.0.0  
**Last Updated:** 10/02/2026
