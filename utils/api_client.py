"""
X-Wise API Client
Xử lý tất cả API calls tới CMS X-Wise
"""

import requests
from typing import Dict, Optional, List
from loguru import logger
from config import settings


class XWiseAPIClient:
    """Client để tương tác với X-Wise CMS API"""
    
    def __init__(self):
        self.base_url = settings.XWISE_API_BASE_URL
        self.jwt_token = settings.XWISE_JWT_TOKEN
        
        if not self.jwt_token:
            raise ValueError("XWISE_JWT_TOKEN not found in environment variables")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        })
        
        # Cache categories
        self._categories_cache = None
        
        logger.info(f"Initialized X-Wise API Client: {self.base_url}")
    
    def get_categories(self) -> List[Dict]:
        """
        Lấy danh sách categories từ X-Wise
        
        Returns:
            List of category dictionaries
        """
        if self._categories_cache:
            return self._categories_cache
        
        try:
            url = f"{self.base_url}/cms/wise/categories/by-parent/NEWS"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self._categories_cache = data.get('data', [])
            
            logger.info(f"Loaded {len(self._categories_cache)} categories")
            return self._categories_cache
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        Download image từ URL và upload lên X-Wise
        
        Args:
            image_url: URL của ảnh cần upload
            
        Returns:
            Attachment ID hoặc None
        """
        try:
            # Download image
            logger.debug(f"Downloading image: {image_url}")
            img_response = requests.get(image_url, timeout=30, stream=True)
            img_response.raise_for_status()
            
            # Get filename from URL
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                filename = 'image.jpg'
            
            # Upload to X-Wise
            url = f"{self.base_url}/cms/wise/attachment/upload"
            files = {
                'file': (filename, img_response.content, img_response.headers.get('content-type', 'image/jpeg'))
            }
            
            # Remove Content-Type header for multipart/form-data
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            
            upload_response = requests.post(url, files=files, headers=headers, timeout=60)
            upload_response.raise_for_status()
            
            data = upload_response.json()
            attachment_id = data.get('data', {}).get('id')
            
            if attachment_id:
                logger.success(f"Uploaded image: {attachment_id}")
                return attachment_id
            else:
                logger.warning("No attachment ID in response")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image {image_url}: {e}")
            return None
    
    def create_news(self, article_data: Dict) -> bool:
        """
        Tạo tin tức mới trên X-Wise
        
        Args:
            article_data: Dictionary chứa dữ liệu bài viết
                - title: str (required)
                - content: str (required)
                - summary: str (optional)
                - category_code: str (required)
                - thumbnail: str (optional, URL)
                - source_url: str (optional, for duplicate check)
                - source_name: str (optional, for logging)
                
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Validate required fields
            if not article_data.get('title'):
                logger.error("Missing required field: title")
                return False
            
            if not article_data.get('content'):
                logger.error("Missing required field: content")
                return False
            
            if not article_data.get('category_code'):
                logger.error("Missing required field: category_code")
                return False
            
            # Check duplicate using cache
            from storage.duplicate_checker import DuplicateChecker
            duplicate_checker = DuplicateChecker()
            
            source_url = article_data.get('source_url')
            if source_url and duplicate_checker.is_crawled(source_url):
                logger.info(f"Article already crawled: {source_url}")
                return False
            
            # Upload thumbnail if exists
            attachment_ids = []
            if article_data.get('thumbnail'):
                attachment_id = self.upload_image(article_data['thumbnail'])
                if attachment_id:
                    attachment_ids.append(attachment_id)
            
            # Add source info to content as HTML comment (for traceability)
            content = article_data['content']
            if source_url:
                source_name = article_data.get('source_name', 'Unknown')
                content += f'\n<!-- Source: {source_name} | URL: {source_url} -->'
            
            # Prepare payload
            payload = {
                'title': article_data['title'][:1000],  # Max 1000 chars
                'content': content[:50000],  # Max 50000 chars
                'status': 'ACTIVE',
                'category_code': article_data['category_code'],
                'attachments': attachment_ids
            }
            
            # Create news
            url = f"{self.base_url}/cms/wise/news"
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            news_id = data.get('data', {}).get('id')
            
            if news_id:
                # Mark as crawled in cache
                if source_url:
                    duplicate_checker.mark_crawled(source_url, news_id)
                
                logger.success(f"Created news: {news_id} - {article_data['title'][:50]}...")
                return True
            else:
                logger.warning("No news ID in response")
                return False
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error_data = e.response.json()
                logger.error(f"Validation error: {error_data}")
            elif e.response.status_code == 401:
                logger.error("Authentication failed. Check JWT token.")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Error creating news: {e}")
            return False
    
    def check_duplicate(self, source_url: str) -> bool:
        """
        Kiểm tra xem bài viết đã tồn tại chưa
        
        Note: Sử dụng Redis cache để check duplicate vì database không có trường source_url
        
        Args:
            source_url: URL nguồn của bài viết
            
        Returns:
            True nếu đã tồn tại, False nếu chưa
        """
        from storage.duplicate_checker import DuplicateChecker
        duplicate_checker = DuplicateChecker()
        return duplicate_checker.is_crawled(source_url)
