"""
文件类型验证工具模块
用于验证上传的文档是否符合配置的允许类型
"""
import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class FileTypeValidator:
    """文件类型验证器"""
    
    def __init__(self, allowed_types: str):
        """
        初始化文件类型验证器
        
        Args:
            allowed_types: 允许的文件类型配置字符串
                          - "*" 或空字符串：允许所有类型
                          - 逗号分隔的扩展名：如 ".pdf,.zip,.rar"
                          - 逗号分隔的MIME类型：如 "application/pdf,application/zip"
                          - 混合格式：如 ".pdf,application/zip,.rar"
        """
        self.allowed_types = allowed_types.strip() if allowed_types else "*"
        self.allow_all = self.allowed_types == "*" or self.allowed_types == ""
        
        # 解析允许的类型
        self.allowed_extensions = set()
        self.allowed_mime_types = set()
        
        if not self.allow_all:
            types_list = [t.strip().lower() for t in self.allowed_types.split(',') if t.strip()]
            for t in types_list:
                if t.startswith('.'):
                    # 文件扩展名
                    self.allowed_extensions.add(t)
                elif '/' in t:
                    # MIME类型
                    self.allowed_mime_types.add(t)
                else:
                    # 没有点的扩展名，自动添加点
                    self.allowed_extensions.add(f".{t}")
        
        logger.info(f"文件类型验证器初始化完成:")
        logger.info(f"  - 允许所有类型: {self.allow_all}")
        logger.info(f"  - 允许的扩展名: {self.allowed_extensions}")
        logger.info(f"  - 允许的MIME类型: {self.allowed_mime_types}")
    
    def validate(self, file_name: Optional[str], mime_type: Optional[str]) -> Tuple[bool, str]:
        """
        验证文件是否符合允许的类型
        
        Args:
            file_name: 文件名
            mime_type: MIME类型
            
        Returns:
            Tuple[bool, str]: (是否通过验证, 错误消息或空字符串)
        """
        # 允许所有类型
        if self.allow_all:
            return True, ""
        
        # 获取文件扩展名
        file_ext = ""
        if file_name:
            file_ext = os.path.splitext(file_name.lower())[1]
        
        # 标准化MIME类型
        normalized_mime = mime_type.lower() if mime_type else ""
        
        # 检查扩展名匹配
        if file_ext and file_ext in self.allowed_extensions:
            logger.info(f"文件扩展名匹配: {file_ext}")
            return True, ""
        
        # 检查MIME类型匹配
        if normalized_mime and normalized_mime in self.allowed_mime_types:
            logger.info(f"MIME类型匹配: {normalized_mime}")
            return True, ""
        
        # 检查MIME类型通配符匹配（如 image/* 匹配 image/png）
        if normalized_mime:
            for allowed_mime in self.allowed_mime_types:
                if allowed_mime.endswith('/*'):
                    prefix = allowed_mime[:-2]
                    if normalized_mime.startswith(prefix + '/'):
                        logger.info(f"MIME类型通配符匹配: {allowed_mime} -> {normalized_mime}")
                        return True, ""
        
        # 验证失败，生成错误消息
        error_msg = self._generate_error_message(file_name, mime_type)
        logger.warning(f"文件类型验证失败: 文件名={file_name}, MIME={mime_type}")
        return False, error_msg
    
    def _generate_error_message(self, file_name: Optional[str], mime_type: Optional[str]) -> str:
        """
        生成用户友好的错误消息
        
        Args:
            file_name: 文件名
            mime_type: MIME类型
            
        Returns:
            str: 错误消息
        """
        file_info = []
        if file_name:
            file_info.append(f"文件: {file_name}")
        if mime_type:
            file_info.append(f"类型: {mime_type}")
        
        file_info_str = "，".join(file_info) if file_info else "未知文件"
        
        # 生成允许的类型列表
        allowed_types_display = []
        if self.allowed_extensions:
            ext_list = sorted(self.allowed_extensions)
            allowed_types_display.append(f"扩展名: {', '.join(ext_list)}")
        if self.allowed_mime_types:
            mime_list = sorted(self.allowed_mime_types)
            allowed_types_display.append(f"MIME类型: {', '.join(mime_list)}")
        
        allowed_str = "\n".join(allowed_types_display) if allowed_types_display else "无"
        
        return (
            f"❌ 不支持的文件类型\n\n"
            f"📄 {file_info_str}\n\n"
            f"✅ 允许的文件类型：\n{allowed_str}"
        )
    
    def get_allowed_types_description(self) -> str:
        """
        获取允许的文件类型的描述信息（用于提示用户）
        
        Returns:
            str: 允许的文件类型描述
        """
        if self.allow_all:
            return "所有文件类型"
        
        descriptions = []
        if self.allowed_extensions:
            ext_list = sorted(self.allowed_extensions)
            descriptions.append(f"• 扩展名: {', '.join(ext_list)}")
        if self.allowed_mime_types:
            mime_list = sorted(self.allowed_mime_types)
            # 简化MIME类型显示
            simplified_mimes = []
            for mime in mime_list:
                if mime.startswith('application/'):
                    simplified_mimes.append(mime.replace('application/', ''))
                else:
                    simplified_mimes.append(mime)
            descriptions.append(f"• 类型: {', '.join(simplified_mimes)}")
        
        return "\n".join(descriptions) if descriptions else "无限制"


def create_file_validator(allowed_types: str) -> FileTypeValidator:
    """
    创建文件类型验证器的工厂函数
    
    Args:
        allowed_types: 允许的文件类型配置字符串
        
    Returns:
        FileTypeValidator: 文件类型验证器实例
    """
    return FileTypeValidator(allowed_types)

