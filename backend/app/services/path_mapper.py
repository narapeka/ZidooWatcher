from typing import Optional, Tuple
from app.core.config import settings
from app.core.logger import logger

class PathMapper:
    def __init__(self):
        self.mappings = settings.mapping_paths
    

    
    def check_path_mapping_status(self, original_path: str) -> Tuple[Optional[str], str]:
        """
        Check path mapping status and return detailed information
        Returns: (mapped_path, status_message)
        """
        if not original_path:
            return None, "路径为空"
            
        logger.debug(f"检查路径映射状态: {original_path}")
        
        disabled_matches = []
        
        for mapping in self.mappings:
            source = mapping.source
            target = mapping.target
            
            if original_path.startswith(source):
                if mapping.enable:
                    # Found enabled mapping
                    mapped_path = original_path.replace(source, target, 1)
                    logger.info(f"路径已映射: {original_path} -> {mapped_path}")
                    return mapped_path, f"成功映射: {source} -> {target}"
                else:
                    # Found disabled mapping
                    disabled_matches.append(source)
        
        # No enabled mapping found
        if disabled_matches:
            # Found disabled mappings
            disabled_sources = ", ".join(disabled_matches)
            status_msg = f"路径映射 {disabled_sources} 已禁用，跳过处理"
            logger.warning(f"路径映射已禁用: {original_path} (匹配的禁用映射: {disabled_sources})")
        else:
            # No mappings found at all
            status_msg = f"未找到匹配的路径映射"
            logger.warning(f"未找到路径映射: {original_path}")
            
        return None, status_msg

    def add_mapping(self, source: str, target: str, enable: bool = True):
        """Add a new path mapping"""
        from app.core.config import PathMapping
        new_mapping = PathMapping(source=source, target=target, enable=enable)
        self.mappings.append(new_mapping)
        settings.mapping_paths = self.mappings
        logger.info(f"已添加路径映射: {source} -> {target} (启用: {enable})")
    
    def remove_mapping(self, source: str, target: str):
        """Remove a path mapping"""
        for i, mapping in enumerate(self.mappings):
            if mapping.source == source and mapping.target == target:
                del self.mappings[i]
                settings.mapping_paths = self.mappings
                logger.info(f"已删除路径映射: {source} -> {target}")
                return
        logger.warning(f"未找到路径映射: {source} -> {target}")
    
    def toggle_mapping(self, source: str, target: str, enable: bool):
        """Toggle mapping enable/disable status"""
        for mapping in self.mappings:
            if mapping.source == source and mapping.target == target:
                mapping.enable = enable
                settings.mapping_paths = self.mappings
                logger.info(f"路径映射状态已切换: {source} -> {target} (启用: {enable})")
                return
        logger.warning(f"未找到路径映射: {source} -> {target}")
    
    def get_all_mappings(self):
        """Get all current path mappings"""
        return [{"source": m.source, "target": m.target, "enable": m.enable} for m in self.mappings] 