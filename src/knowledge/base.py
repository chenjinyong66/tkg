import os
from abc import ABC, abstractmethod
from typing import Any

from src.knowledge.db.connection import KnowledgeBaseDB
from src.knowledge.db.file_operations import FileDAO
from src.knowledge.db.kb_operations import KnowledgeBaseDAO
from src.utils import logger
from src.utils.datetime_utils import coerce_any_to_utc_datetime, utc_isoformat


class KnowledgeBaseException(Exception):
    """知识库统一异常基类"""

    pass


class KBNotFoundError(KnowledgeBaseException):
    """知识库不存在错误"""

    pass


class KBOperationError(KnowledgeBaseException):
    """知识库操作错误"""

    pass


class KnowledgeBase(ABC):
    """知识库抽象基类，定义统一接口"""

    # 类级别的处理队列，跟踪所有正在处理的文件
    _processing_files = set()
    _processing_lock = None

    # 全局数据库连接
    _db_instance = None
    _kb_dao = None
    _file_dao = None

    def __init__(self, work_dir: str, db_config: dict = None):
        """
        初始化知识库

        Args:
            work_dir: 工作目录
            db_config: 数据库配置
        """
        import threading

        self.work_dir = work_dir
        logger.info(f"Initializing knowledge base 用配置: {db_config}")
        # 初始化数据库连接
        if db_config and KnowledgeBase._db_instance is None:
            KnowledgeBase._db_instance = KnowledgeBaseDB(**db_config)
            KnowledgeBase._kb_dao = KnowledgeBaseDAO(KnowledgeBase._db_instance)
            KnowledgeBase._file_dao = FileDAO(KnowledgeBase._db_instance)

        # 初始化类级别的锁
        if KnowledgeBase._processing_lock is None:
            KnowledgeBase._processing_lock = threading.Lock()

        os.makedirs(work_dir, exist_ok=True)

        # 从数据库加载元数据
        self._load_metadata_from_db()

    @staticmethod
    def _normalize_timestamp(value: Any) -> str | None:
        """Convert persisted timestamps to a normalized UTC ISO string."""
        try:
            dt_value = coerce_any_to_utc_datetime(value)
        except (TypeError, ValueError) as exc:  # noqa: BLE001
            logger.warning(f"Invalid timestamp encountered: {value!r} ({exc})")
            return None

        if not dt_value:
            return None
        return utc_isoformat(dt_value)

    def _normalize_metadata_state(self) -> None:
        """Ensure in-memory metadata uses normalized timestamp formats."""
        for meta in self.databases_meta.values():
            if "created_at" in meta:
                normalized = self._normalize_timestamp(meta.get("created_at"))
                if normalized:
                    meta["created_at"] = normalized

        for file_info in self.files_meta.values():
            if "created_at" in file_info:
                normalized = self._normalize_timestamp(file_info.get("created_at"))
                if normalized:
                    file_info["created_at"] = normalized

        for db_benchmarks in self.benchmarks_meta.values():
            for b in db_benchmarks.values():
                if "created_at" in b:
                    normalized = self._normalize_timestamp(b.get("created_at"))
                    if normalized:
                        b["created_at"] = normalized
                if "updated_at" in b:
                    normalized = self._normalize_timestamp(b.get("updated_at"))
                    if normalized:
                        b["updated_at"] = normalized

    @property
    @abstractmethod
    def kb_type(self) -> str:
        """知识库类型标识"""
        pass

    @abstractmethod
    async def _create_kb_instance(self, db_id: str, config: dict) -> Any:
        """
        创建底层知识库实例

        Args:
            db_id: 数据库ID
            config: 配置信息

        Returns:
            底层知识库实例
        """
        pass

    @abstractmethod
    async def _initialize_kb_instance(self, instance: Any) -> None:
        """
        初始化底层知识库实例

        Args:
            instance: 底层知识库实例
        """
        pass

    async def create_database(
        self,
        database_name: str,
        description: str,
        embed_info: dict | None = None,
        llm_info: dict | None = None,
        **kwargs,
    ) -> dict:
        """
        创建数据库 - 现在使用数据库存储
        """
        from src.utils import hashstr
        import json

        # 从 kwargs 中获取 is_private 配置
        is_private = kwargs.get("is_private", False)
        prefix = "kb_private_" if is_private else "kb_"
        db_id = f"{prefix}{hashstr(database_name, with_salt=True)}"

        # 处理 embed_info，确保它是可序列化的字典
        processed_embed_info = embed_info
        if embed_info:
            if hasattr(embed_info, 'dict'):  # 如果是 Pydantic v1 模型
                processed_embed_info = embed_info.dict() if callable(getattr(embed_info, 'dict')) else {k: v for k, v in embed_info.__dict__.items()}
            elif hasattr(embed_info, 'model_dump'):  # 如果是 Pydantic v2 模型
                processed_embed_info = embed_info.model_dump()
            elif not isinstance(embed_info, dict):  # 如果不是字典也不是模型，尝试转换
                try:
                    processed_embed_info = json.loads(json.dumps(embed_info))
                except (TypeError, ValueError):
                    processed_embed_info = str(embed_info)  # 最后手段，转换为字符串

        # 使用数据库存储
        if KnowledgeBase._kb_dao is None:
            # 如果没有数据库连接，使用旧的文件存储方式
            logger.warning("No database connection, using file-based storage")
            
            # 创建工作目录
            working_dir = os.path.join(self.work_dir, db_id)
            os.makedirs(working_dir, exist_ok=True)
            
            # 返回模拟的数据库信息
            db_info = {
                "id": db_id,
                "name": database_name,
                "description": description,
                "kb_type": self.kb_type,
                "embed_info": processed_embed_info,
                "llm_info": llm_info,
                "metadata": kwargs,
                "created_at": self._normalize_timestamp("now"),
                "updated_at": self._normalize_timestamp("now")
            }
            db_info["db_id"] = db_id
            db_info["files"] = {}
            
            # 同时更新内存中的元数据
            self.databases_meta[db_id] = db_info
            
            return db_info
        else:
            success = await KnowledgeBase._kb_dao.create_knowledge_base(
                db_id, database_name, description, self.kb_type, 
                processed_embed_info, llm_info, kwargs
            )
            
            if not success:
                raise Exception(f"Failed to create knowledge base {db_id}")

            # 创建工作目录
            working_dir = os.path.join(self.work_dir, db_id)
            os.makedirs(working_dir, exist_ok=True)

            # 返回数据库信息
            db_info = await KnowledgeBase._kb_dao.get_knowledge_base(db_id)
            db_info["db_id"] = db_id
            db_info["files"] = {}

            return db_info

    def delete_database(self, db_id: str) -> dict:
        """
        删除数据库 - 从数据库删除
        """
        success = self._kb_dao.delete_knowledge_base_sync(db_id)
        if not success:
            raise Exception(f"Failed to delete knowledge base {db_id}")

        # 删除工作目录
        working_dir = os.path.join(self.work_dir, db_id)
        if os.path.exists(working_dir):
            import shutil

            try:
                shutil.rmtree(working_dir)
            except Exception as e:
                logger.error(f"Error deleting working directory {working_dir}: {e}")

        return {"message": "删除成功"}

    def create_folder(self, db_id: str, folder_name: str, parent_id: str | None = None) -> dict:
        """Create a folder in the database."""
        import uuid

        folder_id = f"folder-{uuid.uuid4()}"

        if KnowledgeBase._file_dao:
            # 使用数据库存储文件夹信息
            success = KnowledgeBase._file_dao.create_file_sync(
                file_id=folder_id,
                kb_id=db_id,
                filename=folder_name,
                is_folder=True,
                parent_id=parent_id
            )
            
            if not success:
                raise Exception(f"Failed to create folder {folder_name}")

            file_info = KnowledgeBase._file_dao.get_file_by_id_sync(folder_id)
            return file_info
        else:
            # 如果没有数据库连接，返回模拟的文件信息
            logger.warning("No database connection, using mock folder creation")
            return {
                "id": folder_id,
                "filename": folder_name,
                "is_folder": True,
                "parent_id": parent_id,
                "status": "created"
            }

    @abstractmethod
    async def add_content(self, db_id: str, items: list[str], params: dict | None = None) -> list[dict]:
        """
        添加内容（文件/URL）

        Args:
            db_id: 数据库ID
            items: 文件路径或URL列表
            params: 处理参数

        Returns:
            处理结果列表
        """
        pass

    @abstractmethod
    async def update_content(self, db_id: str, file_ids: list[str], params: dict | None = None) -> list[dict]:
        """
        更新内容 - 根据file_ids重新解析文件并更新向量库

        Args:
            db_id: 数据库ID
            file_ids: 文件ID列表
            params: 处理参数

        Returns:
            更新结果列表
        """
        pass

    @abstractmethod
    async def aquery(self, query_text: str, db_id: str, **kwargs) -> list[dict]:
        """
        异步查询知识库

        Args:
            query_text: 查询文本
            db_id: 数据库ID
            **kwargs: 查询参数

        Returns:
            一个包含字典的列表，每个字典代表一个检索到的文档块。
        """
        pass

    async def export_data(self, db_id: str, format: str = "zip", **kwargs) -> str:
        pass

    def query(self, query_text: str, db_id: str, **kwargs) -> list[dict]:
        """
        同步查询知识库（兼容性方法）

        Args:
            query_text: 查询文本
            db_id: 数据库ID
            **kwargs: 查询参数

        Returns:
            一个包含字典的列表，每个字典代表一个检索到的文档块。
        """
        import asyncio

        logger.warning("query is deprecated, use aquery instead")
        try:
            # 尝试在事件循环中使用 run_coroutine_threadsafe
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(
                self.aquery(query_text, db_id, **kwargs),
                loop
            )
            return future.result(timeout=30)  # 添加超时以避免无限等待
        except RuntimeError:
            # 如果没有运行的事件循环，则使用 asyncio.run
            return asyncio.run(self.aquery(query_text, db_id, **kwargs))

    def get_database_info(self, db_id: str) -> dict | None:
        """
        获取数据库详细信息

        Args:
            db_id: 数据库ID

        Returns:
            数据库信息或None
        """
        if KnowledgeBase._kb_dao is None or KnowledgeBase._file_dao is None:
            # 如果没有数据库连接，使用内存中的元数据
            logger.warning("No database connection, using in-memory metadata")
            
            if db_id not in self.databases_meta:
                return None
            
            db_info = self.databases_meta[db_id].copy()
            db_info["db_id"] = db_id
            
            # 获取该数据库的文件信息
            db_files = {}
            for file_id, file_info in self.files_meta.items():
                if file_info.get("database_id") == db_id:
                    file_copy = file_info.copy()
                    file_copy["file_id"] = file_id
                    file_copy["file_type"] = file_info.get("file_type", "")
                    file_copy["status"] = file_info.get("status", "done")
                    file_copy["is_folder"] = file_info.get("is_folder", False)
                    file_copy["parent_id"] = file_info.get("parent_id", None)
                    db_files[file_id] = file_copy
            
            # 按创建时间倒序排序文件列表
            sorted_files = dict(
                sorted(
                    db_files.items(),
                    key=lambda item: item[1].get("created_at") or "",
                    reverse=True,
                )
            )
            
            db_info["files"] = sorted_files
            db_info["row_count"] = len(sorted_files)
            db_info["status"] = "已连接"
            return db_info
        else:
            db_info = KnowledgeBase._kb_dao.get_knowledge_base_sync(db_id)
            if not db_info:
                return None

            db_info["db_id"] = db_id

            # 检查并修复异常的processing状态
            self._check_and_fix_processing_status(db_id)

            # 获取文件信息
            files = KnowledgeBase._file_dao.get_files_by_kb_id_sync(db_id)
            db_files = {}
            for file_info in files:
                file_info["file_id"] = file_info["id"]
                file_info["file_type"] = file_info.get("file_type", "")
                file_info["status"] = file_info.get("status", "done")
                file_info["is_folder"] = file_info.get("is_folder", False)
                file_info["parent_id"] = file_info.get("parent_id", None)
                db_files[file_info["id"]] = file_info

            # 按创建时间倒序排序文件列表
            sorted_files = dict(
                sorted(
                    db_files.items(),
                    key=lambda item: item[1].get("created_at") or "",
                    reverse=True,
                )
            )

            db_info["files"] = sorted_files
            db_info["row_count"] = len(sorted_files)
            db_info["status"] = "已连接"
            return db_info

    def get_databases(self) -> dict:
        """
        获取所有数据库信息

        Returns:
            数据库列表
        """
        # 如果没有数据库连接，返回内存中的元数据
        if KnowledgeBase._kb_dao is None or KnowledgeBase._file_dao is None:
            databases = []
            for db_id, db_meta in self.databases_meta.items():
                db_dict = db_meta.copy()
                db_dict["db_id"] = db_id
                
                # 获取该数据库的文件信息
                db_files = {}
                for file_id, file_info in self.files_meta.items():
                    if file_info.get("database_id") == db_id:
                        file_copy = file_info.copy()
                        file_copy["file_id"] = file_id
                        file_copy["file_type"] = file_info.get("file_type", "")
                        file_copy["status"] = file_info.get("status", "done")
                        file_copy["is_folder"] = file_info.get("is_folder", False)
                        file_copy["parent_id"] = file_info.get("parent_id", None)
                        db_files[file_id] = file_copy
                
                # 按创建时间倒序排序文件列表
                sorted_files = dict(
                    sorted(
                        db_files.items(),
                        key=lambda item: item[1].get("created_at") or "",
                        reverse=True,
                    )
                )
                
                db_dict["files"] = sorted_files
                db_dict["row_count"] = len(sorted_files)
                db_dict["status"] = "已连接"
                databases.append(db_dict)
            
            return {"databases": databases}
        
        # 使用数据库连接获取数据
        databases = []
        db_list = KnowledgeBase._kb_dao.get_all_knowledge_bases_sync()
        
        for db_meta in db_list:
            db_dict = db_meta.copy()
            db_dict["db_id"] = db_dict["id"]

            # 获取文件信息
            files = KnowledgeBase._file_dao.get_files_by_kb_id_sync(db_dict["id"])
            db_files = {}
            for file_info in files:
                file_info["file_id"] = file_info["id"]
                file_info["file_type"] = file_info.get("file_type", "")
                file_info["status"] = file_info.get("status", "done")
                file_info["is_folder"] = file_info.get("is_folder", False)
                file_info["parent_id"] = file_info.get("parent_id", None)
                db_files[file_info["id"]] = file_info

            # 按创建时间倒序排序文件列表
            sorted_files = dict(
                sorted(
                    db_files.items(),
                    key=lambda item: item[1].get("created_at") or "",
                    reverse=True,
                )
            )

            db_dict["files"] = sorted_files
            db_dict["row_count"] = len(sorted_files)
            db_dict["status"] = "已连接"
            databases.append(db_dict)

        return {"databases": databases}

    @classmethod
    def _add_to_processing_queue(cls, file_id: str) -> None:
        """
        将文件添加到处理队列

        Args:
            file_id: 文件ID
        """
        with cls._processing_lock:
            cls._processing_files.add(file_id)
            logger.debug(f"Added file {file_id} to processing queue")

    @classmethod
    def _remove_from_processing_queue(cls, file_id: str) -> None:
        """
        从处理队列中移除文件

        Args:
            file_id: 文件ID
        """
        with cls._processing_lock:
            cls._processing_files.discard(file_id)
            logger.debug(f"Removed file {file_id} from processing queue")

    @classmethod
    def _is_file_in_processing_queue(cls, file_id: str) -> bool:
        """
        检查文件是否在处理队列中

        Args:
            file_id: 文件ID

        Returns:
            bool: 文件是否在处理队列中
        """
        with cls._processing_lock:
            return file_id in cls._processing_files

    def _check_and_fix_processing_status(self, db_id: str) -> None:
        """
        检查并修复异常的processing状态
        如果文件状态为processing但实际不在处理队列中，则修改为error状态

        Args:
            db_id: 数据库ID
        """
        try:
            status_changed = False

            # 检查该数据库下所有processing状态的文件
            files = self._file_dao.get_files_by_kb_id_sync(db_id)
            for file_info in files:
                if file_info.get("status") == "processing":
                    file_id = file_info.get("id")
                    # 检查文件是否真的在处理队列中
                    if not self._is_file_in_processing_queue(file_id):
                        logger.warning(
                            f"File {file_id} has processing status but is not in processing queue, marking as error"
                        )
                        self._file_dao.update_file_status_sync(file_id, "failed", "Processing interrupted - file not found in processing queue")
                        status_changed = True

            # 如果有状态变更，记录日志
            if status_changed:
                logger.info(f"Fixed processing status for database {db_id}")

        except Exception as e:
            logger.error(f"Error checking processing status for database {db_id}: {e}")

    async def delete_folder(self, db_id: str, folder_id: str) -> None:
        """
        Recursively delete a folder and its content.

        Args:
            db_id: Database ID
            folder_id: Folder ID to delete
        """
        # Find all children
        if KnowledgeBase._file_dao is None:
            logger.warning("No database connection, cannot retrieve folder children")
            # 如果没有数据库连接，无法执行递归删除，只调用删除文件的方法
            await self.delete_file(db_id, folder_id)
        else:
            children = KnowledgeBase._file_dao.get_folder_children_sync(db_id, folder_id)

            for child_id in children:
                child_meta = KnowledgeBase._file_dao.get_file_by_id_sync(child_id)
                if child_meta and child_meta.get("is_folder"):
                    await self.delete_folder(db_id, child_id)
                else:
                    await self.delete_file(db_id, child_id)

            # Delete the folder itself
            await self.delete_file(db_id, folder_id)

    async def move_file(self, db_id: str, file_id: str, new_parent_id: str | None) -> dict:
        """
        Move a file or folder to a new parent folder.

        Args:
            db_id: Database ID
            file_id: File/Folder ID to move
            new_parent_id: New parent folder ID (None for root)

        Returns:
            dict: Updated metadata
        """
        file_info = self._file_dao.get_file_by_id_sync(file_id)
        if not file_info:
            raise ValueError(f"File {file_id} not found")

        if file_info.get("database_id") != db_id:
            raise ValueError(f"File {file_id} does not belong to database {db_id}")

        # Basic cycle detection for folders
        if file_info.get("is_folder") and new_parent_id:
            # Check if new_parent_id is a child of file_id (or is file_id itself)
            if new_parent_id == file_id:
                raise ValueError("Cannot move a folder into itself")

            # Walk up the tree from new_parent_id
            current = new_parent_id
            while current:
                parent_meta = self._file_dao.get_file_by_id_sync(current)
                if not parent_meta:
                    break  # Should not happen if integrity is maintained
                if current == file_id:
                    raise ValueError("Cannot move a folder into its own subfolder")
                current = parent_meta.get("parent_id")

        # Update parent_id in database
        success = self._file_dao.update_file_parent_sync(file_id, new_parent_id)
        if not success:
            raise Exception(f"Failed to update file parent for {file_id}")

        return self._file_dao.get_file_by_id_sync(file_id)

    @abstractmethod
    async def delete_file(self, db_id: str, file_id: str) -> None:
        """
        删除文件

        Args:
            db_id: 数据库ID
            file_id: 文件ID
        """
        pass

    @abstractmethod
    async def get_file_basic_info(self, db_id: str, file_id: str) -> dict:
        """
        获取文件基本信息（仅元数据）

        Args:
            db_id: 数据库ID
            file_id: 文件ID

        Returns:
            dict: 包含文件基本信息的字典
        """
        pass

    @abstractmethod
    async def get_file_content(self, db_id: str, file_id: str) -> dict:
        """
        获取文件内容信息（chunks和lines）

        Args:
            db_id: 数据库ID
            file_id: 文件ID

        Returns:
            dict: 包含文件内容信息的字典
        """
        pass

    @abstractmethod
    async def get_file_info(self, db_id: str, file_id: str) -> dict:
        """
        获取文件完整信息（基本信息+内容信息）- 保持向后兼容

        Args:
            db_id: 数据库ID
            file_id: 文件ID

        Returns:
            dict: 包含文件信息和chunks的字典
        """
        pass

    def get_db_upload_path(self, db_id: str | None = None) -> str:
        """
        获取数据库上传路径

        Args:
            db_id: 数据库ID，可选

        Returns:
            上传路径
        """
        if db_id:
            uploads_folder = os.path.join(self.work_dir, db_id, "uploads")
            os.makedirs(uploads_folder, exist_ok=True)
            return uploads_folder

        general_uploads = os.path.join(self.work_dir, "uploads")
        os.makedirs(general_uploads, exist_ok=True)
        return general_uploads

    def update_database(self, db_id: str, name: str, description: str, llm_info: dict = None) -> dict:
        """
        更新数据库

        Args:
            db_id: 数据库ID
            name: 新名称
            description: 新描述
            llm_info: LLM配置信息（可选，仅用于 LightRAG 类型知识库）

        Returns:
            更新后的数据库信息
        """
        success = self._kb_dao.update_knowledge_base_sync(db_id, name, description, llm_info)
        if not success:
            raise ValueError(f"数据库 {db_id} 不存在")

        return self.get_database_info(db_id)

    def get_retrievers(self) -> dict[str, dict]:
        """
        获取所有检索器

        Returns:
            检索器字典
        """
        retrievers = {}
        
        if KnowledgeBase._kb_dao is None:
            # 如果没有数据库连接，使用内存中的元数据
            logger.warning("No database connection, using in-memory metadata for retrievers")
            
            for db_id, db_meta in self.databases_meta.items():
                def make_retriever(db_id):
                    async def retriever(query_text, **kwargs):
                        return await self.aquery(query_text, db_id, **kwargs)

                    return retriever

                retrievers[db_id] = {
                    "name": db_meta["name"],
                    "description": db_meta["description"],
                    "retriever": make_retriever(db_id),
                    "metadata": db_meta,
                }
        else:
            db_list = KnowledgeBase._kb_dao.get_all_knowledge_bases_sync()
            for db_meta in db_list:
                db_id = db_meta["id"]

                def make_retriever(db_id):
                    async def retriever(query_text, **kwargs):
                        return await self.aquery(query_text, db_id, **kwargs)

                    return retriever

                retrievers[db_id] = {
                    "name": db_meta["name"],
                    "description": db_meta["description"],
                    "retriever": make_retriever(db_id),
                    "metadata": db_meta,
                }
        return retrievers

    def _load_metadata_from_db(self):
        """从数据库加载元数据"""
        try:
            # 如果没有数据库连接，初始化为空
            if KnowledgeBase._kb_dao is None or KnowledgeBase._file_dao is None:
                logger.warning("No database connection, initializing empty metadata")
                self.databases_meta = {}
                self.files_meta = {}
                self.benchmarks_meta = {}
                return
            
            # 加载数据库信息
            db_list = KnowledgeBase._kb_dao.get_all_knowledge_bases_sync()
            self.databases_meta = {db["id"]: db for db in db_list}

            # 加载文件信息
            all_files = []
            for db_id in self.databases_meta:
                files = KnowledgeBase._file_dao.get_files_by_kb_id_sync(db_id)
                all_files.extend(files)
            self.files_meta = {file["id"]: file for file in all_files}

            logger.info(f"Loaded metadata from database: {len(self.databases_meta)} databases, {len(self.files_meta)} files")
        except Exception as e:
            logger.error(f"Failed to load metadata from database: {e}")
            self.databases_meta = {}
            self.files_meta = {}
            self.benchmarks_meta = {}

    def _save_metadata_to_db(self):
        """保存元数据到数据库"""
        # 由于现在使用数据库存储，不再需要单独保存元数据
        pass