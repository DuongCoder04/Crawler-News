"""
CDN Uploader
Upload images to 0x2labs CDN
"""

import requests
from typing import Optional, Dict
from loguru import logger
from config import settings
import os
from urllib.parse import urlparse


class CDNUploader:
    """Upload images to CDN"""
    
    def __init__(self):
        self.upload_url = settings.CDN_UPLOAD_URL
        self.api_key = settings.CDN_API_KEY
        self.bucket = settings.CDN_BUCKET
        
    def download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download image from URL
        
        Args:
            image_url: URL of the image
            
        Returns:
            Image bytes or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://vnexpress.net/',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            return None
    
    def get_filename_from_url(self, url: str) -> str:
        """
        Extract filename from URL
        
        Args:
            url: Image URL
            
        Returns:
            Filename with extension
        """
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        # If no extension, default to jpg
        if '.' not in filename:
            filename += '.jpg'
        
        return filename
    
    def upload_to_cdn(self, image_url: str) -> Optional[Dict]:
        """
        Download image and upload to CDN
        
        Args:
            image_url: URL of the image to upload
            
        Returns:
            Dictionary with CDN info or None if failed
            {
                'key': 'xxx.jpg',
                'bucket': 'images',
                'url': 'https://cdn.0x2labs.com/images/xxx.jpg',
                'size': 224147,
                'mimetype': 'image/jpeg'
            }
        """
        try:
            # Download image
            logger.debug(f"Downloading image from: {image_url}")
            image_data = self.download_image(image_url)
            
            if not image_data:
                return None
            
            # Get filename
            filename = self.get_filename_from_url(image_url)
            
            # Prepare upload request
            files = {
                'file': (filename, image_data)
            }
            
            # Bucket without extra quotes
            data = {
                'bucket': self.bucket  # Just 'images', not '"images"'
            }
            
            headers = {
                'X-API-Key': self.api_key
            }
            
            # Upload to CDN
            logger.debug(f"Uploading to CDN: {filename}")
            
            response = requests.post(
                self.upload_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                cdn_data = result.get('data', {})
                logger.success(f"Uploaded to CDN: {cdn_data.get('url')}")
                return cdn_data
            else:
                logger.error(f"CDN upload failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading to CDN: {e}")
            return None
    
    def upload_with_retry(self, image_url: str, retries: int = 3) -> Optional[Dict]:
        """
        Upload to CDN with retry logic
        
        Args:
            image_url: URL of the image
            retries: Number of retry attempts
            
        Returns:
            CDN data or None
        """
        for attempt in range(retries):
            try:
                result = self.upload_to_cdn(image_url)
                if result:
                    return result
                
                if attempt < retries - 1:
                    logger.warning(f"Upload failed, retrying... ({attempt + 1}/{retries})")
                    
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1} failed: {e}")
        
        logger.error(f"Failed to upload after {retries} attempts")
        return None
