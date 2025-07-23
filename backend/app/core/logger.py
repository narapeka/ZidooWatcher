import sys
import os
from loguru import logger
from app.core.config import settings

# Remove default logger
logger.remove()

# Create config/logs directory if it doesn't exist
# 统一使用项目根目录的config
def get_project_root():
    """获取项目根目录"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从 backend/app/core/ 向上找到项目根目录
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return current_dir

if os.path.exists("/config"):
    logs_dir = "/config/logs"     # Docker 环境
else:
    # 开发环境 - 使用项目根目录的config
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, "config", "logs")

os.makedirs(logs_dir, exist_ok=True)

# Add console logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.general.log_level,
    colorize=True
)

# Add file logger with daily rotation and 7-day retention
logger.add(
    f"{logs_dir}/zidoo_watcher_{{time:YYYY-MM-DD}}.log",
    rotation="00:00",  # Rotate at midnight
    retention="7 days",  # Keep logs for 7 days
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.general.log_level,
    encoding="utf-8",
    compression="zip"  # Compress old log files
) 