import yaml
import os
from typing import List, Optional, Literal
from pydantic import BaseModel, model_validator
from pathlib import Path

class GeneralConfig(BaseModel):
    heart_rate: int = 500
    log_level: str = "INFO"
    auto_start: bool = False
    
    def __init__(self, **data):
        super().__init__(**data)
        # 确保心跳频率在安全范围内
        if self.heart_rate < 200:
            self.heart_rate = 200  # 最小200ms
        elif self.heart_rate > 2000:
            self.heart_rate = 2000  # 最大2秒

class ZidooConfig(BaseModel):
    ip: str = "192.168.1.99"
    api_path: str = "/ZidooVideoPlay/getPlayStatus"
    
    @property
    def port(self) -> int:
        """端口固定为9529"""
        return 9529

class PathMapping(BaseModel):
    source: str
    mapping_type: Literal["media", "strm"] = "media"  # Type of mapping: "media" for real media files, "strm" for STRM files
    target: str  # Target path - for media mappings: BlurayPoster path; for STRM mappings: actual file system path to read .strm files
    enable: bool = True  # 默认启用
    
    @model_validator(mode='after')
    def validate_mapping_fields(self):
        """Validate that target is set"""
        if self.target is None or self.target == '':
            raise ValueError('Target path is required')
        return self

class NotificationConfig(BaseModel):
    endpoint: str = "http://192.168.1.50:7507/play"
    timeout_seconds: int = 10

class ExtensionMonitoringConfig(BaseModel):
    bdmv: bool = True
    iso: bool = True
    mkv: bool = False
    mp4: bool = False
    m2ts: bool = False

class CloudDriveConfig(BaseModel):
    mount_path: str = ""

class Settings(BaseModel):
    general: GeneralConfig = GeneralConfig()
    zidoo: ZidooConfig = ZidooConfig()
    mapping_paths: List[PathMapping] = []
    notification: NotificationConfig = NotificationConfig()
    extension_monitoring: ExtensionMonitoringConfig = ExtensionMonitoringConfig()
    clouddrive: CloudDriveConfig = CloudDriveConfig()

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
            
            # Migrate existing path mappings to include mapping_type and consolidate strm into target
            if config_data and 'mapping_paths' in config_data:
                for mapping in config_data['mapping_paths']:
                    # If mapping_type is not set, determine it from existing fields
                    if 'mapping_type' not in mapping:
                        has_target = mapping.get('target') is not None and mapping.get('target') != ''
                        has_strm = mapping.get('strm') is not None and mapping.get('strm') != ''
                        
                        if has_strm:
                            # If strm is set, use it as target and set type to strm
                            mapping['mapping_type'] = 'strm'
                            mapping['target'] = mapping.get('strm')
                        elif has_target:
                            # Only target: media mapping
                            mapping['mapping_type'] = 'media'
                        else:
                            # Neither set: default to media (will fail validation, but better than nothing)
                            mapping['mapping_type'] = 'media'
                    
                    # Remove strm field if it exists (we now use target for both)
                    if 'strm' in mapping:
                        del mapping['strm']
            
            # Sort mappings: media type first, then strm type
            if config_data and 'mapping_paths' in config_data and config_data['mapping_paths']:
                def sort_key(mapping):
                    # media = 0, strm = 1 (so media comes first)
                    mapping_type = mapping.get('mapping_type', 'media')
                    return 0 if mapping_type == 'media' else 1
                
                config_data['mapping_paths'] = sorted(config_data['mapping_paths'], key=sort_key)
            
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
                yaml.dump(self.model_dump(), f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config to {config_path}: {e}")

# Global settings instance
settings = Settings.load_from_file() 