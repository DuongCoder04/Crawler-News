"""
Test Dantri HTML structure to find correct selectors
"""
import requests
from bs4 import BeautifulSoup

# Test URL
url = 'https://dantri.com.vn/the-thao/duong-quoc-hoang-vo-dich-premier-league-pool-2026-di-vao-lich-su-20260223110550978.htm'

print(f"Testing URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    print("=" * 70)
    print("TESTING TITLE SELECTORS")
    print("=" * 70)
    
    title_selectors = [
        'h1.title-page',
        'h1.article-title',
        'h1.dt-news__title',
        'h1[data-role="title"]',
        'h1',
        'meta[property="og:title"]',
        'meta[name="title"]',
    ]
    
    for selector in title_selectors:
        elem = soup.select_one(selector)
        if elem:
            if elem.name == 'meta':
                content = elem.get('content', '')
                print(f"✓ {selector:40s} -> {content[:80]}")
            else:
                text = elem.get_text(strip=True)
                print(f"✓ {selector:40s} -> {text[:80]}")
        else:
            print(f"✗ {selector:40s} -> Not found")
    
    print("\n" + "=" * 70)
    print("TESTING CONTENT SELECTORS")
    print("=" * 70)
    
    content_selectors = [
        'div.singular-content',
        'div.e-magazine__body',
        'div.article-content',
        'div.dt-news__content',
        'div.dt-news__body',
        'article div.content',
        'div[data-role="content"]',
    ]
    
    for selector in content_selectors:
        elem = soup.select_one(selector)
        if elem:
            text_len = len(elem.get_text(strip=True))
            print(f"✓ {selector:40s} -> Found ({text_len} chars)")
        else:
            print(f"✗ {selector:40s} -> Not found")
    
    print("\n" + "=" * 70)
    print("TESTING SUMMARY SELECTORS")
    print("=" * 70)
    
    summary_selectors = [
        'h2.singular-sapo',
        'div.dt-news__sapo',
        'div.article-sapo',
        'p.sapo',
        'div.sapo',
        'meta[name="description"]',
    ]
    
    for selector in summary_selectors:
        elem = soup.select_one(selector)
        if elem:
            if elem.name == 'meta':
                content = elem.get('content', '')
                print(f"✓ {selector:40s} -> {content[:80]}")
            else:
                text = elem.get_text(strip=True)
                print(f"✓ {selector:40s} -> {text[:80]}")
        else:
            print(f"✗ {selector:40s} -> Not found")
    
    print("\n" + "=" * 70)
    print("TESTING THUMBNAIL SELECTORS")
    print("=" * 70)
    
    thumb_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'div.dt-news__avatar img',
        'figure.image img',
    ]
    
    for selector in thumb_selectors:
        elem = soup.select_one(selector)
        if elem:
            if elem.name == 'meta':
                content = elem.get('content', '')
                print(f"✓ {selector:40s} -> {content[:80]}")
            else:
                src = elem.get('src', '')
                print(f"✓ {selector:40s} -> {src[:80]}")
        else:
            print(f"✗ {selector:40s} -> Not found")
    
    print("\n" + "=" * 70)
    print("HTML STRUCTURE SAMPLE")
    print("=" * 70)
    
    # Find all h1 tags
    h1_tags = soup.find_all('h1')
    if h1_tags:
        print(f"\nFound {len(h1_tags)} H1 tag(s):")
        for i, h1 in enumerate(h1_tags, 1):
            classes = h1.get('class', [])
            data_role = h1.get('data-role', '')
            print(f"  {i}. <h1 class='{' '.join(classes)}' data-role='{data_role}'>")
            print(f"     Text: {h1.get_text(strip=True)[:100]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
