# 数据库迁移指南

## 概述

本项目默认使用 SQLite 作为主业务数据库，但支持迁移到 MySQL 或 PostgreSQL。本文档将详细介绍如何配置和迁移数据库。

## 支持的数据库类型

- SQLite (默认)
- MySQL
- PostgreSQL

## 配置说明

### 1. 配置优先级

项目采用多层配置系统，优先级从高到低：
1. 环境变量 (最高优先级)
2. TOML 配置文件 (中等优先级) 
3. 代码中的默认值 (最低优先级)

### 2. 环境变量配置

在项目根目录创建 `.env` 文件或在运行时设置环境变量：

#### SQLite (默认配置)
```bash
DB_TYPE=sqlite
SAVE_DIR=saves
```

#### MySQL 配置
```bash
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=yuxi_know
SAVE_DIR=saves
```

#### PostgreSQL 配置
```bash
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=yuxi_know
SAVE_DIR=saves
```

### 3. TOML 配置文件

也可以通过 TOML 配置文件设置数据库参数，编辑 `saves/config/base.toml`:

```toml
db_type = "mysql"
mysql_host = "localhost"
mysql_port = 3306
mysql_user = "root"
mysql_password = "your_password"
mysql_database = "yuxi_know"
```

### 4. Docker 环境配置

如果使用 Docker 部署，可以在 `docker-compose.yml` 中配置环境变量：

```yaml
services:
  api:
    # ... 其他配置
    environment:
      - DB_TYPE=mysql
      - MYSQL_HOST=mysql
      - MYSQL_PORT=3306
      - MYSQL_USER=root
      - MYSQL_PASSWORD=your_password
      - MYSQL_DATABASE=yuxi_know
      - SAVE_DIR=saves
```

## 数据迁移步骤

### 从 SQLite 迁移到 MySQL/PostgreSQL

#### 1. 准备目标数据库

首先在目标数据库系统中创建数据库：

**MySQL:**
```sql
CREATE DATABASE yuxi_know CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**PostgreSQL:**
```sql
CREATE DATABASE yuxi_know;
-- 创建用户并授权 (可选)
CREATE USER yuxi_know WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE yuxi_know TO yuxi_know;
```

#### 2. 配置环境变量

设置环境变量指向新的数据库系统。

#### 3. 运行迁移脚本

```bash
# 启动应用，自动执行迁移
python -m server.main
```

或者运行特定的迁移脚本：
```bash
python scripts/migrate_user_soft_delete.py
```

#### 4. 使用数据库迁移脚本迁移数据

如果需要从现有数据库迁移到新数据库，可以使用数据库迁移脚本：

```bash
# 设置源数据库（当前数据库）和目标数据库环境变量
SOURCE_DB_TYPE=sqlite
SOURCE_SQLITE_PATH=saves/database/server.db
TARGET_DB_TYPE=mysql
TARGET_MYSQL_HOST=localhost
TARGET_MYSQL_USER=your_username
TARGET_MYSQL_PASSWORD=your_password
TARGET_MYSQL_DATABASE=your_database_name

# 运行迁移脚本
python scripts/database_migration.py
```

#### 5. 验证数据

启动应用后，检查数据库表是否已正确创建并包含所需的数据。

## 数据库连接配置详解

### 连接字符串格式

- SQLite: `sqlite+aiosqlite:///path/to/database.db`
- MySQL: `mysql+aiomysql://user:password@host:port/database`
- PostgreSQL: `postgresql+asyncpg://user:password@host:port/database`

### 连接池配置

默认配置包括连接池设置，以确保在高并发场景下的性能。

## MySQL 数据库初始化

当项目使用 MySQL 作为主数据库时，需要进行以下初始化步骤：

### 1. 创建数据库

首先在 MySQL 服务器中创建数据库：
```sql
CREATE DATABASE yuxi_know CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 配置连接参数

设置以下环境变量：
```bash
DB_TYPE=mysql
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=yuxi_know
```

### 3. 使用初始化脚本

项目提供了MySQL数据库初始化脚本，可以自动创建数据库和表结构：

```bash
# 复制示例环境文件
cp .env.example .env

# 编辑 .env 文件配置MySQL参数
# DB_TYPE=mysql
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password
# MYSQL_DATABASE=yuxi_know

# 运行初始化脚本
python scripts/init_mysql_db.py
```

### 4. 启动项目初始化

首次启动项目时，系统会自动创建所需的数据表：
```bash
python -m server.main
```

或者使用 uvicorn：
```bash
uvicorn server.main:app --host 0.0.0.0 --port 5050
```

### 5. 验证初始化

检查数据库是否已创建以下表：
- users
- conversations
- messages
- tool_calls
- conversation_stats
- operation_logs
- message_feedbacks
- migration_versions

## 注意事项

1. **数据备份**: 在进行任何数据库迁移之前，请务必备份现有数据。
2. **权限配置**: 确保数据库用户具有创建表和执行 DDL 的权限。
3. **字符集**: 推荐使用 UTF-8 字符集以支持中文内容。
4. **性能**: 对于生产环境，建议使用 MySQL 或 PostgreSQL 以获得更好的性能。
5. **索引**: 某些索引可能需要手动创建以优化查询性能。

## 常见问题

### 1. 迁移失败

- 检查数据库连接参数是否正确
- 确认数据库用户具有创建表和执行 DDL 的权限
- 查看日志中的具体错误信息

### 2. 性能问题

- 确保在生产环境中使用适当的数据库（MySQL/PostgreSQL）
- 配置适当的连接池大小
- 定期优化数据库表结构

### 3. 字符编码问题

- MySQL 使用 `utf8mb4` 字符集
- PostgreSQL 默认支持 UTF-8
- 确保应用程序和数据库使用相同的字符编码

## 验证迁移成功

迁移完成后，可以通过以下方式验证：

1. 检查数据库表是否已创建
2. 验证用户数据是否已迁移
3. 测试应用程序功能是否正常
4. 检查日志中是否有错误信息