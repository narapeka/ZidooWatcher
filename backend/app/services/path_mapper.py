from typing import Optional, Tuple
from app.core.config import settings
from app.core.logger import logger
import os

class PathMapper:
    def __init__(self):
        pass  # 不再在初始化时读取配置
    
    def _normalize_path(self, path: str) -> str:
        """
        标准化路径，确保路径格式一致
        - 统一使用正斜杠
        - 移除多余的斜杠
        """
        if not path:
            return path
        
        # 统一使用正斜杠
        normalized = path.replace('\\', '/')
        
        # 移除多余的斜杠
        while '//' in normalized:
            normalized = normalized.replace('//', '/')
        
        return normalized
    
    def _ensure_trailing_slash(self, path: str, is_directory: bool = True) -> str:
        """
        确保路径末尾有斜杠（如果是目录）
        """
        if not path:
            return path
        
        normalized = self._normalize_path(path)
        
        if is_directory and not normalized.endswith('/'):
            normalized += '/'
        elif not is_directory and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        
        return normalized
    
    def _smart_path_replace(self, original_path: str, source: str, target: str) -> str:
        """
        智能路径替换，处理斜杠兼容性问题
        支持多种斜杠组合的自动匹配和修复
        """
        # 标准化所有路径
        original_normalized = self._normalize_path(original_path)
        source_normalized = self._normalize_path(source)
        target_normalized = self._normalize_path(target)
        
        logger.debug(f"标准化路径: 原始={original_normalized}, 源={source_normalized}, 目标={target_normalized}")
        
        # 生成所有可能的源路径变体
        source_variants = []
        
        # 1. 原始标准化路径
        source_variants.append(source_normalized)
        
        # 2. 带末尾斜杠的版本
        if not source_normalized.endswith('/'):
            source_variants.append(source_normalized + '/')
        
        # 3. 不带末尾斜杠的版本
        if source_normalized.endswith('/'):
            source_variants.append(source_normalized.rstrip('/'))
        
        # 4. 处理原始路径中可能缺少斜杠的情况
        # 例如：/storage/emulated/0/CloudDrive/115电影 -> /storage/emulated/0/CloudDrive/115/电影
        if '/' in source_normalized:
            parts = source_normalized.split('/')
            if len(parts) > 1:
                # 尝试在最后一个目录后添加斜杠
                base_path = '/'.join(parts[:-1])
                last_part = parts[-1]
                if last_part and not last_part.endswith('/'):
                    # 检查是否原始路径中缺少了斜杠
                    potential_missing_slash = base_path + '/' + last_part + '/'
                    source_variants.append(potential_missing_slash)
        
        # 确保目标路径有末尾斜杠
        if not target_normalized.endswith('/'):
            target_normalized += '/'
        
        # 尝试所有源路径变体
        for source_variant in source_variants:
            if original_normalized.startswith(source_variant):
                remaining_path = original_normalized[len(source_variant):]
                
                # 确保remaining_path格式正确
                if remaining_path and not remaining_path.startswith('/'):
                    remaining_path = '/' + remaining_path
                
                # 构建最终结果，避免双斜杠
                if target_normalized.endswith('/') and remaining_path.startswith('/'):
                    # 如果目标路径以斜杠结尾，remaining_path也以斜杠开头，则移除一个斜杠
                    result = target_normalized + remaining_path[1:]
                else:
                    result = target_normalized + remaining_path
                
                logger.debug(f"路径替换成功: {original_normalized} -> {result} (使用变体: {source_variant})")
                return result
        
        # 特殊处理：检查是否原始路径中缺少了斜杠
        # 例如：/storage/emulated/0/CloudDrive/115电影/... -> /storage/emulated/0/CloudDrive/115/电影/...
        if '/' in source_normalized:
            parts = source_normalized.split('/')
            if len(parts) > 1:
                base_path = '/'.join(parts[:-1])
                last_part = parts[-1]
                
                # 检查原始路径是否在base_path后直接跟着last_part（缺少斜杠）
                potential_pattern = base_path + '/' + last_part
                if original_normalized.startswith(potential_pattern):
                    # 找到匹配，需要插入斜杠
                    remaining_path = original_normalized[len(potential_pattern):]
                    if remaining_path and not remaining_path.startswith('/'):
                        remaining_path = '/' + remaining_path
                    
                    # 构建最终结果，避免双斜杠
                    if target_normalized.endswith('/') and remaining_path.startswith('/'):
                        # 如果目标路径以斜杠结尾，remaining_path也以斜杠开头，则移除一个斜杠
                        result = target_normalized + remaining_path[1:]
                    else:
                        result = target_normalized + remaining_path
                    
                    logger.debug(f"路径替换（修复缺少斜杠）: {original_normalized} -> {result}")
                    return result
        
        logger.debug(f"未找到匹配的路径映射: {original_normalized}")
        return None

    def _get_current_mappings(self):
        """获取当前最新的路径映射配置 - 直接从内存读取，不重新加载文件"""
        return settings.mapping_paths
    
    def _sort_mappings(self, mappings):
        """Sort mappings: media type first, then strm type"""
        def sort_key(mapping):
            # media = 0, strm = 1 (so media comes first)
            return 0 if mapping.mapping_type == "media" else 1
        
        return sorted(mappings, key=sort_key)

    def check_path_mapping_status(self, original_path: str) -> Tuple[Optional[str], str]:
        """
        Check path mapping status and return detailed information
        Only uses media type mappings (mapping_type == "media")
        Returns: (mapped_path, status_message)
        """
        if not original_path:
            return None, "路径为空"
            
        logger.debug(f"检查路径映射状态: {original_path}")
        
        # 每次检查时都重新获取最新配置
        current_mappings = self._get_current_mappings()
        disabled_matches = []
        
        for mapping in current_mappings:
            # Only process media type mappings
            if mapping.mapping_type != "media":
                continue
                
            source = mapping.source
            target = mapping.target
            
            if not target:
                continue
            
            # 使用智能路径替换
            mapped_path = self._smart_path_replace(original_path, source, target)
            
            if mapped_path is not None:
                if mapping.enable:
                    # Found enabled mapping
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

    def add_mapping(self, source: str, mapping_type: str = "media", target: Optional[str] = None, 
                    enable: bool = True):
        """Add a new path mapping
        
        Args:
            source: Source path (Zidoo path)
            mapping_type: Type of mapping - "media" or "strm"
            target: Target path - for media: BlurayPoster path; for STRM: actual file system path
            enable: Whether the mapping is enabled
        """
        from app.core.config import PathMapping
        
        if not target:
            raise ValueError("Target path is required")
        
        new_mapping = PathMapping(source=source, mapping_type=mapping_type, target=target, enable=enable)
        
        if mapping_type == "media":
            logger.info(f"已添加媒体路径映射: {source} -> {target} (启用: {enable})")
        elif mapping_type == "strm":
            logger.info(f"已添加STRM路径映射: {source} -> {target} (启用: {enable})")
        else:
            raise ValueError(f"Invalid mapping_type: {mapping_type}. Must be 'media' or 'strm'")
        
        current_mappings = self._get_current_mappings()
        current_mappings.append(new_mapping)
        # Sort mappings: media first, then strm
        sorted_mappings = self._sort_mappings(current_mappings)
        settings.mapping_paths = sorted_mappings
    
    def remove_mapping(self, source: str, mapping_type: Optional[str] = None, 
                      target: Optional[str] = None):
        """Remove a path mapping
        
        Args:
            source: Source path
            mapping_type: Type of mapping (optional, for more precise matching)
            target: Target path (optional, for more precise matching)
        """
        current_mappings = self._get_current_mappings()
        # 使用智能匹配，不依赖精确的路径格式
        for i, mapping in enumerate(current_mappings):
            # Match by source first
            if self._normalize_path(mapping.source) != self._normalize_path(source):
                continue
            
            # If mapping_type is provided, match it
            if mapping_type and mapping.mapping_type != mapping_type:
                continue
            
            # Match by target if provided
            if target and self._normalize_path(mapping.target or "") == self._normalize_path(target):
                del current_mappings[i]
                settings.mapping_paths = current_mappings
                logger.info(f"已删除路径映射: {source} -> {target}")
                return
        
        logger.warning(f"未找到路径映射: {source}")
    
    def update_mapping(self, old_source: str, old_mapping_type: Optional[str] = None, 
                      old_target: Optional[str] = None,
                      new_source: Optional[str] = None, new_target: Optional[str] = None):
        """Update a path mapping in place (preserves order)
        
        Args:
            old_source: Original source path (for finding the mapping)
            old_mapping_type: Original mapping type (optional, for more precise matching)
            old_target: Original target path (optional, for more precise matching)
            new_source: New source path (if None, keeps original)
            new_target: New target path (if None, keeps original)
        """
        from app.core.config import PathMapping
        
        current_mappings = self._get_current_mappings()
        # 使用智能匹配，不依赖精确的路径格式
        for i, mapping in enumerate(current_mappings):
            # Match by source first
            if self._normalize_path(mapping.source) != self._normalize_path(old_source):
                continue
            
            # If mapping_type is provided, match it
            if old_mapping_type and mapping.mapping_type != old_mapping_type:
                continue
            
            # Match by target if provided
            if old_target and self._normalize_path(mapping.target or "") != self._normalize_path(old_target):
                continue
            
            # Found the mapping - update it in place
            updated_source = new_source if new_source is not None else mapping.source
            updated_target = new_target if new_target is not None else mapping.target
            
            if not updated_target:
                raise ValueError("Target path cannot be empty")
            
            # Update the mapping in place
            mapping.source = updated_source
            mapping.target = updated_target
            # mapping_type and enable remain unchanged
            
            # Re-sort to maintain order (in case type changed, though it shouldn't)
            sorted_mappings = self._sort_mappings(current_mappings)
            settings.mapping_paths = sorted_mappings
            logger.info(f"已更新路径映射: {old_source} -> {updated_source}")
            return
        
        logger.warning(f"未找到路径映射: {old_source}")
    
    def toggle_mapping(self, source: str, mapping_type: Optional[str] = None,
                      target: Optional[str] = None, enable: bool = True):
        """Toggle mapping enable/disable status
        
        Args:
            source: Source path
            mapping_type: Type of mapping (optional, for more precise matching)
            target: Target path (optional, for more precise matching)
            enable: Enable/disable status
        """
        current_mappings = self._get_current_mappings()
        # 使用智能匹配，不依赖精确的路径格式
        for mapping in current_mappings:
            # Match by source first
            if self._normalize_path(mapping.source) != self._normalize_path(source):
                continue
            
            # If mapping_type is provided, match it
            if mapping_type and mapping.mapping_type != mapping_type:
                continue
            
            # Match by target if provided
            if target and self._normalize_path(mapping.target or "") == self._normalize_path(target):
                mapping.enable = enable
                settings.mapping_paths = current_mappings
                logger.info(f"路径映射状态已切换: {source} -> {target} (启用: {enable})")
                return
        
        logger.warning(f"未找到路径映射: {source}")
    
    def get_all_mappings(self):
        """Get all current path mappings (sorted: media first, then strm)"""
        current_mappings = self._get_current_mappings()
        # Ensure mappings are sorted
        sorted_mappings = self._sort_mappings(current_mappings)
        return [{
            "source": m.source, 
            "mapping_type": m.mapping_type,
            "target": m.target, 
            "enable": m.enable
        } for m in sorted_mappings]
    
    def map_to_strm_path(self, zidoo_path: str) -> Optional[str]:
        """
        Map Zidoo-specific path to actual file system path for reading .strm files
        Only uses STRM type mappings (mapping_type == "strm")
        For STRM mappings, the target field contains the actual file system path
        
        Args:
            zidoo_path: Path from Zidoo API (Zidoo-specific)
            
        Returns:
            Actual file system path if mapping found, None otherwise
        """
        if not zidoo_path:
            return None
        
        logger.debug(f"Mapping Zidoo path to STRM file system path: {zidoo_path}")
        
        current_mappings = self._get_current_mappings()
        
        for mapping in current_mappings:
            # Only process STRM type mappings
            if mapping.mapping_type != "strm":
                continue
                
            if not mapping.enable:
                continue
            
            if not mapping.target:
                continue
            
            source = mapping.source
            strm_path = mapping.target  # For STRM mappings, target contains the STRM file system path
            
            # Use smart path replace to map source -> strm_path
            mapped_path = self._smart_path_replace(zidoo_path, source, strm_path)
            
            if mapped_path is not None:
                logger.info(f"STRM路径已映射: {zidoo_path} -> {mapped_path}")
                return mapped_path
        
        logger.debug(f"未找到STRM路径映射: {zidoo_path}")
        return None 