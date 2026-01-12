"""
Centralized configuration constants for LightRAG.

This module defines default values for configuration constants used across
different parts of the LightRAG system. Centralizing these values ensures
consistency and makes maintenance easier.
"""

# ===================== 云南电网业务特定配置 =====================
# 云南电网实体类型定义
DEFAULT_ENTITY_TYPES = [
    "人才",           # 人员个体，如"李鹏"、"张伟"
    "项目",           # 具体项目/课题，如"云南智能电网示范项目"、"云电送粤工程"
    "组织机构",       # 公司/部门/单位，如"云南电网公司"、"南方电网公司"
    "技术领域",       # 技术方向，如"智能电网技术"、"新能源并网技术"
    "技能专长",       # 具体技能，如"数字化转型"、"变电站自动化"
    "成果专利",       # 奖项/专利/论文，如"电力行业杰出领导奖"、"全国五一劳动奖章"
    "学历背景",       # 学校/专业，如"清华大学电气工程博士"、"华北电力大学"
    "职称等级",       # 职称/职务，如"董事长"、"总经理"、"首席技术专家"
    "专家类别",       # 专家类型，如"青年技术骨干"、"技术专家"
    "培训经历",       # 培训/学习，如"数字化转型高级研修班"
    "评价标准",       # 评价指标，如"5亿元"、"99.98%"、"15年"、"2018年"
    "专业方向",       # 专业领域，如"电气工程"、"电力系统"
    "项目角色",       # 在项目中的角色，如"项目负责人"、"项目成员"
    "区域单位",       # 地域性单位，如"昆明市"、"云南省"
]

# 默认处理语言 - 云南电网业务主要使用中文
DEFAULT_SUMMARY_LANGUAGE = "Chinese"

# ===================== 服务器设置默认值 =====================
DEFAULT_WOKERS = 2
DEFAULT_MAX_GRAPH_NODES = 1000

# ===================== 提取设置默认值 =====================
# 默认最大实体名称长度 - 云南电网实体名称通常较短
DEFAULT_ENTITY_NAME_MAX_LENGTH = 256
# 默认最大提取迭代次数
DEFAULT_MAX_GLEANING = 1

# 触发LLM总结的描述片段数量阈值
DEFAULT_FORCE_LLM_SUMMARY_ON_MERGE = 8
# 触发LLM总结的最大描述token大小
DEFAULT_SUMMARY_MAX_TOKENS = 1200
# 推荐的LLM总结输出长度（token）
DEFAULT_SUMMARY_LENGTH_RECOMMENDED = 600
# 发送给LLM进行总结的最大上下文token大小
DEFAULT_SUMMARY_CONTEXT_SIZE = 12000

# 用于实体描述、source_id和关系关键字段的分隔符（插入数据后不可更改）
GRAPH_FIELD_SEP = "<SEP>"

# ===================== 查询和检索配置默认值 =====================
# 默认top_k值 - 云南电网知识图谱规模适中
DEFAULT_TOP_K = 40
# 默认chunk_top_k值
DEFAULT_CHUNK_TOP_K = 20
# 实体最大token数 - 云南电网实体描述相对简洁
DEFAULT_MAX_ENTITY_TOKENS = 6000
# 关系最大token数
DEFAULT_MAX_RELATION_TOKENS = 8000
# 总token数上限
DEFAULT_MAX_TOTAL_TOKENS = 30000
# 余弦相似度阈值 - 云南电网查询需要较高精度
DEFAULT_COSINE_THRESHOLD = 0.3
# 相关chunk数量
DEFAULT_RELATED_CHUNK_NUMBER = 5
# 知识图谱chunk选择方法 - 云南电网推荐使用向量相似度
DEFAULT_KG_CHUNK_PICK_METHOD = "VECTOR"

# TODO: Deprated. All conversation_history messages is send to LLM.
DEFAULT_HISTORY_TURNS = 0

# ===================== 重排序配置默认值 =====================
DEFAULT_MIN_RERANK_SCORE = 0.0
DEFAULT_RERANK_BINDING = "null"

# ===================== 源ID限制配置 =====================
# 云南电网实体和关系的源ID默认最大数量
DEFAULT_MAX_SOURCE_IDS_PER_ENTITY = 300
DEFAULT_MAX_SOURCE_IDS_PER_RELATION = 300

# 控制chunk_id限制方法: FIFO, KEEP
#   FIFO: 先进先出（保持最新）
#   KEEP: 保留最旧（减少合并操作，更快）
SOURCE_IDS_LIMIT_METHOD_KEEP = "KEEP"
SOURCE_IDS_LIMIT_METHOD_FIFO = "FIFO"
DEFAULT_SOURCE_IDS_LIMIT_METHOD = SOURCE_IDS_LIMIT_METHOD_FIFO
VALID_SOURCE_IDS_LIMIT_METHODS = {
    SOURCE_IDS_LIMIT_METHOD_KEEP,
    SOURCE_IDS_LIMIT_METHOD_FIFO,
}

# 实体/关系file_path字段中存储的最大文件路径数（仅用于显示，不影响查询性能）
DEFAULT_MAX_FILE_PATHS = 100
# Milvus Schema中file_path字段长度（不应更改）
DEFAULT_MAX_FILE_PATH_LENGTH = 32768
# 元数据中更多文件路径的占位符（不应更改）
DEFAULT_FILE_PATH_MORE_PLACEHOLDER = "truncated"

# ===================== LLM配置默认值 =====================
DEFAULT_TEMPERATURE = 0.7  # 云南电网需要更确定的回答

# ===================== 异步配置默认值 =====================
DEFAULT_MAX_ASYNC = 4  # 默认最大异步操作数
DEFAULT_MAX_PARALLEL_INSERT = 2  # 默认最大并行插入操作数

# ===================== 嵌入配置默认值 =====================
DEFAULT_EMBEDDING_FUNC_MAX_ASYNC = 8  # 嵌入函数默认最大异步数
DEFAULT_EMBEDDING_BATCH_NUM = 10  # 嵌入计算的默认批处理大小

# ===================== 超时配置 =====================
DEFAULT_TIMEOUT = 300  # Gunicorn worker超时
DEFAULT_LLM_TIMEOUT = 180  # 默认LLM超时
DEFAULT_EMBEDDING_TIMEOUT = 30  # 默认嵌入超时

# ===================== 日志配置默认值 =====================
DEFAULT_LOG_MAX_BYTES = 10485760  # 默认10MB
DEFAULT_LOG_BACKUP_COUNT = 5  # 默认5个备份
DEFAULT_LOG_FILENAME = "lightrag.log"  # 默认日志文件名

# ===================== Ollama服务器配置默认值 =====================
DEFAULT_OLLAMA_MODEL_NAME = "lightrag"
DEFAULT_OLLAMA_MODEL_TAG = "latest"
DEFAULT_OLLAMA_MODEL_SIZE = 7365960935
DEFAULT_OLLAMA_CREATED_AT = "2024-01-15T00:00:00Z"
DEFAULT_OLLAMA_DIGEST = "sha256:lightrag"

# ===================== 云南电网特定关系类型 =====================
# 云南电网标准关系类型
YUNNAN_GRID_RELATION_TYPES = [
    "全资子公司",     # 组织间关系
    "总部所在地",     # 组织与位置关系
    "服务区域",       # 组织与区域关系
    "担任职务",       # 人员与职务关系
    "任职开始时间",   # 人员与时间关系
    "曾任职务",       # 人员与历史职务关系
    "曾任时间",       # 人员与历史时间关系
    "获得奖项",       # 人员与奖项关系
    "教育背景",       # 人员与学历关系
    "专业领域",       # 人员与技术关系
    "工作经验",       # 人员与时间关系
    "技术专长",       # 人员与技术关系
    "主导项目",       # 人员与项目关系
    "毕业时间",       # 人员与时间关系
    "毕业院校",       # 人员与学校关系
    "负责项目",       # 人员与项目关系
    "获得称号",       # 人员与荣誉关系
    "获得时间",       # 人员与时间关系
    "现任职务",       # 人员与当前职务关系
    "调动时间",       # 人员与时间关系
    "调动方式",       # 人员与项目关系
    "项目状态",       # 项目与状态关系
    "开始日期",       # 项目与时间关系
    "项目预算",       # 项目与金额关系
    "项目负责人",     # 项目与人员关系
    "项目成员",       # 项目与人员关系
    "培训时长",       # 培训与时间关系
    "完成日期",       # 培训与时间关系
    "颁发证书",       # 培训与证书关系
    "培训讲师",       # 培训与人员关系
    "培训学员",       # 培训与人员关系
    "项目周期",       # 项目与时间关系
    "培训年份",       # 培训与时间关系
]

# ===================== 云南电网实体提取优化参数 =====================
# 实体提取最大重试次数
YUNNAN_ENTITY_EXTRACT_MAX_RETRY = 3
# 实体提取置信度阈值
YUNNAN_ENTITY_CONFIDENCE_THRESHOLD = 0.8
# 关系提取置信度阈值
YUNNAN_RELATION_CONFIDENCE_THRESHOLD = 0.7