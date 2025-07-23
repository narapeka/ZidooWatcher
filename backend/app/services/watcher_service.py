import asyncio
import time
import os
import platform
from typing import Optional
from app.services.zidoo_client import ZidooClient
from app.services.path_mapper import PathMapper
from app.services.notification_service import NotificationService
from app.core.config import settings
from app.core.logger import logger
from app.core.log_buffer import log_buffer

# 设置时区 - 针对不同操作系统
if platform.system() == "Windows":
    # Windows系统需要特殊处理
    os.environ['TZ'] = 'Asia/Shanghai'
    # 在Windows上，我们需要确保Python使用正确的时区
    try:
        import locale
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Chinese_China.UTF8')
        except:
            pass
else:
    # Linux/Unix系统
    os.environ['TZ'] = 'Asia/Shanghai'
    try:
        time.tzset()
    except AttributeError:
        pass

def get_utc_timestamp():
    """获取UTC时间戳"""
    return time.time()

class WatcherService:
    def __init__(self):
        self.zidoo_client = ZidooClient()
        self.path_mapper = PathMapper()
        self.notification_service = NotificationService()
        
        self.is_running = False
        self.is_paused = False
        self.task: Optional[asyncio.Task] = None
        self.last_status = None
        self.last_notified_path = None
        self.device_connectivity_state = "unknown"  # Track device connectivity
        self.last_handled_video = None  # Track last video that was actually handled/processed
        
    async def start(self):
        """Start the watcher service"""
        if self.is_running:
            logger.warning("监控服务已在运行中")
            return
            
        self.is_running = True
        self.is_paused = False
        self.task = asyncio.create_task(self._heartbeat_loop())
        
        # Immediately check device status when starting
        await self._check_play_status()
        
        logger.info("监控服务已启动")
        log_buffer.add_log("监控服务已启动", "INFO")
        
    async def stop(self):
        """Stop the watcher service"""
        if not self.is_running:
            logger.warning("监控服务未在运行")
            return
            
        logger.info("正在停止监控服务...")
        
        # First set is_running to False to signal the loop to stop
        self.is_running = False
        
        # Clear status immediately
        self.last_status = None
        self.last_notified_path = None
        self.last_handled_video = None
        self.device_connectivity_state = "unknown"
        
        # Cancel the task if it exists
        if self.task and not self.task.done():
            logger.info("正在取消心跳任务...")
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("心跳任务已成功取消")
            except Exception as e:
                logger.error(f"取消心跳任务时出错: {e}")
            finally:
                self.task = None
        
        logger.info("监控服务已成功停止")
        log_buffer.add_log("监控服务已停止", "INFO")
        
    async def _heartbeat_loop(self):
        """Main heartbeat monitoring loop"""
        logger.info("心跳循环已启动")
        while self.is_running:
            try:
                # Check if we should continue
                if not self.is_running:
                    logger.info("心跳循环停止 - is_running 为 False")
                    break
                    
                await self._check_play_status()
                
                # Wait for the configured heartbeat interval
                # Use a shorter sleep interval to check is_running more frequently
                for _ in range(settings.general.heart_rate // 100):  # Check every 100ms
                    if not self.is_running:
                        logger.info("心跳循环在睡眠期间停止")
                        break
                    await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                logger.info("心跳循环已取消")
                break
            except Exception as e:
                logger.error(f"心跳循环出错: {e}")
                log_buffer.add_log(f"心跳循环出错: {e}", "ERROR")
                await asyncio.sleep(1)  # Wait a bit before retrying
        
        logger.info("心跳循环已结束")
    
    def get_status(self):
        """Get current service status"""
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "last_status": self.last_status,
            "last_notified_path": self.last_notified_path,
            "device_connectivity": self.device_connectivity_state
        }
                
    async def _check_play_status(self):
        """Check the current play status and handle state changes"""
        status, connectivity_state = await self.zidoo_client.get_play_status()
        
        # Update connectivity state
        if connectivity_state != self.device_connectivity_state:
            self.device_connectivity_state = connectivity_state
            if connectivity_state == "offline":
                log_buffer.add_log("Zidoo设备离线 - 继续监控", "WARNING")
            elif connectivity_state == "online":
                log_buffer.add_log("Zidoo设备已重新上线", "INFO")
        
        if connectivity_state == "offline":
            # Device is offline - continue monitoring but show offline status
            current_status = {
                "status": "offline",
                "message": "Zidoo设备离线",
                "connectivity": connectivity_state,
                "timestamp": get_utc_timestamp()
            }
            self.last_status = current_status
            return
            
        elif connectivity_state == "error":
            # API error - device might be online but API endpoint issue
            current_status = {
                "status": "error",
                "message": "获取播放状态失败 - API错误",
                "connectivity": connectivity_state,
                "timestamp": get_utc_timestamp()
            }
            self.last_status = current_status
            return
            
        elif status is None:
            # Unexpected error
            current_status = {
                "status": "error",
                "message": "获取播放状态失败",
                "connectivity": connectivity_state,
                "timestamp": get_utc_timestamp()
            }
            self.last_status = current_status
            return
            
        # Device is online and we got a response
        is_playing = self.zidoo_client.is_playing(status)
        video_path = self.zidoo_client.get_video_path(status)
        
        current_status = {
            "status": "playing" if is_playing else "stopped",
            "video_path": video_path,
            "zidoo_status": status.status,
            "connectivity": connectivity_state,
            "timestamp": get_utc_timestamp()
        }
        
        if is_playing and video_path:
            current_status["title"] = status.video.title if status.video else "Unknown"
            current_status["position"] = status.video.currentPosition if status.video else 0
            current_status["duration"] = status.video.duration if status.video else 0
            
        # Handle state changes
        if is_playing and video_path:
            if self.last_notified_path != video_path:
                # New video started playing
                await self._handle_video_start(video_path, status)
                self.last_notified_path = video_path
        else:
            # Video stopped playing - only log if we were actually handling the previous video
            self.last_notified_path = None
            self.last_handled_video = None
            
        self.last_status = current_status
        
    async def _handle_video_start(self, video_path: str, status):
        """Handle when a new video starts playing"""
        # Log with both title and path for clarity
        title = status.video.title if status.video else "未知"
        logger.info(f"新视频开始播放: {title}")
        log_buffer.add_log(f"新视频开始播放: {title} ({video_path})", "INFO")
        
        # Check path mapping with detailed status
        mapped_path, mapping_status = self.path_mapper.check_path_mapping_status(video_path)
        
        if mapped_path:
            # Successfully mapped - record that we're handling this video
            self.last_handled_video = video_path
            
            # Log combined action
            log_buffer.add_log("正在发送通知并停止本机播放...", "INFO")
            
            # Create task for notification (don't await it)
            notification_task = asyncio.create_task(
                self._send_notification_async(mapped_path)
            )
            
            # Immediately create task to stop playback (don't await it)
            stop_task = asyncio.create_task(
                self._stop_playback_async()
            )
            
        else:
            # No mapping found or mapping disabled - clear handled video
            self.last_handled_video = None
            log_buffer.add_log(mapping_status, "WARNING")
    
    async def _send_notification_async(self, mapped_path: str):
        """Send notification asynchronously"""
        try:
            success = await self.notification_service.send_notification(mapped_path)
            if success:
                log_buffer.add_log(f"通知已发送: {mapped_path}", "INFO")
            else:
                log_buffer.add_log(f"发送通知失败: {mapped_path}", "ERROR")
        except Exception as e:
            logger.error(f"发送通知时出错: {e}")
            log_buffer.add_log(f"发送通知时出错: {e}", "ERROR")
    
    async def _stop_playback_async(self):
        """Stop playback asynchronously"""
        try:
            logger.info("正在异步停止播放...")
            
            stop_success = await self.zidoo_client.stop_playback()
            if stop_success:
                logger.info("播放已成功停止")
            else:
                log_buffer.add_log("停止本机播放失败", "WARNING")
        except Exception as e:
            logger.error(f"停止播放时出错: {e}")
            log_buffer.add_log(f"停止本机播放时出错: {e}", "ERROR") 