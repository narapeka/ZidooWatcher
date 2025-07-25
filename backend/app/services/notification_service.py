import httpx
from typing import Optional
from app.models.zidoo_models import NotificationPayload
from app.core.config import settings
from app.core.logger import logger

class NotificationService:
    def __init__(self):
        # 移除初始化时的配置读取，改为每次发送时从内存获取最新配置
        pass
        
    async def send_notification(self, file_path: str) -> bool:
        """Send notification to external endpoint"""
        # 每次发送时从内存获取最新配置
        endpoint = settings.notification.endpoint
        timeout = settings.notification.timeout_seconds
        
        payload = NotificationPayload(file_path=file_path)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload.dict(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                logger.info(f"Notification sent successfully to {endpoint}: {file_path}")
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
    
 