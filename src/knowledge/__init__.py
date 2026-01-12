import os

from ..config import config
from .factory import KnowledgeBaseFactory
from .implementations.lightrag import LightRagKB
from .implementations.milvus import MilvusKB
from .manager import KnowledgeBaseManager
from .services.upload_graph_service import UploadGraphService

# 注册知识库类型
KnowledgeBaseFactory.register("milvus", MilvusKB, {"description": "基于 Milvus 的生产级向量知识库，适合高性能部署"})
KnowledgeBaseFactory.register("lightrag", LightRagKB, {"description": "基于图检索的知识库，支持实体关系构建和复杂查询"})

# 创建知识库管理器
work_dir = os.path.join(config.save_dir, "knowledge_base_data")
# 从环境变量或配置中获取数据库配置
db_config = {
    "host": os.getenv("MYSQL_HOST", config.mysql_host),
    "port": int(os.getenv("MYSQL_PORT", config.mysql_port)),
    "user": os.getenv("MYSQL_USER", config.mysql_user),
    "password": os.getenv("MYSQL_PASSWORD", config.mysql_password),
    "database": os.getenv("MYSQL_DATABASE", config.mysql_database)
}
knowledge_base = KnowledgeBaseManager(work_dir, db_config=db_config)

# 创建图数据库实例
graph_base = UploadGraphService()

# 向后兼容：让 GraphDatabase 指向 UploadGraphService
GraphDatabase = UploadGraphService

__all__ = ["GraphDatabase", "UploadGraphService", "knowledge_base", "graph_base"]
