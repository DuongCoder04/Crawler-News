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
    
    def clean(self, html: str, source_name: str = '') -> str:
        """
        Làm sạch HTML content
        
        Args:
            html: Raw HTML content
            source_name: Tên nguồn tin (để xử lý đặc biệt cho từng nguồn)
            
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
            
            # Xử lý đặc biệt cho Dân Trí
            if 'dân trí' in source_name.lower() or 'dantri' in source_name.lower():
                self._clean_dantri_specific(soup)
            
            # Remove all links from content (convert to plain text)
            self._remove_links(soup)
            
            # Fix images - convert lazy loading to actual src
            self._fix_images(soup)
            
            # Normalize font and styling
            self._normalize_styling(soup)
            
            # Remove empty paragraphs and excessive whitespace
            self._remove_empty_elements(soup)
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
                comment.extract()
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Additional text cleaning
            cleaned_html = self._clean_text(cleaned_html)
            
            # Remove "(Dân trí) - " prefix
            cleaned_html = re.sub(r'^\s*\(Dân trí\)\s*[-–—]\s*', '', cleaned_html, flags=re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>\s*\(Dân trí\)\s*[-–—]\s*', '<p>', cleaned_html, flags=re.IGNORECASE)
            
            return cleaned_html
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return html
    
    def _clean_dantri_specific(self, soup: BeautifulSoup):
        """
        Xử lý đặc biệt cho nội dung Dân Trí
        
        Args:
            soup: BeautifulSoup object
        """
        # Remove h1 title (it's already saved separately in title field)
        for h1 in soup.find_all('h1'):
            h1.decompose()
        
        # Remove category tags (THỜI SỰ, etc.)
        # e-magazine__maincate contains category name
        for div in soup.find_all('div', class_=lambda x: x and 'maincate' in str(x).lower()):
            div.decompose()
        
        # Remove author info section (Thực hiện:, etc.)
        # e-magazine__info and e-magazine__meta contain author info
        for div in soup.find_all('div', class_=lambda x: x and ('e-magazine__info' in str(x) or 'e-magazine__meta' in str(x))):
            div.decompose()
        
        # Remove any remaining author meta items
        for span in soup.find_all('span', class_=lambda x: x and 'author' in str(x).lower()):
            span.decompose()
        
        # Remove category tags (usually at the beginning of content)
        # Dantri uses div with class containing 'tag' or 'category'
        for div in soup.find_all('div', class_=lambda x: x and ('tag' in str(x).lower() or 'category' in str(x).lower())):
            div.decompose()
        
        # Remove breadcrumb navigation
        for nav in soup.find_all('nav'):
            nav.decompose()
        
        for ul in soup.find_all('ul', class_=lambda x: x and 'breadcrumb' in str(x).lower()):
            ul.decompose()
        
        # Remove author info container (avatar, name, time)
        # Dantri uses specific structure: div.dt-flex.dt-items-center.dt-gap-1
        for div in soup.find_all('div', class_=lambda x: x and 'dt-flex' in x and 'dt-items-center' in x):
            # Check if contains author link or avatar
            if div.find('a', href=lambda x: x and 'tac-gia' in x):
                div.decompose()
                continue
            # Check if contains time element
            if div.find('time'):
                div.decompose()
                continue
        
        # Remove all links to author pages
        for a in soup.find_all('a', href=lambda x: x and 'tac-gia' in x):
            parent = a.parent
            if parent:
                parent.decompose()
        
        # Remove time/date elements
        for time_tag in soup.find_all('time'):
            time_tag.decompose()
        
        # Remove avatar images (small images, usually 24x24 or 36x36)
        for img in soup.find_all('img'):
            width = img.get('width', '')
            height = img.get('height', '')
            alt = img.get('alt', '').lower()
            src = img.get('src', '').lower()
            
            # Remove if it's a small avatar image
            if (width and int(width) <= 50) or (height and int(height) <= 50):
                img.decompose()
            elif 'avatar' in alt or 'avatar' in src or 'tac-gia' in src:
                img.decompose()
        
        # Remove "(Dân trí) - " from h2 sapo
        for h2 in soup.find_all('h2'):
            text = h2.get_text()
            if text.startswith('(Dân trí)') or text.startswith('(Dân Trí)'):
                # Remove the prefix
                new_text = re.sub(r'^\s*\(Dân [tT]rí\)\s*[-–—]\s*', '', text)
                h2.string = new_text
    
    def _remove_links(self, soup: BeautifulSoup):
        """
        Remove all links from content (convert to plain text)
        
        Args:
            soup: BeautifulSoup object
        """
        for a in soup.find_all('a'):
            # Keep the text but remove the link
            a.unwrap()
    
    def _fix_images(self, soup: BeautifulSoup):
        """
        Fix image tags - convert lazy loading to actual src
        
        Args:
            soup: BeautifulSoup object
        """
        for img in soup.find_all('img'):
            # Check for lazy loading attributes
            if img.has_attr('data-src'):
                img['src'] = img['data-src']
                del img['data-src']
            
            if img.has_attr('data-original'):
                img['src'] = img['data-original']
                del img['data-original']
            
            if img.has_attr('data-lazy-src'):
                img['src'] = img['data-lazy-src']
                del img['data-lazy-src']
            
            # Remove loading="lazy" attribute
            if img.has_attr('loading'):
                del img['loading']
            
            # Ensure img has src attribute
            if not img.has_attr('src') or not img['src'] or img['src'].startswith('data:'):
                # Try to find src in other attributes
                for attr in ['data-url', 'data-image', 'data-img']:
                    if img.has_attr(attr):
                        img['src'] = img[attr]
                        break
                else:
                    # If still no valid src, remove the img tag
                    img.decompose()
                    continue
            
            # Add alt text if missing
            if not img.has_attr('alt'):
                img['alt'] = 'Image'
            
            # Remove excessive attributes
            attrs_to_keep = ['src', 'alt', 'title', 'width', 'height']
            attrs_to_remove = [attr for attr in img.attrs if attr not in attrs_to_keep]
            for attr in attrs_to_remove:
                del img[attr]
    
    def _remove_empty_elements(self, soup: BeautifulSoup):
        """
        Remove empty elements and excessive whitespace
        
        Args:
            soup: BeautifulSoup object
        """
        # Remove empty paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            # Remove if empty or only contains whitespace/special chars
            if not text or text in ['&nbsp;', '\xa0', ' ']:
                p.decompose()
        
        # Remove empty divs
        for div in soup.find_all('div'):
            if not div.get_text(strip=True) and not div.find_all('img'):
                div.decompose()
        
        # Remove excessive br tags
        for br in soup.find_all('br'):
            # Check if there are multiple consecutive br tags
            next_sibling = br.next_sibling
            if next_sibling and next_sibling.name == 'br':
                br.decompose()
    
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
        # Remove excessive whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove multiple spaces within text
        html = re.sub(r'[ \t]+', ' ', html)
        
        # Remove spaces before punctuation
        html = re.sub(r'\s+([.,;:!?])', r'\1', html)
        
        # Remove multiple line breaks (more than 2)
        html = re.sub(r'\n{3,}', '\n\n', html)
        
        # Remove leading/trailing whitespace in paragraphs
        html = re.sub(r'<p>\s+', '<p>', html)
        html = re.sub(r'\s+</p>', '</p>', html)
        
        # Remove &nbsp; entities
        html = html.replace('&nbsp;', ' ')
        html = html.replace('\xa0', ' ')
        
        return html.strip()
