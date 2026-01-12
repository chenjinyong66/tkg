"""Knowledge Base Database Connection Manager"""

import pymysql
import threading
import time
from contextlib import contextmanager
from pymysql import MySQLError
from pymysql.cursors import DictCursor
from typing import Any

from src.utils import logger


class KnowledgeBaseDB:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        # 使用环境变量或默认值
        self.mysql_config = {
            'host': host or self._get_env_or_default('MYSQL_HOST', 'localhost'),
            'port': port or int(self._get_env_or_default('MYSQL_PORT', 3306)),
            'user': user or self._get_env_or_default('MYSQL_USER', 'root'),
            'password': password or self._get_env_or_default('MYSQL_PASSWORD', '123456'),
            'database': database or self._get_env_or_default('MYSQL_DATABASE', 'talent-test')
        }
        # 创建连接管理器实例
        self.connection_manager = MySQLConnectionManager(self.mysql_config)

    def _get_env_or_default(self, env_key: str, default_value: Any) -> Any:
        """获取环境变量值，如果不存在则返回默认值"""
        import os
        return os.getenv(env_key) or default_value

    def get_connection(self):
        """获取数据库连接"""
        return self.connection_manager.get_connection()

    def get_cursor(self):
        """获取数据库游标"""
        return self.connection_manager.get_cursor()


class MySQLConnectionManager:
    """知识库专用的MySQL数据库连接管理器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.connection = None
        self._lock = threading.Lock()
        self.last_connection_time = 0
        self.max_connection_age = 3600  # 1小时后重新连接

    def _get_connection(self) -> pymysql.Connection:
        """获取数据库连接"""
        current_time = time.time()

        # 检查连接是否过期或断开
        if (
            self.connection is None
            or not self.connection.open
            or current_time - self.last_connection_time > self.max_connection_age
        ):
            with self._lock:
                # 双重检查
                if (
                    self.connection is None
                    or not self.connection.open
                    or current_time - self.last_connection_time > self.max_connection_age
                ):
                    # 关闭旧连接
                    if self.connection and self.connection.open:
                        try:
                            self.connection.close()
                        except Exception as _:
                            pass

                    # 创建新连接
                    self.connection = self._create_connection()
                    self.last_connection_time = current_time

        return self.connection

    def _create_connection(self) -> pymysql.Connection:
        """创建新的数据库连接"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                connection = pymysql.connect(
                    host=self.config["host"],
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"],
                    port=self.config["port"],
                    charset=self.config.get("charset", "utf8mb4"),
                    cursorclass=DictCursor,
                    connect_timeout=10,
                    read_timeout=60,  # 增加读取超时
                    write_timeout=30,
                    autocommit=True,  # 自动提交
                )
                logger.info(f"Knowledge Base MySQL connection established successfully (attempt {attempt + 1})")
                return connection

            except MySQLError as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # 指数退避
                else:
                    logger.error(f"Failed to connect to MySQL after {max_retries} attempts: {e}")
                    raise ConnectionError(f"MySQL connection failed: {e}")

    def test_connection(self) -> bool:
        """测试连接是否有效"""
        try:
            if self.connection and self.connection.open:
                # 执行简单查询测试连接
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                return True
        except Exception as _:
            pass
        return False

    def _invalidate_connection(self, connection: pymysql.Connection | None = None):
        """关闭并清理失效的连接"""
        try:
            if connection:
                connection.close()
        except Exception:
            pass
        finally:
            self.connection = None

    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        max_retries = 2
        cursor = None
        connection = None
        last_error: Exception | None = None

        # 优先确保成功获取游标再交给调用方执行查询
        for attempt in range(max_retries):
            try:
                connection = self._get_connection()
                cursor = connection.cursor()
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to acquire cursor (attempt {attempt + 1}): {e}")
                self._invalidate_connection(connection)
                cursor = None
                connection = None
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)

        if cursor is None or connection is None:
            raise last_error or ConnectionError("Unable to acquire MySQL cursor")

        try:
            yield cursor
            connection.commit()
        except Exception as e:
            try:
                connection.rollback()
            except Exception:
                pass

            # 标记连接失效，等待下一次获取时重建
            if "MySQL" in str(e) or "connection" in str(e).lower():
                logger.warning(f"MySQL connection error encountered, invalidating connection: {e}")
                self._invalidate_connection(connection)

            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Knowledge Base MySQL connection closed")

    def get_connection(self) -> pymysql.Connection:
        """对外暴露的连接获取方法"""
        return self._get_connection()

    def invalidate_connection(self):
        """手动标记连接失效"""
        self._invalidate_connection(self.connection)

    @property
    def database_name(self) -> str:
        """返回当前配置的数据库名称"""
        return self.config["database"]