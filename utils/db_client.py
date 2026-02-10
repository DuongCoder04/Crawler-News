"""
Database Client
Kết nối trực tiếp với PostgreSQL database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Optional, List
from loguru import logger
from config import settings
import uuid
from datetime import datetime


class DatabaseClient:
    """Client để tương tác trực tiếp với PostgreSQL"""
    
    def __init__(self):
        self.connection_params = {
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME
        }
        
        # Test connection
        try:
            conn = self._get_connection()
            conn.close()
            logger.info(f"Connected to database: {settings.DB_NAME}@{settings.DB_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
        
        # Cache categories
        self._categories_cache = None
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def get_categories(self) -> List[Dict]:
        """
        Lấy danh sách categories từ database
        
        Returns:
            List of category dictionaries
        """
        if self._categories_cache:
            return self._categories_cache
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, code, name, parent_code, status
                FROM category
                WHERE parent_code = 'NEWS' OR code = 'NEWS'
                ORDER BY name
            """)
            
            self._categories_cache = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            logger.info(f"Loaded {len(self._categories_cache)} categories")
            return self._categories_cache
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    def download_and_save_image(self, image_url: str) -> Optional[str]:
        """
        Download image và lưu attachment record
        
        Note: Method này không được sử dụng nữa vì attachment table có foreign key constraint
        Thay vào đó, thumbnail URL được embed trực tiếp vào content
        
        Args:
            image_url: URL của ảnh
            
        Returns:
            Attachment ID hoặc None
        """
        # Deprecated - không sử dụng
        return None
    
    def create_news(self, article_data: Dict) -> bool:
        """
        Tạo tin tức mới trong database
        
        Args:
            article_data: Dictionary chứa dữ liệu bài viết
                - title: str (required)
                - content: str (required)
                - category_code: str (required)
                - thumbnail: str (optional, URL)
                - source_url: str (optional)
                - source_name: str (optional)
                
        Returns:
            True nếu thành công, False nếu thất bại
        """
        conn = None
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
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Prepare content with thumbnail
            content = article_data['content']
            
            # Add thumbnail as img tag at the beginning if exists
            if article_data.get('thumbnail'):
                thumbnail_html = f'<img src="{article_data["thumbnail"]}" alt="thumbnail" style="max-width:100%"/><br/>'
                content = thumbnail_html + content
            
            # Add source info to content as HTML comment
            if source_url:
                source_name = article_data.get('source_name', 'Unknown')
                content += f'\n<!-- Source: {source_name} | URL: {source_url} -->'
            
            # Create news record
            news_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO news (id, title, content, status, category_code, created_at, reaction_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                news_id,
                article_data['title'][:500],  # Max 500 chars for title
                content,  # Full content with thumbnail
                'ACTIVE',
                article_data['category_code'],
                datetime.now(),
                0
            ))
            
            conn.commit()
            
            # Mark as crawled in cache
            if source_url:
                duplicate_checker.mark_crawled(source_url, news_id)
            
            logger.success(f"Created news: {news_id} - {article_data['title'][:50]}...")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            logger.error(f"Error creating news: {e}")
            return False
    
    def check_duplicate(self, source_url: str) -> bool:
        """
        Kiểm tra xem bài viết đã tồn tại chưa
        
        Args:
            source_url: URL nguồn của bài viết
            
        Returns:
            True nếu đã tồn tại, False nếu chưa
        """
        from storage.duplicate_checker import DuplicateChecker
        duplicate_checker = DuplicateChecker()
        return duplicate_checker.is_crawled(source_url)
    
    def get_news_count(self) -> int:
        """Get total news count"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM news")
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count
        except Exception as e:
            logger.error(f"Error getting news count: {e}")
            return 0
