"""Find content selector for Dantri"""
import requests
from bs4 import BeautifulSoup

url = 'https://dantri.com.vn/the-thao/duong-quoc-hoang-vo-dich-premier-league-pool-2026-di-vao-lich-su-20260223110550978.htm'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'lxml')

print("SEARCHING FOR CONTENT")
print("=" * 70)

# Look for article tag
article = soup.find('article')
if article:
    print(f"Found <article> tag with classes: {article.get('class', [])}")
    divs = article.find_all('div', recursive=False)
    print(f"Direct child divs: {len(divs)}")
    for i, div in enumerate(divs[:5], 1):
        classes = ' '.join(div.get('class', []))
        text_len = len(div.get_text(strip=True))
        print(f"  {i}. {classes[:50]} ({text_len} chars)")

# Test patterns
print("\nTESTING PATTERNS:")
patterns = ['article', 'article > div', 'div.detail-content']
for pattern in patterns:
    elem = soup.select_one(pattern)
    if elem:
        text_len = len(elem.get_text(strip=True))
        print(f"✓ {pattern:30s} -> {text_len} chars")
    else:
        print(f"✗ {pattern:30s} -> Not found")

# Check paragraphs
all_p = soup.find_all('p')
print(f"\nTotal <p> tags: {len(all_p)}")
if all_p:
    for p in all_p:
        if len(p.get_text(strip=True)) > 50:
            parent = p.parent
            print(f"First <p> parent: {parent.name}, classes: {parent.get('class', [])}")
            break
