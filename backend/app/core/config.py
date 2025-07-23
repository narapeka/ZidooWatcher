import yaml
import os
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

class GeneralConfig(BaseModel):
    heart_rate: int = 500
    log_level: str = "DEBUG"

class ZidooConfig(BaseModel):
    ip: str = "192.168.1.99"
    port: int = 9529
    api_path: str = "/ZidooVideoPlay/getPlayStatus"

class PathMapping(BaseModel):
    source: str
    target: str
    enable: bool = True  # 默认启用

class NotificationConfig(BaseModel):
    endpoint: str = "http://192.168.1.50:7507/play"
    timeout_seconds: int = 10

class Settings(BaseModel):
    general: GeneralConfig = GeneralConfig()
    zidoo: ZidooConfig = ZidooConfig()
    mapping_paths: List[PathMapping] = []
    notification: NotificationConfig = NotificationConfig()

    @classmethod
    def load_from_file(cls, config_path: str = None) -> "Settings":
        if config_path is None:
            # 统一配置文件路径
            def get_project_root():
                """获取项目根目录"""
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # 从 backend/app/core/ 向上找到项目根目录
                while current_dir != os.path.dirname(current_dir):
                    if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
                        return current_dir
                    current_dir = os.path.dirname(current_dir)
                return current_dir
            
            if os.path.exists("/config/config.yaml"):
                possible_paths = ["/config/config.yaml"]  # Docker 环境
            else:
                # 开发环境 - 使用项目根目录
                project_root = get_project_root()
                possible_paths = [os.path.join(project_root, "config", "config.yaml")]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            else:
                # Use default settings if no config file found
                return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            return cls()

    def save_to_file(self, config_path: str = None):
        if config_path is None:
            # 统一保存路径
            if os.path.exists("/config"):
                config_path = "/config/config.yaml"  # Docker 环境
            else:
                # 开发环境 - 使用项目根目录
                def get_project_root():
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    while current_dir != os.path.dirname(current_dir):
                        if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
                            return current_dir
                        current_dir = os.path.dirname(current_dir)
                    return current_dir
                
                project_root = get_project_root()
                config_path = os.path.join(project_root, "config", "config.yaml")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.dict(), f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config to {config_path}: {e}")

# Global settings instance
settings = Settings.load_from_file() 