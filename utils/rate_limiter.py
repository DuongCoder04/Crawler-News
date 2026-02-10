"""
Rate Limiter
Giới hạn số request per minute
"""

import time
from collections import deque
from loguru import logger


class RateLimiter:
    """Rate limiter sử dụng sliding window"""
    
    def __init__(self, requests_per_minute: int = 30):
        """
        Args:
            requests_per_minute: Số request tối đa mỗi phút
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.requests = deque()
    
    def wait_if_needed(self):
        """Đợi nếu đã vượt quá rate limit"""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window_size:
            self.requests.popleft()
        
        # Check if we need to wait
        if len(self.requests) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.requests[0]
            wait_time = self.window_size - (now - oldest_request)
            
            if wait_time > 0:
                logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                
                # Clean up again after waiting
                now = time.time()
                while self.requests and self.requests[0] < now - self.window_size:
                    self.requests.popleft()
        
        # Record this request
        self.requests.append(time.time())
