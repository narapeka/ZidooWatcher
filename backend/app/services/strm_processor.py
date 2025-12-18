import os
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote
from app.core.config import settings
from app.core.logger import logger
from app.core.log_buffer import log_buffer
from app.services.path_mapper import PathMapper

class StrmProcessor:
    """Service to extract real media file paths from .strm files"""
    
    def __init__(self, path_mapper: Optional[PathMapper] = None):
        """Initialize StrmProcessor with optional PathMapper for path translation"""
        self.path_mapper = path_mapper or PathMapper()
    
    def extract_real_path(self, zidoo_strm_path: str) -> Optional[str]:
        """
        Extract the real media file path from a .strm file
        
        First maps Zidoo-specific path to actual file system path using path_mapper,
        then reads the .strm file and extracts the real media path.
        
        Case 1: Content starts with /mnt/ -> return content directly as real path
        Case 2: Content starts with http:// -> parse URL, extract file_path parameter,
                URL decode it, and merge with clouddrive.mount_path
        
        Args:
            zidoo_strm_path: Zidoo-specific path to the .strm file (from Zidoo API)
            
        Returns:
            Real media file path if extraction succeeds, None otherwise
        """
        if not zidoo_strm_path:
            logger.warning("STRM path is empty")
            return None
        
        # First, map Zidoo path to actual file system path
        actual_strm_path = self.path_mapper.map_to_strm_path(zidoo_strm_path)
        if not actual_strm_path:
            # If no mapping found, try using the original path directly
            actual_strm_path = zidoo_strm_path
            logger.debug(f"未找到STRM路径映射，使用原始路径: {zidoo_strm_path}")
        else:
            logger.debug(f"STRM路径已映射: {zidoo_strm_path} -> {actual_strm_path}")
        
        try:
            # Read strm file content from actual file system path
            if not os.path.exists(actual_strm_path):
                logger.warning(f"STRM file not found: {actual_strm_path} (原始路径: {zidoo_strm_path})")
                return None
            
            with open(actual_strm_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Log STRM file content to UI
            log_buffer.add_log(f"检测到STRM文件内容: {content}", "INFO")
            
            if not content:
                logger.warning(f"STRM file is empty: {actual_strm_path}")
                return None
            
            # Case 1: Content starts with /mnt/
            if content.startswith('/mnt/'):
                logger.debug(f"STRM file contains /mnt/ path: {content}")
                return content
            
            # Case 2: Content starts with http://
            if content.startswith('http://'):
                logger.debug(f"STRM file contains HTTP URL: {content}")
                return self._extract_path_from_url(content)
            
            # Content doesn't match either case
            logger.warning(f"STRM file content doesn't match Case 1 (/mnt/) or Case 2 (http://): {content[:100]}")
            return None
            
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode STRM file {actual_strm_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading STRM file {actual_strm_path}: {e}")
            return None
    
    def _extract_path_from_url(self, url: str) -> Optional[str]:
        """
        Extract file_path from HTTP URL and merge with mount_path
        
        Args:
            url: HTTP URL from strm file content
            
        Returns:
            Merged path if successful, None otherwise
        """
        try:
            # Parse URL
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Extract file_path parameter
            if 'file_path' not in query_params:
                logger.warning(f"file_path parameter not found in URL: {url[:100]}")
                return None
            
            file_path_param = query_params['file_path'][0]
            
            # URL decode the file_path
            decoded_file_path = unquote(file_path_param)
            
            # Get mount_path from settings
            mount_path = settings.clouddrive.mount_path
            if not mount_path:
                logger.warning("clouddrive.mount_path is not configured")
                return None
            
            # Merge mount_path with decoded file_path
            # Handle leading/trailing slashes
            mount_path_normalized = mount_path.rstrip('/')
            file_path_normalized = decoded_file_path.lstrip('/')
            
            merged_path = f"{mount_path_normalized}/{file_path_normalized}"
            
            logger.debug(f"Merged path: {merged_path}")
            return merged_path
            
        except Exception as e:
            logger.error(f"Error extracting path from URL: {e}")
            return None
