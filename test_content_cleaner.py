"""
Test Content Cleaner
Kiểm tra chức năng làm sạch và chuẩn hóa nội dung
"""

from utils.content_cleaner import ContentCleaner


def test_video_removal():
    """Test loại bỏ video"""
    print("=" * 60)
    print("TEST 1: Loại bỏ video tags")
    print("=" * 60)
    
    html = """
    <div class="article-content">
        <p>Đây là đoạn văn bản.</p>
        <video width="320" height="240" controls>
            <source src="movie.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <p>Đoạn văn bản tiếp theo.</p>
        <iframe src="https://www.youtube.com/embed/xyz" frameborder="0"></iframe>
        <p>Đoạn cuối cùng.</p>
    </div>
    """
    
    cleaner = ContentCleaner()
    cleaned = cleaner.clean(html)
    
    print("Input HTML:")
    print(html)
    print("\nCleaned HTML:")
    print(cleaned)
    print("\nVideo removed:", "video" not in cleaned.lower())
    print("Iframe removed:", "iframe" not in cleaned.lower())
    print()


def test_video_container_removal():
    """Test loại bỏ video containers"""
    print("=" * 60)
    print("TEST 2: Loại bỏ video containers")
    print("=" * 60)
    
    html = """
    <div class="article-content">
        <p>Nội dung bài viết.</p>
        <div class="video-player">
            <div class="player-wrapper">Video content here</div>
        </div>
        <div class="youtube-embed">YouTube video</div>
        <p>Nội dung tiếp theo.</p>
    </div>
    """
    
    cleaner = ContentCleaner()
    cleaned = cleaner.clean(html)
    
    print("Input HTML:")
    print(html)
    print("\nCleaned HTML:")
    print(cleaned)
    print("\nVideo containers removed:", "video-player" not in cleaned.lower())
    print()


def test_font_normalization():
    """Test chuẩn hóa font và cỡ chữ"""
    print("=" * 60)
    print("TEST 3: Chuẩn hóa font và cỡ chữ")
    print("=" * 60)
    
    html = """
    <div class="article-content">
        <p style="font-family: Times New Roman; font-size: 14px; color: red;">
            Đoạn văn với font Times New Roman.
        </p>
        <p style="font-size: 18px; line-height: 2.0;">
            Đoạn văn với font size 18px.
        </p>
        <font face="Arial" size="3" color="blue">Đoạn văn với font tag</font>
        <h2 style="font-family: Georgia; font-size: 24px;">Tiêu đề</h2>
        <p style="text-align: center; font-size: 16px;">Đoạn căn giữa</p>
    </div>
    """
    
    cleaner = ContentCleaner()
    cleaned = cleaner.clean(html)
    
    print("Input HTML:")
    print(html)
    print("\nCleaned HTML:")
    print(cleaned)
    print("\nFont-family removed:", "font-family" not in cleaned.lower())
    print("Font-size removed:", "font-size" not in cleaned.lower())
    print("Text-align preserved:", "text-align" in cleaned.lower())
    print("Font tag removed:", "<font" not in cleaned.lower())
    print()


def test_complete_cleaning():
    """Test làm sạch hoàn chỉnh"""
    print("=" * 60)
    print("TEST 4: Làm sạch hoàn chỉnh")
    print("=" * 60)
    
    html = """
    <div class="article-content">
        <h1 style="font-family: Arial; font-size: 32px; color: #333;">Tiêu đề bài viết</h1>
        
        <p style="font-size: 16px; line-height: 1.5;">
            Đây là đoạn mở đầu của bài viết.
        </p>
        
        <div class="video-container">
            <video controls>
                <source src="video.mp4" type="video/mp4">
            </video>
        </div>
        
        <p style="font-family: Georgia; font-size: 14px;">
            Nội dung chính của bài viết với nhiều thông tin quan trọng.
        </p>
        
        <div class="advertisement">
            <img src="ad.jpg" alt="Advertisement">
        </div>
        
        <iframe src="https://www.youtube.com/embed/xyz"></iframe>
        
        <p style="text-align: justify; font-size: 15px; color: black;">
            Đoạn văn cuối cùng của bài viết.
        </p>
        
        <script>console.log('tracking');</script>
        
        <p></p>
        <p>   </p>
    </div>
    """
    
    cleaner = ContentCleaner()
    cleaned = cleaner.clean(html)
    
    print("Input HTML:")
    print(html)
    print("\nCleaned HTML:")
    print(cleaned)
    print("\n✓ Video removed:", "video" not in cleaned.lower())
    print("✓ Iframe removed:", "iframe" not in cleaned.lower())
    print("✓ Script removed:", "script" not in cleaned.lower())
    print("✓ Advertisement removed:", "advertisement" not in cleaned.lower())
    print("✓ Font-family removed:", "font-family" not in cleaned.lower())
    print("✓ Font-size removed:", "font-size" not in cleaned.lower())
    print("✓ Text-align preserved:", "text-align" in cleaned.lower())
    print("✓ Empty paragraphs removed:", cleaned.count("<p></p>") == 0)
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CONTENT CLEANER TEST SUITE")
    print("=" * 60 + "\n")
    
    test_video_removal()
    test_video_container_removal()
    test_font_normalization()
    test_complete_cleaning()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
