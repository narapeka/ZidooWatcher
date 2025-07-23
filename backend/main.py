import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
import time
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

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.api.routes import api_router
from app.core.logger import logger
from app.services.watcher_service import WatcherService

# Global instances
watcher_service = None

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
    
    # Don't auto-start the watcher service - let user control it manually
    logger.info("监控服务已准备就绪但未启动。请使用前端界面启动/停止服务。")
    
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

# Include API routes
fastapi_app.include_router(api_router, prefix="/api")

# Serve frontend static files
frontend_dist = "../frontend/dist"  # 开发环境路径
if not os.path.exists(frontend_dist):
    frontend_dist = "./frontend/dist"  # Docker 环境路径

if os.path.exists(frontend_dist):
    fastapi_app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:fastapi_app",
        host="0.0.0.0",
        port=7502,
        reload=True,
        log_level=settings.general.log_level.lower()
    ) 