"""
Static Crawler
Xử lý các trang web render HTML tĩnh (server-side)
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger
from engine.base_crawler import BaseCrawler


class StaticCrawler(BaseCrawler):
    """Crawler cho trang web tĩnh"""
    
    def extract_article_links(self, html: str, base_url: str) -> List[str]:
        """Extract article links từ list page"""
        soup = BeautifulSoup(html, 'lxml')
        
        selector = self.config['list_page']['selectors']['article_links']
        links = []
        
        for element in soup.select(selector):
            href = element.get('href')
            if href:
                # Convert to absolute URL
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        return links
    
    def extract_article_data(self, html: str, url: str) -> Optional[Dict]:
        """Extract article data từ detail page"""
        soup = BeautifulSoup(html, 'lxml')
        selectors = self.config['detail_page']['selectors']
        
        try:
            # Extract title
            title_elem = soup.select_one(selectors['title'])
            if not title_elem:
                logger.warning(f"No title found: {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract summary
            summary_elem = soup.select_one(selectors.get('summary', ''))
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # Extract content
            content_elem = soup.select_one(selectors['content'])
            if not content_elem:
                logger.warning(f"No content found: {url}")
                return None
            
            # Remove unwanted elements
            for remove_selector in self.config['detail_page'].get('remove_elements', []):
                for elem in content_elem.select(remove_selector):
                    elem.decompose()
            
            content = str(content_elem)
            
            # Extract thumbnail
            thumbnail = ''
            if 'thumbnail' in selectors:
                thumb_elem = soup.select_one(selectors['thumbnail'])
                if thumb_elem:
                    thumbnail = thumb_elem.get('content') or thumb_elem.get('src', '')
            
            # Extract published date
            published_date = None
            if 'published_date' in selectors:
                date_elem = soup.select_one(selectors['published_date'])
                if date_elem:
                    published_date = date_elem.get_text(strip=True)
            
            # Extract tags
            tags = []
            if 'tags' in selectors:
                tag_elems = soup.select(selectors['tags'])
                tags = [tag.get_text(strip=True) for tag in tag_elems]
            
            # Extract author
            author = ''
            if 'author' in selectors:
                author_elem = soup.select_one(selectors['author'])
                if author_elem:
                    author = author_elem.get_text(strip=True)
            
            return {
                'title': title,
                'summary': summary,
                'content': content,
                'thumbnail': thumbnail,
                'published_date': published_date,
                'tags': tags,
                'author': author
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data from {url}: {e}")
            return None
