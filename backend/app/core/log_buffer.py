from collections import deque
from typing import List, Dict, Any
import time
import os
import platform
import threading

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

class LogBuffer:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.logs = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.sequence_id = 0
    
    def add_log(self, message: str, level: str = "INFO") -> int:
        """Add a log entry and return its sequence ID"""
        with self.lock:
            self.sequence_id += 1
            log_entry = {
                "id": self.sequence_id,
                "type": "log",
                "level": level,
                "message": message,
                "timestamp": time.time()  # 使用UTC时间戳
            }
            self.logs.append(log_entry)
            return self.sequence_id
    
    def get_logs_since(self, since_id: int = 0) -> List[Dict[str, Any]]:
        """Get all logs since the given sequence ID"""
        with self.lock:
            if since_id == 0:
                # Return last 50 logs for initial load
                return list(self.logs)[-50:]
            
            # Return logs with ID > since_id
            return [log for log in self.logs if log["id"] > since_id]
    
    def get_latest_logs(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get the latest N logs"""
        with self.lock:
            return list(self.logs)[-count:]
    
    def clear(self):
        """Clear all logs"""
        with self.lock:
            self.logs.clear()
            self.sequence_id = 0

# Global log buffer instance
log_buffer = LogBuffer() 