import requests
from bs4 import BeautifulSoup

url = 'https://dantri.com.vn/the-thao/duong-quoc-hoang-vo-dich-premier-league-pool-2026-di-vao-lich-su-20260223110550978.htm'

print(f"Testing URL: {url}\n")

r = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(r.text, 'lxml')

print("=== TITLE SELECTORS ===")
selectors = [
    'h1.title-page',
    'h1.article-title',
    'h1.title',
    'h1',
    'meta[property="og:title"]'
]

for selector in selectors:
    elem = soup.select_one(selector)
    if elem:
        if elem.name == 'meta':
            print(f"✓ {selector}: {elem.get('content', '')[:100]}")
        else:
            print(f"✓ {selector}: {elem.get_text(strip=True)[:100]}")
    else:
        print(f"✗ {selector}: Not found")

print("\n=== CONTENT SELECTORS ===")
content_selectors = [
    'div.singular-content',
    'div.e-magazine__body',
    'div.article-content',
    'div.detail-content'
]

for selector in content_selectors:
    elem = soup.select_one(selector)
    if elem:
        print(f"✓ {selector}: Found ({len(elem.get_text())} chars)")
    else:
        print(f"✗ {selector}: Not found")
