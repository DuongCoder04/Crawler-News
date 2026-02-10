"""
Content Cleaner
Làm sạch và chuẩn hóa nội dung HTML
"""

from bs4 import BeautifulSoup
import re
from loguru import logger


class ContentCleaner:
    """Làm sạch nội dung HTML"""
    
    def __init__(self):
        # Danh sách các class/id thường chứa quảng cáo
        self.ad_patterns = [
            r'ad[s]?[-_]',
            r'advertisement',
            r'banner',
            r'sponsor',
            r'promo',
            r'commercial'
        ]
        
        # Danh sách các tag không mong muốn
        self.unwanted_tags = [
            'script', 'style', 'iframe', 'noscript',
            'embed', 'object', 'applet'
        ]
    
    def clean(self, html: str) -> str:
        """
        Làm sạch HTML content
        
        Args:
            html: Raw HTML content
            
        Returns:
            Cleaned HTML content
        """
        if not html:
            return ''
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove unwanted tags
            for tag_name in self.unwanted_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove elements with ad-related class/id
            for pattern in self.ad_patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                
                # Remove by class
                for tag in soup.find_all(class_=regex):
                    tag.decompose()
                
                # Remove by id
                for tag in soup.find_all(id=regex):
                    tag.decompose()
            
            # Remove empty paragraphs
            for p in soup.find_all('p'):
                if not p.get_text(strip=True):
                    p.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
                comment.extract()
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Additional text cleaning
            cleaned_html = self._clean_text(cleaned_html)
            
            return cleaned_html
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return html
    
    def _clean_text(self, html: str) -> str:
        """Làm sạch text trong HTML"""
        # Remove multiple spaces
        html = re.sub(r'\s+', ' ', html)
        
        # Remove spaces before punctuation
        html = re.sub(r'\s+([.,;:!?])', r'\1', html)
        
        # Remove multiple line breaks
        html = re.sub(r'\n\s*\n', '\n\n', html)
        
        return html.strip()
