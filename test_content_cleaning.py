"""Test content cleaning for Dantri"""
import requests
from bs4 import BeautifulSoup
from utils.content_cleaner import ContentCleaner

url = 'https://dantri.com.vn/thoi-su/ha-noi-khong-xin-tien-khi-xay-dung-luat-thu-do-20260223082458443.htm'

print(f"Testing URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'lxml')

# Get article content
article = soup.find('article')
if article:
    print("=" * 70)
    print("ORIGINAL CONTENT (first 500 chars)")
    print("=" * 70)
    original = str(article)[:500]
    print(original)
    
    print("\n" + "=" * 70)
    print("CLEANED CONTENT (first 1000 chars)")
    print("=" * 70)
    
    cleaner = ContentCleaner()
    cleaned = cleaner.clean(str(article), source_name='Dân Trí')
    print(cleaned[:1000])
    
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Original length: {len(str(article))} chars")
    print(f"Cleaned length: {len(cleaned)} chars")
    print(f"Reduction: {100 - (len(cleaned) / len(str(article)) * 100):.1f}%")
    
    # Check for issues
    print("\n" + "=" * 70)
    print("CHECKS")
    print("=" * 70)
    
    if '(Dân trí)' in cleaned or '(Dân Trí)' in cleaned:
        print("✗ Still contains '(Dân trí)' prefix")
    else:
        print("✓ '(Dân trí)' prefix removed")
    
    # Count images
    soup_cleaned = BeautifulSoup(cleaned, 'lxml')
    images = soup_cleaned.find_all('img')
    print(f"✓ Found {len(images)} images in cleaned content")
    
    for i, img in enumerate(images[:3], 1):
        src = img.get('src', 'NO SRC')
        print(f"  {i}. {src[:80]}")
    
    # Check for excessive whitespace
    if '\n\n\n' in cleaned:
        print("✗ Contains excessive line breaks")
    else:
        print("✓ No excessive line breaks")
    
else:
    print("✗ No article tag found")
