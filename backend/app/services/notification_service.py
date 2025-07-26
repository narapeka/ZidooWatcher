import httpx
from typing import Optional
from app.models.zidoo_models import NotificationPayload
from app.core.config import settings
from app.core.logger import logger

class NotificationService:
    def __init__(self):
        # 移除初始化时的配置读取，改为每次发送时从内存获取最新配置
        pass
        
    async def send_notification(self, file_path: str) -> int:
        """Send notification to external endpoint
        
        Returns:
            int: HTTP status code from the notification endpoint
        """
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
                
                # Log the notification result
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Successfully sent notification for {file_path}")
                    logger.debug(f"Response: {response.status_code} {response.text}")
                else:
                    logger.error(f"Failed to send notification: HTTP {response.status_code}")
                    logger.debug(f"Response: {response.text}")
                
                return response.status_code
                
        except httpx.RequestError as e:
            logger.error(f"Request error when sending notification: {e}")
            return 0  # Return 0 for network/connection errors
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when sending notification: {e.response.status_code}")
            return e.response.status_code
        except Exception as e:
            logger.error(f"Unexpected error when sending notification: {e}")
            return 0  # Return 0 for unexpected errors
    
 