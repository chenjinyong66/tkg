from src.knowledge.db.connection import KnowledgeBaseDB
from src.utils import logger
import json
import asyncio
import concurrent.futures
import threading


class KnowledgeBaseDAO:
    def __init__(self, db: KnowledgeBaseDB):
        self.db = db

    async def create_knowledge_base(self, kb_id: str, name: str, description: str,
                                    kb_type: str, embed_info: dict = None,
                                    llm_info: dict = None, metadata: dict = None) -> bool:
        """创建知识库 - 使用现有连接管理"""
        try:
            with self.db.get_cursor() as cursor:
                sql = """
                INSERT INTO knowledge_bases 
                (id, name, description, kb_type, embed_info, llm_info, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    kb_id, name, description, kb_type,
                    json.dumps(embed_info) if embed_info else None,
                    json.dumps(llm_info) if llm_info else None,
                    json.dumps(metadata) if metadata else None
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to create knowledge base {kb_id}: {e}")
            return False

    def create_knowledge_base_sync(self, kb_id: str, name: str, description: str,
                                   kb_type: str, embed_info: dict = None,
                                   llm_info: dict = None, metadata: dict = None) -> bool:
        """同步版本的创建知识库方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.create_knowledge_base(kb_id, name, description, kb_type, embed_info, llm_info, metadata))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def get_knowledge_base(self, kb_id: str) -> dict:
        """获取知识库信息 - 使用现有连接管理"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "SELECT * FROM knowledge_bases WHERE id = %s"
                cursor.execute(sql, (kb_id,))
                result = cursor.fetchone()
                if result:
                    # 解析JSON字段
                    if result['embed_info']:
                        result['embed_info'] = json.loads(result['embed_info'])
                    if result['llm_info']:
                        result['llm_info'] = json.loads(result['llm_info'])
                    if result['metadata']:
                        result['metadata'] = json.loads(result['metadata'])
                return result
        except Exception as e:
            logger.error(f"Failed to get knowledge base {kb_id}: {e}")
            return None

    def get_knowledge_base_sync(self, kb_id: str) -> dict:
        """同步版本的获取知识库信息方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_knowledge_base(kb_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def get_all_knowledge_bases(self) -> list:
        """获取所有知识库 - 使用现有连接管理"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "SELECT * FROM knowledge_bases ORDER BY created_at DESC"
                cursor.execute(sql)
                results = cursor.fetchall()

                for result in results:
                    if result['embed_info']:
                        result['embed_info'] = json.loads(result['embed_info'])
                    if result['llm_info']:
                        result['llm_info'] = json.loads(result['llm_info'])
                    if result['metadata']:
                        result['metadata'] = json.loads(result['metadata'])

                return results
        except Exception as e:
            logger.error(f"Failed to get all knowledge bases: {e}")
            return []

    def get_all_knowledge_bases_sync(self) -> list:
        """同步版本的获取所有知识库方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_all_knowledge_bases())
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def update_knowledge_base(self, kb_id: str, name: str = None, description: str = None,
                                    llm_info: dict = None) -> bool:
        """更新知识库信息"""
        try:
            with self.db.get_cursor() as cursor:
                updates = []
                params = []

                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                if llm_info is not None:
                    updates.append("llm_info = %s")
                    params.append(json.dumps(llm_info))

                if updates:
                    params.append(kb_id)
                    sql = f"UPDATE knowledge_bases SET {', '.join(updates)}, updated_at = NOW() WHERE id = %s"
                    cursor.execute(sql, params)
                    return True
                return True  # No updates needed
        except Exception as e:
            logger.error(f"Failed to update knowledge base {kb_id}: {e}")
            return False

    def update_knowledge_base_sync(self, kb_id: str, name: str = None, description: str = None,
                                   llm_info: dict = None) -> bool:
        """同步版本的更新知识库信息方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.update_knowledge_base(kb_id, name, description, llm_info))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def delete_knowledge_base(self, kb_id: str) -> bool:
        """删除知识库 - 使用现有连接管理"""
        try:
            with self.db.get_cursor() as cursor:
                sql = "DELETE FROM knowledge_bases WHERE id = %s"
                cursor.execute(sql, (kb_id,))
                return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge base {kb_id}: {e}")
            return False

    def delete_knowledge_base_sync(self, kb_id: str) -> bool:
        """同步版本的删除知识库方法"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.delete_knowledge_base(kb_id))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()