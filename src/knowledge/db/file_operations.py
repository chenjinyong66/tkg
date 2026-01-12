from src.knowledge.db.connection import KnowledgeBaseDB
from src.utils import logger
import json
from typing import List, Dict, Optional
import asyncio
import concurrent.futures
import threading


class FileDAO:
    def __init__(self, db: KnowledgeBaseDB):
        self.db = db

    async def create_file(self, file_id: str, kb_id: str, filename: str,
                          path: str = None, file_type: str = None,
                          content_hash: str = None, size: int = 0,
                          is_folder: bool = False, parent_id: str = None) -> bool:
        """创建文件记录"""
        try:
            with self.db.get_cursor() as cursor:
                sql = """
                INSERT INTO kb_files 
                (id, kb_id, filename, path, file_type, content_hash, size, is_folder, parent_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    file_id, kb_id, filename, path, file_type,
                    content_hash, size, is_folder, parent_id
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to create file {file_id}: {e}")
            return False

    def create_file_sync(self, file_id: str, kb_id: str, filename: str,
                         path: str = None, file_type: str = None,
                         content_hash: str = None, size: int = 0,
                         is_folder: bool = False, parent_id: str = None) -> bool:
        """同步版本的创建文件记录方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.create_file(file_id, kb_id, filename, path, file_type, content_hash, size, is_folder, parent_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def update_file_status(self, file_id: str, status: str, error_message: str = None) -> bool:
        """更新文件状态"""
        try:
            with self.db.get_cursor() as cursor:
                if error_message:
                    sql = "UPDATE kb_files SET status = %s, error_message = %s, updated_at = NOW() WHERE id = %s"
                    cursor.execute(sql, (status, error_message, file_id))
                else:
                    sql = "UPDATE kb_files SET status = %s, updated_at = NOW() WHERE id = %s"
                    cursor.execute(sql, (status, file_id))
                return True
        except Exception as e:
            logger.error(f"Failed to update file status {file_id}: {e}")
            return False

    def update_file_status_sync(self, file_id: str, status: str, error_message: str = None) -> bool:
        """同步版本的更新文件状态方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.update_file_status(file_id, status, error_message))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    def update_file_parent_sync(self, file_id: str, parent_id: str) -> bool:
        """同步版本的更新文件父级方法"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "UPDATE kb_files SET parent_id = %s, updated_at = NOW() WHERE id = %s"
                cursor.execute(sql, (parent_id, file_id))
                return True
        except Exception as e:
            logger.error(f"Failed to update file parent {file_id}: {e}")
            return False

    async def get_files_by_kb_id(self, kb_id: str) -> List[Dict]:
        """根据知识库ID获取文件列表"""
        try:
            with self.db.get_cursor() as cursor:
                sql = """
                SELECT * FROM kb_files 
                WHERE kb_id = %s AND (parent_id IS NULL OR parent_id = '')
                ORDER BY created_at DESC
                """
                cursor.execute(sql, (kb_id,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            logger.error(f"Failed to get files for kb_id {kb_id}: {e}")
            return []

    def get_files_by_kb_id_sync(self, kb_id: str) -> List[Dict]:
        """同步版本的根据知识库ID获取文件列表方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_files_by_kb_id(kb_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    def get_folder_children_sync(self, db_id: str, folder_id: str) -> List[str]:
        """同步版本的获取文件夹子项方法"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "SELECT id FROM kb_files WHERE kb_id = %s AND parent_id = %s"
                cursor.execute(sql, (db_id, folder_id))
                results = cursor.fetchall()
                return [row['id'] for row in results]
        except Exception as e:
            logger.error(f"Failed to get folder children for folder {folder_id}: {e}")
            return []

    async def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """根据ID获取文件信息"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "SELECT * FROM kb_files WHERE id = %s"
                cursor.execute(sql, (file_id,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None

    def get_file_by_id_sync(self, file_id: str) -> Optional[Dict]:
        """同步版本的根据ID获取文件信息方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_file_by_id(file_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def delete_file(self, file_id: str) -> bool:
        """删除文件记录"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "DELETE FROM kb_files WHERE id = %s"
                cursor.execute(sql, (file_id,))
                return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    def delete_file_sync(self, file_id: str) -> bool:
        """同步版本的删除文件记录方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.delete_file(file_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def get_file_basic_info(self, file_id: str) -> Optional[Dict]:
        """获取文件基本信息"""
        try:
            with self.db.get_cursor() as cursor:
                sql = """
                SELECT id, filename, path, file_type, size, status, created_at, updated_at, error_message
                FROM kb_files WHERE id = %s
                """
                cursor.execute(sql, (file_id,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"Failed to get file basic info {file_id}: {e}")
            return None

    def get_file_basic_info_sync(self, file_id: str) -> Optional[Dict]:
        """同步版本的获取文件基本信息方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_file_basic_info(file_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def get_file_content(self, file_id: str) -> Optional[Dict]:
        """获取文件内容信息（chunks和lines）"""
        try:
            with self.db.get_cursor() as cursor:
                # 获取文件的文本块信息
                sql = """
                SELECT id, content, chunk_index, chunk_metadata
                FROM kb_file_chunks 
                WHERE file_id = %s 
                ORDER BY chunk_index
                """
                cursor.execute(sql, (file_id,))
                chunks = cursor.fetchall()

                content_info = {"lines": []}
                for chunk in chunks:
                    chunk_data = {
                        "id": chunk["id"],
                        "content": chunk["content"],
                        "chunk_order_index": chunk["chunk_index"],
                        "metadata": json.loads(chunk["chunk_metadata"]) if chunk["chunk_metadata"] else {}
                    }
                    content_info["lines"].append(chunk_data)

                return content_info
        except Exception as e:
            logger.error(f"Failed to get file content {file_id}: {e}")
            return {"lines": []}

    def get_file_content_sync(self, file_id: str) -> Optional[Dict]:
        """同步版本的获取文件内容信息方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_file_content(file_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()