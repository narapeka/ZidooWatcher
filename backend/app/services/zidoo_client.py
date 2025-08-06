import httpx
import asyncio
import time
from typing import Optional, Tuple
from app.models.zidoo_models import ZidooPlayStatus
from app.core.config import settings
from app.core.logger import logger

class ZidooClient:
    def __init__(self):
        # 移除初始化时的配置读取，改为每次请求时从内存获取最新配置
        self.timeout = httpx.Timeout(10.0)
        self.is_device_online = True  # Track device connectivity
        self.consecutive_errors = 0   # Track consecutive connection errors
        self.last_request_time = 0    # Track last request time for rate limiting
        self.min_request_interval = 0.2  # 最小请求间隔200ms，防止DDOS
        
    async def get_play_status(self) -> Tuple[Optional[ZidooPlayStatus], str]:
        """
        Get the current play status from Zidoo player
        Returns: (status_object, connection_state)
        connection_state: "online", "offline", "error"
        """
        # 每次请求时从内存获取最新配置
        base_url = f"http://{settings.zidoo.ip}:{settings.zidoo.port}"
        api_path = settings.zidoo.api_path
        
        # 频率限制：确保请求间隔不小于最小间隔
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"频率限制：等待 {sleep_time:.3f}秒")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
        url = f"{base_url}{api_path}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"Zidoo API response: {data}")
                
                # Reset error counter on successful connection
                if not self.is_device_online:
                    logger.info("Zidoo设备已重新上线")
                    await self._on_device_online()
                
                self.is_device_online = True
                self.consecutive_errors = 0
                
                return ZidooPlayStatus(**data), "online"
                
        except httpx.ConnectError as e:
            # Device is likely offline or unreachable
            logger.warning(f"Zidoo设备似乎离线: {e}")
            await self._on_device_offline()
            return None, "offline"
            
        except httpx.TimeoutException as e:
            # Request timed out
            logger.warning(f"Zidoo API请求超时: {e}")
            await self._on_device_offline()
            return None, "offline"
            
        except httpx.RequestError as e:
            # Network-related errors
            logger.error(f"调用Zidoo API时网络错误: {e}")
            await self._on_device_offline()
            return None, "offline"
            
        except httpx.HTTPStatusError as e:
            # HTTP errors (like 404, 500, etc.)
            logger.error(f"调用Zidoo API时HTTP错误: {e.response.status_code}")
            # HTTP errors might indicate device is online but API endpoint is wrong
            return None, "error"
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"调用Zidoo API时意外错误: {e}")
            return None, "error"
    
    async def _on_device_offline(self):
        """Handle when device goes offline"""
        if self.is_device_online:
            logger.info("Zidoo设备已离线")
            self.is_device_online = False
            self.consecutive_errors += 1
    
    async def _on_device_online(self):
        """Handle when device comes back online"""
        logger.info("Zidoo设备已重新上线")
        self.is_device_online = True
        self.consecutive_errors = 0
    
    def is_playing(self, status: ZidooPlayStatus) -> bool:
        """Check if the player is currently playing"""
        return (status.status == 200 and 
                status.video is not None and 
                status.video.status == 1)
    
    def get_video_path(self, status: ZidooPlayStatus) -> Optional[str]:
        """Get the video path from the status response"""
        if self.is_playing(status) and status.video and status.video.path:
            return status.video.path
        return None
    
    async def stop_playback(self) -> bool:
        """Stop the current playback"""
        # 从内存获取最新配置
        base_url = f"http://{settings.zidoo.ip}:{settings.zidoo.port}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First send Key.Back
                back_url = f"{base_url}/ZidooControlCenter/RemoteControl/sendkey?key=Key.Back"
                logger.debug("发送 Key.Back 命令...")
                response = await client.get(back_url)
                response.raise_for_status()
                back_data = response.json()
                logger.debug(f"Key.Back 响应: {back_data}")
                
                # Wait 100ms
                await asyncio.sleep(0.1)
                
                # Then send Key.MediaStop
                stop_url = f"{base_url}/ZidooControlCenter/RemoteControl/sendkey?key=Key.MediaStop"
                logger.debug("发送 Key.MediaStop 命令...")
                response = await client.get(stop_url)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"停止播放响应: {data}")
                return True
                
        except Exception as e:
            logger.error(f"停止播放失败: {e}")
            return False
    
    def get_connectivity_status(self) -> dict:
        """Get current connectivity status"""
        # 从内存获取最新配置
        base_url = f"http://{settings.zidoo.ip}:{settings.zidoo.port}"
        return {
            "is_online": self.is_device_online,
            "consecutive_errors": self.consecutive_errors,
            "base_url": base_url
        } 