from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.zidoo_models import ToggleServiceRequest, ToggleServiceResponse
from app.core.config import settings
from app.core.logger import logger
from app.services.watcher_service import WatcherService
from app.services.path_mapper import PathMapper
from app.core.log_buffer import log_buffer
import time
import os
import platform

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

# Global instances (will be set by main.py)
watcher_service: WatcherService = None

api_router = APIRouter()

# Service control endpoints
@api_router.post("/service/start", response_model=Dict[str, Any])
async def start_service():
    """Start the watcher service"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    await watcher_service.start()
    return {"success": True, "message": "服务已启动"}

@api_router.post("/service/stop", response_model=Dict[str, Any])
async def stop_service():
    """Stop the watcher service"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    await watcher_service.stop()
    return {"success": True, "message": "服务已停止"}



@api_router.get("/service/status", response_model=Dict[str, Any])
async def get_service_status():
    """Get the current service status"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    return watcher_service.get_status()

@api_router.get("/service/connectivity", response_model=Dict[str, Any])
async def get_connectivity_status():
    """Get the current device connectivity status"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    return watcher_service.zidoo_client.get_connectivity_status()

# Configuration endpoints
@api_router.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration"""
    # 构建配置响应，不包含端口（因为端口固定为9529）
    config_response = {
        "general": settings.general.model_dump(),
        "zidoo": {
            "ip": settings.zidoo.ip,
            "api_path": settings.zidoo.api_path
        },
        "notification": settings.notification.model_dump(),
        "extension_monitoring": settings.extension_monitoring.model_dump()
    }
    return config_response

@api_router.post("/config", response_model=Dict[str, Any])
async def update_config(config_data: Dict[str, Any]):
    """Update configuration"""
    try:
        # Update general settings
        if "general" in config_data:
            for key, value in config_data["general"].items():
                if hasattr(settings.general, key):
                    setattr(settings.general, key, value)
        
        # Update zidoo settings
        if "zidoo" in config_data:
            for key, value in config_data["zidoo"].items():
                # 跳过端口设置，因为端口固定为9529
                if key == "port":
                    continue
                if hasattr(settings.zidoo, key):
                    setattr(settings.zidoo, key, value)
        
        # Update notification settings
        if "notification" in config_data:
            for key, value in config_data["notification"].items():
                if hasattr(settings.notification, key):
                    setattr(settings.notification, key, value)
        
        # Update extension monitoring settings
        if "extension_monitoring" in config_data:
            for key, value in config_data["extension_monitoring"].items():
                if hasattr(settings.extension_monitoring, key):
                    setattr(settings.extension_monitoring, key, value)
        
        # Save configuration
        settings.save_to_file()
        
        logger.info("Configuration updated")
        return {"success": True, "message": "Configuration updated"}
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {e}")

# Extension monitoring endpoints
@api_router.get("/extension-monitoring", response_model=Dict[str, Any])
async def get_extension_monitoring():
    """Get extension monitoring configuration"""
    return settings.extension_monitoring.model_dump()

@api_router.put("/extension-monitoring", response_model=Dict[str, Any])
async def update_extension_monitoring(extension_data: Dict[str, bool]):
    """Update extension monitoring configuration"""
    try:
        for key, value in extension_data.items():
            if hasattr(settings.extension_monitoring, key):
                setattr(settings.extension_monitoring, key, value)
        
        # Save configuration
        settings.save_to_file()
        
        logger.info("Extension monitoring configuration updated")
        return {"success": True, "message": "扩展名监控配置已更新"}
        
    except Exception as e:
        logger.error(f"Error updating extension monitoring configuration: {e}")
        raise HTTPException(status_code=500, detail=f"更新扩展名监控配置时出错: {e}")

# Path mapping endpoints
@api_router.get("/mappings", response_model=List[Dict[str, Any]])
async def get_path_mappings():
    """Get all path mappings"""
    path_mapper = PathMapper()
    return path_mapper.get_all_mappings()

@api_router.post("/mappings", response_model=Dict[str, Any])
async def add_path_mapping(mapping: Dict[str, Any]):
    """Add a new path mapping"""
    try:
        path_mapper = PathMapper()
        enable = mapping.get("enable", True)
        path_mapper.add_mapping(mapping["source"], mapping["target"], enable)
        settings.save_to_file()
        
        logger.info(f"路径映射已添加: {mapping['source']} -> {mapping['target']}")
        return {"success": True, "message": "路径映射已添加"}
        
    except Exception as e:
        logger.error(f"添加路径映射时出错: {e}")
        raise HTTPException(status_code=500, detail=f"添加路径映射时出错: {e}")

@api_router.delete("/mappings", response_model=Dict[str, Any])
async def remove_path_mapping(mapping: Dict[str, str]):
    """Remove a path mapping"""
    try:
        path_mapper = PathMapper()
        path_mapper.remove_mapping(mapping["source"], mapping["target"])
        settings.save_to_file()
        
        logger.info(f"路径映射已删除: {mapping['source']} -> {mapping['target']}")
        return {"success": True, "message": "路径映射已删除"}
        
    except Exception as e:
        logger.error(f"删除路径映射时出错: {e}")
        raise HTTPException(status_code=500, detail=f"删除路径映射时出错: {e}")

@api_router.put("/mappings/toggle", response_model=Dict[str, Any])
async def toggle_path_mapping(mapping: Dict[str, Any]):
    """Toggle path mapping enable/disable status"""
    try:
        path_mapper = PathMapper()
        path_mapper.toggle_mapping(mapping["source"], mapping["target"], mapping["enable"])
        settings.save_to_file()
        
        status = "启用" if mapping["enable"] else "禁用"
        logger.info(f"路径映射状态已切换: {mapping['source']} -> {mapping['target']} ({status})")
        return {"success": True, "message": f"路径映射已{status}"}
        
    except Exception as e:
        logger.error(f"切换路径映射状态时出错: {e}")
        raise HTTPException(status_code=500, detail=f"切换路径映射状态时出错: {e}")

# Callback endpoint for external services
@api_router.post("/toggle_service", response_model=ToggleServiceResponse)
async def toggle_service(request: ToggleServiceRequest):
    """Toggle service based on external request"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    if request.serviceName != "filewatcher":
        return ToggleServiceResponse(
            success=False,
            message=f"未知服务: {request.serviceName}",
            service_status="unknown"
        )
    
    try:
        if request.action == "start":
            await watcher_service.start()
            service_status = "running"
            message = "服务已启动"
        elif request.action == "stop":
            await watcher_service.stop()
            service_status = "stopped"
            message = "服务已停止"
        else:
            return ToggleServiceResponse(
                success=False,
                message=f"无效操作: {request.action}",
                service_status="error"
            )
        
        logger.info(f"通过回调切换服务: {request.action}")
        return ToggleServiceResponse(
            success=True,
            message=message,
            service_status=service_status
        )
        
    except Exception as e:
        logger.error(f"切换服务时出错: {e}")
        return ToggleServiceResponse(
            success=False,
            message=f"切换服务时出错: {e}",
            service_status="error"
        )

# Health check endpoint
@api_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": None,  # Will be set by frontend
        "version": "1.0.0"
    } 

# New polling endpoints
@api_router.get("/logs/recent", response_model=Dict[str, Any])
async def get_recent_logs(
    since_id: Optional[int] = Query(0, description="Get logs since this ID"), 
    limit: Optional[int] = Query(50, description="Maximum number of logs to return")
):
    """Get recent logs for polling"""
    try:
        if since_id:
            logs = log_buffer.get_logs_since(since_id)
        else:
            logs = log_buffer.get_latest_logs(limit)
        
        return {
            "success": True,
            "logs": logs,
            "latest_id": logs[-1]["id"] if logs else 0
        }
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting logs: {e}")

@api_router.get("/status/current", response_model=Dict[str, Any])
async def get_current_status():
    """Get current player and service status for polling"""
    if not watcher_service:
        raise HTTPException(status_code=500, detail="监控服务未初始化")
    
    try:
        # Get service status
        service_status = watcher_service.get_status()
        
        # Get current player status (direct call, not cached)
        player_status = getattr(watcher_service, 'last_status', None)
        
        return {
            "success": True,
            "service_status": service_status,
            "current_status": player_status,
            "timestamp": time.time()  # 使用UTC时间戳
        }
    except Exception as e:
        logger.error(f"Error getting current status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {e}")

@api_router.post("/logs/clear", response_model=Dict[str, Any])
async def clear_logs():
    """Clear all logs"""
    try:
        log_buffer.clear()
        logger.info("Logs cleared")
        return {"success": True, "message": "Logs cleared"}
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {e}") 