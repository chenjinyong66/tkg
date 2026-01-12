import asyncio
import json
import os
import shutil
import tempfile

from src.knowledge.base import KBNotFoundError, KnowledgeBase
from src.knowledge.factory import KnowledgeBaseFactory
from src.utils import logger
from src.utils.datetime_utils import coerce_any_to_utc_datetime, utc_isoformat
from src.knowledge.db.connection import KnowledgeBaseDB
from src.knowledge.db.kb_operations import KnowledgeBaseDAO
from src.knowledge.db.file_operations import FileDAO


class KnowledgeBaseManager:
    """
    知识库管理器

    统一管理多种类型的知识库实例，提供统一的外部接口
    """

    def __init__(self, work_dir: str, db_config: dict = None):
        """
        初始化知识库管理器

        Args:
            work_dir: 工作目录
            db_config: 数据库配置
        """
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

        # 初始化数据库连接
        if db_config:
            self.db_instance = KnowledgeBaseDB(**db_config)
            self.kb_dao = KnowledgeBaseDAO(self.db_instance)
            self.file_dao = FileDAO(self.db_instance)
        else:
            # 如果没有提供db_config，初始化为None，但需要在需要时检查
            self.db_instance = None
            self.kb_dao = None
            self.file_dao = None

        # 知识库实例缓存 {kb_type: kb_instance}
        self.kb_instances: dict[str, KnowledgeBase] = {}

        # 全局数据库元信息 {db_id: metadata_with_kb_type}
        self.global_databases_meta: dict[str, dict] = {}

        # 元数据锁
        self._metadata_lock = asyncio.Lock()

        # 加载全局元数据
        self._load_global_metadata()
        self._normalize_global_metadata()

        # 初始化已存在的知识库实例
        self._initialize_existing_kbs()

        logger.info("KnowledgeBaseManager initialized")

    def _load_global_metadata(self):
        """加载全局元数据 - 从数据库加载"""
        try:
            # 如果没有数据库连接，尝试从各个知识库实例中加载元数据
            if not self.kb_dao:
                logger.warning("No database connection, attempting to load global metadata from knowledge base instances")
                self.global_databases_meta = {}
                
                # 尝试从已有的知识库实例中加载元数据
                for kb_type, kb_instance in self.kb_instances.items():
                    if hasattr(kb_instance, 'databases_meta'):
                        for db_id, db_meta in kb_instance.databases_meta.items():
                            # 确保db_meta包含kb_type信息
                            db_meta_copy = db_meta.copy()
                            if 'kb_type' not in db_meta_copy:
                                db_meta_copy['kb_type'] = kb_instance.kb_type
                            self.global_databases_meta[db_id] = db_meta_copy
                
                logger.info(f"Loaded global metadata for {len(self.global_databases_meta)} databases from knowledge base instances")
                return
            
            # 从数据库加载全局元数据
            all_kbs = self.kb_dao.get_all_knowledge_bases_sync()
            for kb in all_kbs:
                self.global_databases_meta[kb['id']] = kb
            logger.info(f"Loaded global metadata for {len(self.global_databases_meta)} databases from database")
        except Exception as e:
            logger.error(f"Failed to load global metadata from database: {e}")
            # 初始化为空状态
            logger.warning("Initializing empty global metadata")
            self.global_databases_meta = {}

    def _save_global_metadata(self):
        """保存全局元数据 - 通过数据库DAO保存"""
        self._normalize_global_metadata()
        # 由于现在使用数据库存储，不再保存到文件
        # 保存操作通过数据库DAO完成
        pass

    def _normalize_global_metadata(self) -> None:
        """Normalize stored timestamps within the global metadata cache."""
        for meta in self.global_databases_meta.values():
            if "created_at" in meta:
                try:
                    dt_value = coerce_any_to_utc_datetime(meta.get("created_at"))
                    if dt_value:
                        meta["created_at"] = utc_isoformat(dt_value)
                        continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning(f"Failed to normalize database metadata timestamp {meta.get('created_at')!r}: {exc}")

    def _initialize_existing_kbs(self):
        """初始化已存在的知识库实例"""
        kb_types_in_use = set()
        for db_meta in self.global_databases_meta.values():
            kb_type = db_meta.get("kb_type", "lightrag")  # 默认为lightrag
            kb_types_in_use.add(kb_type)

        # 如果没有从全局元数据中找到任何数据库，尝试从工作目录中发现可能存在的数据库
        if not kb_types_in_use and self.db_instance is None:
            # 尝试扫描工作目录中可能存在的知识库
            if os.path.exists(self.work_dir):
                for item in os.listdir(self.work_dir):
                    item_path = os.path.join(self.work_dir, item)
                    if os.path.isdir(item_path):
                        # 检查是否是知识库目录（通常以kb_或kb_private_开头）
                        if item.startswith('kb_'):
                            # 假设这是lightrag类型的KB，因为这是默认类型
                            kb_types_in_use.add('lightrag')

        # 为每种使用中的知识库类型创建实例
        for kb_type in kb_types_in_use:
            try:
                self._get_or_create_kb_instance(kb_type)
            except Exception as e:
                logger.error(f"Failed to initialize {kb_type} knowledge base: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")  # 添加详细错误信息

    def _get_or_create_kb_instance(self, kb_type: str) -> KnowledgeBase:
        """
        获取或创建知识库实例

        Args:
            kb_type: 知识库类型

        Returns:
            知识库实例
        """
        if kb_type in self.kb_instances:
            return self.kb_instances[kb_type]

        # 创建新的知识库实例，传递数据库配置
        kb_work_dir = os.path.join(self.work_dir, f"{kb_type}_data")
        db_config_to_pass = self.db_instance.mysql_config if (self.db_instance and hasattr(self.db_instance, 'mysql_config')) else None
        kb_instance = KnowledgeBaseFactory.create(kb_type, kb_work_dir, db_config=db_config_to_pass)

        self.kb_instances[kb_type] = kb_instance
        logger.info(f"Created {kb_type} knowledge base instance")
        return kb_instance

    async def move_file(self, db_id: str, file_id: str, new_parent_id: str | None) -> dict:
        """
        移动文件/文件夹
        """
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.move_file(db_id, file_id, new_parent_id)

    def _get_kb_for_database(self, db_id: str) -> KnowledgeBase:
        """
        根据数据库ID获取对应的知识库实例

        Args:
            db_id: 数据库ID

        Returns:
            知识库实例

        Raises:
            KBNotFoundError: 数据库不存在或知识库类型不支持
        """
        # 首先尝试从全局元数据中查找
        if db_id in self.global_databases_meta:
            kb_type = self.global_databases_meta[db_id].get("kb_type", "lightrag")
        else:
            # 如果全局元数据中没有，尝试从数据库中直接查询
            kb_type = None
            if self.kb_dao:
                db_info = self.kb_dao.get_knowledge_base_sync(db_id)
                if db_info:
                    kb_type = db_info.get("kb_type", "lightrag")
                    # 同时更新全局元数据缓存
                    self.global_databases_meta[db_id] = db_info
            
            # 如果仍然找不到，抛出异常
            if kb_type is None:
                raise KBNotFoundError(f"Database {db_id} not found")

        if not KnowledgeBaseFactory.is_type_supported(kb_type):
            raise KBNotFoundError(f"Unsupported knowledge base type: {kb_type}")

        return self._get_or_create_kb_instance(kb_type)

    # =============================================================================
    # 统一的外部接口 - 与原始 LightRagBasedKB 兼容
    # =============================================================================

    def get_kb(self, db_id: str) -> KnowledgeBase:
        """Public accessor to fetch the underlying knowledge base instance by database id.

        This provides a simple compatibility layer for callers that expect a
        `get_kb` method on the manager.
        """
        return self._get_kb_for_database(db_id)

    def get_databases(self) -> dict:
        """获取所有数据库信息"""
        all_databases = []

        # 收集所有知识库的数据库信息
        for kb_type, kb_instance in self.kb_instances.items():
            try:
                kb_databases = kb_instance.get_databases()["databases"]
                all_databases.extend(kb_databases)
            except Exception as e:
                logger.error(f"Failed to get databases from {kb_type} knowledge base: {e}")
                continue  # 继续处理其他知识库实例

        return {"databases": all_databases}

    async def create_folder(self, db_id: str, folder_name: str, parent_id: str = None) -> dict:
        """Create a folder in the database."""
        kb_instance = self._get_kb_for_database(db_id)
        return kb_instance.create_folder(db_id, folder_name, parent_id)

    async def create_database(
        self, database_name: str, description: str, kb_type: str = "lightrag", embed_info: dict | None = None, **kwargs
    ) -> dict:
        """
        创建知识库 - 现在使用数据库存储
        """
        if not KnowledgeBaseFactory.is_type_supported(kb_type):
            available_types = list(KnowledgeBaseFactory.get_available_types().keys())
            raise ValueError(f"Unsupported knowledge base type: {kb_type}. Available types: {available_types}")

        kb_instance = self._get_or_create_kb_instance(kb_type)

        db_info = await kb_instance.create_database(database_name, description, embed_info, **kwargs)
        db_id = db_info["db_id"]

        # 通过数据库DAO更新全局元数据
        if self.kb_dao:
            success = self.kb_dao.update_knowledge_base_sync(db_id, 
                name=database_name,
                description=description,
                llm_info=None  # 如果需要的话可以传递llm_info
            )

            if not success:
                logger.error(f"Failed to update global metadata for {db_id}")
        else:
            # 如果没有数据库连接，更新全局元数据到内存中
            self.global_databases_meta[db_id] = {
                "id": db_id,
                "name": database_name,
                "description": description,
                "kb_type": kb_type,
                "created_at": db_info.get("created_at"),
                "updated_at": db_info.get("updated_at"),
                **kwargs
            }

        logger.info(f"Created {kb_type} database: {database_name} ({db_id}) with {kwargs}")
        return db_info

    async def delete_database(self, db_id: str) -> dict:
        """删除数据库 - 从数据库删除"""
        try:
            kb_instance = self._get_kb_for_database(db_id)
            result = kb_instance.delete_database(db_id)

            # 从全局元数据中删除
            if db_id in self.global_databases_meta:
                del self.global_databases_meta[db_id]
                
                # 通过数据库DAO删除全局元数据
                if self.kb_dao:
                    success = self.kb_dao.delete_knowledge_base_sync(db_id)
                    if not success:
                        logger.error(f"Failed to delete global metadata for {db_id}")

            return result
        except KBNotFoundError as e:
            logger.warning(f"Database {db_id} not found during deletion: {e}")
            return {"message": "删除成功"}
        except Exception as e:
            logger.error(f"Error deleting database {db_id}: {e}")
            # 即使发生错误，也要尝试清理内存中的元数据
            if db_id in self.global_databases_meta:
                del self.global_databases_meta[db_id]
            return {"message": "删除成功"}

    async def add_content(self, db_id: str, items: list[str], params: dict | None = None) -> list[dict]:
        """添加内容（文件/URL）"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.add_content(db_id, items, params or {})

    async def aquery(self, query_text: str, db_id: str, **kwargs) -> str:
        """异步查询知识库"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.aquery(query_text, db_id, **kwargs)

    async def export_data(self, db_id: str, format: str = "zip", **kwargs) -> str:
        """导出知识库数据"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.export_data(db_id, format=format, **kwargs)

    def query(self, query_text: str, db_id: str, **kwargs) -> str:
        """同步查询知识库（兼容性方法）"""
        kb_instance = self._get_kb_for_database(db_id)
        return kb_instance.query(query_text, db_id, **kwargs)

    def get_database_info(self, db_id: str) -> dict | None:
        """获取数据库详细信息"""
        try:
            kb_instance = self._get_kb_for_database(db_id)
            db_info = kb_instance.get_database_info(db_id)

            # 添加全局元数据中的additional_params信息
            if db_info and db_id in self.global_databases_meta:
                global_meta = self.global_databases_meta[db_id]
                additional_params = global_meta.get("additional_params", {}).copy()

                # 确保 auto_generate_questions 存在，默认为 False
                if "auto_generate_questions" not in additional_params:
                    additional_params["auto_generate_questions"] = False

                db_info["additional_params"] = additional_params

            return db_info
        except KBNotFoundError:
            logger.warning(f"Database {db_id} not found in any knowledge base instance")
            return None
        except Exception as e:
            logger.error(f"Error getting database info for {db_id}: {e}")
            # 检查是否是由于数据库连接问题导致的错误
            if db_id in self.global_databases_meta:
                # 如果全局元数据中存在该数据库，尝试使用全局元数据构建基本的信息
                logger.info(f"Using global metadata as fallback for {db_id}")
                global_meta = self.global_databases_meta[db_id]
                return {
                    "id": db_id,
                    "db_id": db_id,
                    "name": global_meta.get("name", ""),
                    "description": global_meta.get("description", ""),
                    "kb_type": global_meta.get("kb_type", "lightrag"),
                    "created_at": global_meta.get("created_at"),
                    "updated_at": global_meta.get("updated_at"),
                    "files": {},
                    "row_count": 0,
                    "status": "已连接",
                    "additional_params": global_meta.get("additional_params", {})
                }
            return None

    async def delete_folder(self, db_id: str, folder_id: str) -> None:
        """递归删除文件夹"""
        kb_instance = self._get_kb_for_database(db_id)
        await kb_instance.delete_folder(db_id, folder_id)

    async def delete_file(self, db_id: str, file_id: str) -> None:
        """删除文件"""
        kb_instance = self._get_kb_for_database(db_id)
        await kb_instance.delete_file(db_id, file_id)

    async def update_content(self, db_id: str, file_ids: list[str], params: dict | None = None) -> list[dict]:
        """更新内容（重新分块）"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.update_content(db_id, file_ids, params or {})

    async def get_file_basic_info(self, db_id: str, file_id: str) -> dict:
        """获取文件基本信息（仅元数据）"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.get_file_basic_info(db_id, file_id)

    async def get_file_content(self, db_id: str, file_id: str) -> dict:
        """获取文件内容信息（chunks和lines）"""
        kb_instance = self._get_kb_for_database(db_id)
        return await kb_instance.get_file_content(db_id, file_id)

    async def get_file_info(self, db_id: str, file_id: str) -> dict:
        """获取文件完整信息（基本信息+内容信息）- 保持向后兼容"""
        kb_instance = self._get_kb_for_database(db_id)
        logger.info(f"获取文件完整信息 Getting file info for {file_id}")
        logger.info(f"获取文件完整信息 kb_instance:{kb_instance} ")
        return await kb_instance.get_file_info(db_id, file_id)

    def get_db_upload_path(self, db_id: str | None = None) -> str:
        """获取数据库上传路径"""
        if db_id:
            try:
                kb_instance = self._get_kb_for_database(db_id)
                return kb_instance.get_db_upload_path(db_id)
            except KBNotFoundError:
                # 如果数据库不存在，创建通用上传路径
                pass

        # 通用上传路径
        general_uploads = os.path.join(self.work_dir, "uploads")
        os.makedirs(general_uploads, exist_ok=True)
        return general_uploads

    async def file_name_existed_in_db(self, db_id: str | None, file_name: str | None) -> bool:
        """检查指定数据库中是否存在同名的文件"""
        if not db_id or not file_name:
            return False
        try:
            kb_instance = self._get_kb_for_database(db_id)
        except KBNotFoundError:
            return False

        for file_info in kb_instance.files_meta.values():
            if file_info.get("database_id") != db_id:
                continue
            if file_info.get("status") == "failed":
                continue
            if file_info.get("file_name") == file_name:
                return True

        return False

    async def get_same_name_files(self, db_id: str, filename: str) -> list[dict]:
        """获取同一知识库中同名文件列表
        基于原始文件名直接比较
        返回基础信息：文件名、大小、上传时间

        Args:
            db_id: 数据库ID
            filename: 要检测的文件名（原始文件名）

        Returns:
            同名文件列表，每项包含：
            - filename: 文件名
            - size: 文件大小
            - created_at: 上传时间
            - file_id: 文件ID（用于下载）
        """
        if not db_id or not filename:
            return []
        try:
            kb_instance = self._get_kb_for_database(db_id)
        except KBNotFoundError:
            return []

        same_name_files = []
        for file_id, file_info in kb_instance.files_meta.items():
            if file_info.get("database_id") != db_id:
                continue
            if file_info.get("status") == "failed":
                continue

            # 直接比较文件名（现在就是原始文件名）
            current_filename = file_info.get("filename", "")

            if current_filename.lower() == filename.lower():
                same_name_files.append(
                    {
                        "file_id": file_id,
                        "filename": current_filename,
                        "size": file_info.get("size", 0),
                        "created_at": file_info.get("created_at", ""),
                        "content_hash": file_info.get("content_hash", ""),
                    }
                )

        # 按上传时间降序排序
        same_name_files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return same_name_files

    async def update_file(self, db_id: str, region_file_id: str, file_name: str, params: dict | None = None) -> dict:
        """对单个文件执行更新"""
        kb_instance = self._get_kb_for_database(db_id)
        await kb_instance.delete_file(db_id, region_file_id)
        data_list = await kb_instance.add_content(db_id, [file_name], params or {})
        return data_list[0]

    async def file_existed_in_db(self, db_id: str | None, content_hash: str | None) -> bool:
        """检查指定数据库中是否存在相同内容哈希的文件"""
        if not db_id or not content_hash:
            return False

        try:
            kb_instance = self._get_kb_for_database(db_id)
        except KBNotFoundError:
            return False

        for file_info in kb_instance.files_meta.values():
            if file_info.get("database_id") != db_id:
                continue
            if file_info.get("status") == "failed":
                continue
            if file_info.get("content_hash") == content_hash:
                return True

        return False

    def update_database(
        self, db_id: str, name: str, description: str, llm_info: dict = None, additional_params: dict | None = None
    ) -> dict:
        """更新数据库"""
        kb_instance = self._get_kb_for_database(db_id)
        result = kb_instance.update_database(db_id, name, description, llm_info)

        # 更新全局元数据
        if db_id in self.global_databases_meta:
            self.global_databases_meta[db_id]["name"] = name
            self.global_databases_meta[db_id]["description"] = description

            # 合并现有的 additional_params 和新的 additional_params
            existing_additional_params = self.global_databases_meta[db_id].get("additional_params", {})
            if additional_params:
                existing_additional_params.update(additional_params)
            self.global_databases_meta[db_id]["additional_params"] = existing_additional_params

            # 清理旧的 top-level key (如果存在)
            self.global_databases_meta[db_id].pop("auto_generate_questions", None)

        return result

    def get_retrievers(self) -> dict[str, dict]:
        """获取所有检索器"""
        all_retrievers = {}

        # 收集所有知识库的检索器
        for kb_instance in self.kb_instances.values():
            retrievers = kb_instance.get_retrievers()
            all_retrievers.update(retrievers)

        return all_retrievers

    # =============================================================================
    # 管理器特有的方法
    # =============================================================================

    def get_supported_kb_types(self) -> dict[str, dict]:
        """获取支持的知识库类型"""
        return KnowledgeBaseFactory.get_available_types()

    def get_kb_instance_info(self) -> dict[str, dict]:
        """获取知识库实例信息"""
        info = {}
        for kb_type, kb_instance in self.kb_instances.items():
            info[kb_type] = {
                "work_dir": kb_instance.work_dir,
                "database_count": len(kb_instance.databases_meta),
                "file_count": len(kb_instance.files_meta),
            }
        return info

    def get_statistics(self) -> dict:
        """获取统计信息"""
        stats = {"total_databases": len(self.global_databases_meta), "kb_types": {}, "total_files": 0}

        # 按知识库类型统计
        for db_meta in self.global_databases_meta.values():
            kb_type = db_meta.get("kb_type", "lightrag")
            if kb_type not in stats["kb_types"]:
                stats["kb_types"][kb_type] = 0
            stats["kb_types"][kb_type] += 1

        # 统计文件总数
        for kb_instance in self.kb_instances.values():
            stats["total_files"] += len(kb_instance.files_meta)

        return stats

    # =============================================================================
    # 兼容性方法 - 为了支持现有的 graph_router.py
    # =============================================================================

    async def _get_lightrag_instance(self, db_id: str):
        """
        获取 LightRAG 实例（兼容性方法）

        Args:
            db_id: 数据库ID

        Returns:
            LightRAG 实例，如果数据库不是 lightrag 类型则返回 None

        Raises:
            ValueError: 如果数据库不存在或不是 lightrag 类型
        """
        try:
            # 检查数据库是否存在
            if db_id not in self.global_databases_meta:
                logger.error(f"Database {db_id} not found in global metadata")
                return None

            # 检查是否是 LightRAG 类型
            kb_type = self.global_databases_meta[db_id].get("kb_type", "lightrag")
            if kb_type != "lightrag":
                logger.error(f"Database {db_id} is not a LightRAG type (actual type: {kb_type})")
                raise ValueError(f"Database {db_id} is not a LightRAG knowledge base")

            # 获取 LightRAG 知识库实例
            kb_instance = self._get_kb_for_database(db_id)

            # 如果不是 LightRagKB 实例，返回错误
            if not hasattr(kb_instance, "_get_lightrag_instance"):
                logger.error(f"Knowledge base instance for {db_id} is not LightRagKB")
                return None

            # 调用 LightRagKB 的方法获取 LightRAG 实例
            return await kb_instance._get_lightrag_instance(db_id)

        except Exception as e:
            logger.error(f"Failed to get LightRAG instance for {db_id}: {e}")
            return None

    def is_lightrag_database(self, db_id: str) -> bool:
        """
        检查数据库是否是 LightRAG 类型

        Args:
            db_id: 数据库ID

        Returns:
            是否是 LightRAG 类型的数据库
        """
        if db_id not in self.global_databases_meta:
            return False

        kb_type = self.global_databases_meta[db_id].get("kb_type", "lightrag")
        return kb_type == "lightrag"

    def get_lightrag_databases(self) -> list[dict]:
        """
        获取所有 LightRAG 类型的数据库

        Returns:
            LightRAG 数据库列表
        """
        lightrag_databases = []

        all_databases = self.get_databases()["databases"]
        for db in all_databases:
            if db.get("kb_type", "lightrag") == "lightrag":
                lightrag_databases.append(db)

        return lightrag_databases

    # =============================================================================
    # 数据一致性检测方法
    # =============================================================================

    async def detect_data_inconsistencies(self) -> dict:
        """
        检测向量数据库中存在但在 metadata 中缺失的数据

        Returns:
            包含不一致信息的字典，按知识库类型分组
        """
        inconsistencies = {
            "milvus": {"missing_collections": [], "missing_files": []},
            "total_missing_collections": 0,
            "total_missing_files": 0,
        }

        logger.info("开始检测向量数据库与元数据的一致性...")

        # 检测 Milvus 数据不一致
        if "milvus" in self.kb_instances:
            try:
                milvus_inconsistencies = await self._detect_milvus_inconsistencies()
                inconsistencies["milvus"] = milvus_inconsistencies
                inconsistencies["total_missing_collections"] += len(milvus_inconsistencies["missing_collections"])
                inconsistencies["total_missing_files"] += len(milvus_inconsistencies["missing_files"])
            except Exception as e:
                logger.error(f"检测 Milvus 数据不一致时出错: {e}")

        # 输出检测结果到日志
        self._log_inconsistencies(inconsistencies)

        return inconsistencies

    async def _detect_milvus_inconsistencies(self) -> dict:
        """检测 Milvus 中的数据不一致"""
        inconsistencies = {"missing_collections": [], "missing_files": []}

        milvus_kb = self.kb_instances["milvus"]

        try:
            from pymilvus import utility

            # 获取 Milvus 中所有实际的集合
            actual_collection_names = set(utility.list_collections(using=milvus_kb.connection_alias))

            # 获取 metadata 中记录的数据库ID
            metadata_collection_names = set(milvus_kb.databases_meta.keys())

            # 找出存在于 Milvus 但不在 metadata 中的集合
            missing_collections = actual_collection_names - metadata_collection_names
            for collection_name in missing_collections:
                # 跳过一些系统集合
                if not collection_name.startswith("kb_"):
                    continue

                collection_info = {"collection_name": collection_name, "detected_at": utc_isoformat()}

                # 尝试获取集合的基本信息
                try:
                    from pymilvus import Collection

                    collection = Collection(name=collection_name, using=milvus_kb.connection_alias)
                    collection_info["count"] = collection.num_entities
                    collection_info["description"] = collection.description
                except Exception as e:
                    logger.warning(f"无法获取集合 {collection_name} 的详细信息: {e}")
                    collection_info["count"] = "unknown"

                inconsistencies["missing_collections"].append(collection_info)
                logger.warning(
                    f"发现 Milvus 中存在但 metadata 中缺失的集合: {collection_name} "
                    f"(实体数: {collection_info['count']})"
                )

            # 检查文件级别的不一致（针对已知的数据库）
            for db_id in metadata_collection_names:
                try:
                    if utility.has_collection(db_id, using=milvus_kb.connection_alias):
                        from pymilvus import Collection

                        collection = Collection(name=db_id, using=milvus_kb.connection_alias)
                        actual_count = collection.num_entities

                        # 获取 metadata 中记录的文件数量
                        metadata_files_count = sum(
                            1 for file_info in milvus_kb.files_meta.values() if file_info.get("database_id") == db_id
                        )

                        # 如果向量数据库中有数据但 metadata 中没有文件记录，可能存在文件缺失
                        if actual_count > 0 and metadata_files_count == 0:
                            inconsistencies["missing_files"].append(
                                {
                                    "database_id": db_id,
                                    "vector_count": actual_count,
                                    "metadata_files_count": metadata_files_count,
                                    "detected_at": utc_isoformat(),
                                }
                            )
                            logger.warning(
                                f"发现数据库 {db_id} 在 Milvus 中有 {actual_count} 条向量数据，"
                                "但 metadata 中没有文件记录"
                            )

                except Exception as e:
                    logger.debug(f"检查数据库 {db_id} 的文件一致性时出错: {e}")

        except Exception as e:
            logger.error(f"检测 Milvus 数据不一致时出错: {e}")

        return inconsistencies

    def _log_inconsistencies(self, inconsistencies: dict) -> None:
        """将不一致检测结果输出到日志"""
        total_missing_collections = inconsistencies["total_missing_collections"]
        total_missing_files = inconsistencies["total_missing_files"]

        if total_missing_collections == 0 and total_missing_files == 0:
            logger.info("数据一致性检测完成，未发现不一致情况")
            return

        logger.warning("=" * 80)
        logger.warning("数据一致性检测完成，发现以下不一致情况：")
        logger.warning("=" * 80)

        # Milvus 不一致情况
        milvus_missing = inconsistencies["milvus"]["missing_collections"]
        milvus_files_missing = inconsistencies["milvus"]["missing_files"]
        if milvus_missing or milvus_files_missing:
            logger.warning("Milvus 不一致情况：")
            logger.warning(f"  缺失集合数量: {len(milvus_missing)}")
            for collection_info in milvus_missing:
                logger.warning(f"    - 集合: {collection_info['collection_name']}, 实体数: {collection_info['count']}")
            logger.warning(f"  缺失文件记录数量: {len(milvus_files_missing)}")
            for file_info in milvus_files_missing:
                logger.warning(
                    f"    - 数据库: {file_info['database_id']}, 向量数: {file_info['vector_count']}, "
                    f"元数据文件数: {file_info['metadata_files_count']}"
                )

        logger.warning("=" * 80)
        logger.warning(f"总计：缺失集合 {total_missing_collections} 个，缺失文件记录 {total_missing_files} 个")
        logger.warning("建议：检查这些不一致的数据，必要时进行数据清理或元数据修复")
        logger.warning("=" * 80)

    async def manual_consistency_check(self) -> dict:
        """
        手动触发数据一致性检测

        Returns:
            检测结果字典
        """
        logger.info("手动触发数据一致性检测...")
        return await self.detect_data_inconsistencies()
