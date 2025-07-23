import httpx
from typing import Optional
from app.models.zidoo_models import NotificationPayload
from app.core.config import settings
from app.core.logger import logger

class NotificationService:
    def __init__(self):
        self.endpoint = settings.notification.endpoint
        self.timeout = settings.notification.timeout_seconds
        
    async def send_notification(self, file_path: str) -> bool:
        """Send notification to external endpoint"""
        payload = NotificationPayload(file_path=file_path)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.endpoint,
                    json=payload.dict(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                logger.info(f"Notification sent successfully to {self.endpoint}: {file_path}")
                return True
                
        except httpx.RequestError as e:
            logger.error(f"Request error when sending notification: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when sending notification: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending notification: {e}")
            return False
    
 