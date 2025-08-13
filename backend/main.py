import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import time
import platform
import logging

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

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.api.routes import api_router
from app.core.logger import logger
from app.services.watcher_service import WatcherService

# Global instances
watcher_service = None

# 禁用uvicorn的访问日志，减少轮询请求的日志输出
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global watcher_service
    
    logger.info("正在启动Zidoo Watcher应用...")
    
    # Initialize Watcher service
    watcher_service = WatcherService()
    
    # Initialize global instances for API routes
    import app.api.routes as api_routes
    api_routes.watcher_service = watcher_service
    
    # Auto-start the watcher service if configured
    if settings.general.auto_start:
        logger.info("已配置为自动启动监控服务，正在启动...")
        try:
            await watcher_service.start()
            logger.info("监控服务已自动启动")
        except Exception as e:
            logger.error(f"自动启动监控服务失败: {e}")
    else:
        logger.info("监控服务已准备就绪，请使用前端界面启动/停止服务。")
    
    yield
    
    # Shutdown
    logger.info("正在关闭Zidoo Watcher应用...")
    if watcher_service:
        await watcher_service.stop()

fastapi_app = FastAPI(
    title="Zidoo Watcher",
    description="Zidoo player heartbeat monitoring system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes FIRST (before static files)
fastapi_app.include_router(api_router, prefix="/api")

# Serve frontend static files
frontend_dist = "../frontend/dist"  # 开发环境路径
if not os.path.exists(frontend_dist):
    frontend_dist = "./frontend/dist"  # Docker 环境路径

if os.path.exists(frontend_dist):
    # Mount static files for assets (CSS, JS, images, etc.)
    fastapi_app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # SPA fallback route - 处理所有前端路由
    @fastapi_app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Skip API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Skip static assets (already handled by mount)
        if full_path.startswith("assets/"):
            raise HTTPException(status_code=404, detail="Static file not found")
        
        # For all other routes, serve index.html (SPA routing)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
else:
    logger.warning(f"Frontend dist directory not found: {frontend_dist}")

if __name__ == "__main__":
    uvicorn.run(
        "main:fastapi_app",
        host="0.0.0.0",
        port=7502,
        reload=True,
        log_level="error"  # 改为ERROR级别，只显示错误日志，减少轮询请求的日志输出
    ) 