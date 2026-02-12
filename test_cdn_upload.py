"""
Test CDN Upload
Test upload image to 0x2labs CDN
"""

from utils.cdn_uploader import CDNUploader
from utils.logger import setup_logger

# Setup logger
setup_logger()

def test_cdn_upload():
    """Test CDN upload functionality"""
    
    # Test image URL - public image
    test_image_url = "https://picsum.photos/800/600"
    
    print("=" * 70)
    print("Testing CDN Upload")
    print("=" * 70)
    print(f"\nTest Image URL: {test_image_url}\n")
    
    # Initialize uploader
    uploader = CDNUploader()
    
    # Upload to CDN
    print("Uploading to CDN...")
    result = uploader.upload_with_retry(test_image_url)
    
    if result:
        print("\n✅ Upload successful!")
        print(f"\nCDN Data:")
        print(f"  - Key:      {result.get('key')}")
        print(f"  - Bucket:   {result.get('bucket')}")
        print(f"  - URL:      {result.get('url')}")
        print(f"  - Size:     {result.get('size')} bytes")
        print(f"  - MimeType: {result.get('mimetype')}")
    else:
        print("\n❌ Upload failed!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_cdn_upload()
