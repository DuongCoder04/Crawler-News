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
        
        # Danh sách các tag không mong muốn (bao gồm video)
        self.unwanted_tags = [
            'script', 'style', 'iframe', 'noscript',
            'embed', 'object', 'applet', 'video', 'audio',
            'source', 'track'
        ]
        
        # Cấu hình font và cỡ chữ chuẩn
        self.standard_font = 'Arial, sans-serif'
        self.standard_font_size = '16px'
        self.standard_line_height = '1.6'
    
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
            
            # Remove unwanted tags (bao gồm video)
            for tag_name in self.unwanted_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove video containers by common class names
            video_patterns = [
                r'video[-_]?',
                r'player[-_]?',
                r'media[-_]?player',
                r'youtube',
                r'vimeo',
                r'dailymotion'
            ]
            for pattern in video_patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                for tag in soup.find_all(class_=regex):
                    tag.decompose()
                for tag in soup.find_all(id=regex):
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
            
            # Normalize font and styling
            self._normalize_styling(soup)
            
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
    
    def _normalize_styling(self, soup: BeautifulSoup):
        """
        Chuẩn hóa font, cỡ chữ và styling
        
        Args:
            soup: BeautifulSoup object
        """
        # Remove inline styles that affect font/size
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            # Remove font-related styles
            style = re.sub(r'font-family:[^;]+;?', '', style, flags=re.IGNORECASE)
            style = re.sub(r'font-size:[^;]+;?', '', style, flags=re.IGNORECASE)
            style = re.sub(r'line-height:[^;]+;?', '', style, flags=re.IGNORECASE)
            style = re.sub(r'color:[^;]+;?', '', style, flags=re.IGNORECASE)
            
            if style.strip():
                tag['style'] = style.strip()
            else:
                del tag['style']
        
        # Remove font tags
        for font_tag in soup.find_all('font'):
            font_tag.unwrap()
        
        # Remove size/color attributes
        for tag in soup.find_all():
            if tag.has_attr('size'):
                del tag['size']
            if tag.has_attr('color'):
                del tag['color']
            if tag.has_attr('face'):
                del tag['face']
        
        # Normalize heading tags
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                # Remove inline styles from headings
                if heading.has_attr('style'):
                    del heading['style']
        
        # Normalize paragraph tags
        for p in soup.find_all('p'):
            # Remove inline styles from paragraphs
            if p.has_attr('style'):
                style = p.get('style', '')
                # Keep only important styles like text-align
                important_styles = []
                if 'text-align' in style.lower():
                    align_match = re.search(r'text-align:\s*([^;]+)', style, re.IGNORECASE)
                    if align_match:
                        important_styles.append(f'text-align: {align_match.group(1).strip()}')
                
                if important_styles:
                    p['style'] = '; '.join(important_styles)
                else:
                    del p['style']
    
    def _clean_text(self, html: str) -> str:
        """Làm sạch text trong HTML"""
        # Remove multiple spaces
        html = re.sub(r'\s+', ' ', html)
        
        # Remove spaces before punctuation
        html = re.sub(r'\s+([.,;:!?])', r'\1', html)
        
        # Remove multiple line breaks
        html = re.sub(r'\n\s*\n', '\n\n', html)
        
        return html.strip()
