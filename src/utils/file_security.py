"""
文件安全工具模块 - 负责文件安全性检查和清理
"""

import os
import re
from pathlib import Path
from typing import List
from src.knowledge.indexing import SUPPORTED_FILE_EXTENSIONS


class FileSecurityManager:
    """文件安全管理器"""

    @staticmethod
    def is_safe_path(basedir: str, path: str) -> bool:
        """
        检查路径是否安全，防止路径遍历攻击

        Args:
            basedir: 基准目录
            path: 要检查的路径

        Returns:
            bool: 路径是否安全

        Raises:
            ValueError: 路径为空或包含空字符
        """
        if not path:
            return False

        # 检查是否包含空字符
        if '\0' in path:
            return False

        try:
            # 规范化路径
            basedir = os.path.abspath(basedir)
            full_path = os.path.abspath(os.path.join(basedir, path))

            # 检查是否在基准目录内
            if not full_path.startswith(basedir):
                return False

            # 检查是否为符号链接
            if os.path.islink(full_path):
                return False

            # 检查是否为绝对路径
            if os.path.isabs(path):
                return False

            # 检查是否包含父目录引用
            normalized_path = os.path.normpath(path)
            if '..' in normalized_path.split(os.path.sep):
                return False

            # 检查路径中是否包含控制字符
            if any(ord(c) < 32 for c in path):
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除不安全字符

        Args:
            filename: 原始文件名

        Returns:
            str: 清理后的安全文件名
        """
        if not filename:
            return "unnamed_file"

        # 获取文件名部分，移除路径信息
        filename = Path(filename).name

        # 移除控制字符和Unicode控制字符
        filename = ''.join(c for c in filename if ord(c) >= 32 and ord(c) != 127)

        # 移除不安全字符（Windows和Linux文件系统都不允许的字符）
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')

        # 移除连续的空格和下划线
        filename = re.sub(r'[ _]+', '_', filename)

        # 移除首尾的空格、点和下划线
        filename = filename.strip(' ._')

        # 如果文件名为空，使用默认名称
        if not filename:
            filename = "unnamed_file"

        # 限制文件名长度
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext

        return filename

    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: List[str] = None) -> bool:
        """
        验证文件类型

        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名列表，默认为支持的文件类型

        Returns:
            bool: 文件类型是否允许
        """
        if not allowed_extensions:
            allowed_extensions = SUPPORTED_FILE_EXTENSIONS + ['.zip']

        ext = Path(filename).suffix.lower()
        return ext in allowed_extensions

    @staticmethod
    def validate_file_content(file_content: bytes, max_size: int = 100 * 1024 * 1024) -> bool:
        """
        验证文件内容

        Args:
            file_content: 文件内容
            max_size: 最大文件大小（字节）

        Returns:
            bool: 文件内容是否有效
        """
        # 检查文件大小
        if len(file_content) > max_size:
            return False

        # 检查文件是否为空
        if len(file_content) == 0:
            return False

        # 可以添加更多内容检查逻辑，如文件魔数检查等
        return True


# 全局安全管理器实例
file_security_manager = FileSecurityManager()