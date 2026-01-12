# MySQL快速配置指南

## 概述

本指南将帮助您快速将项目从默认的SQLite数据库切换到MySQL数据库。

## 步骤1: 准备MySQL环境

确保您的MySQL服务正在运行，并且您有创建数据库和表的权限。

## 步骤2: 配置环境变量

复制示例环境文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置MySQL参数：

```bash
# 数据库配置
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=yuxi_know

# 保存目录
SAVE_DIR=saves
```

## 步骤3: 初始化MySQL数据库

运行初始化脚本创建数据库和表结构：

```bash
python scripts/init_mysql_db.py
```

## 步骤4: 启动应用

现在您可以启动应用，它将使用MySQL作为主数据库：

```bash
# 使用uvicorn启动
uvicorn server.main:app --host 0.0.0.0 --port 5050

# 或者直接运行
python -m server.main
```

## 验证配置

启动后，检查应用日志确认是否成功连接到MySQL数据库：

```
INFO:     Uvicorn running on http://0.0.0.0:5050
INFO:     Database tables created/checked
```

## 故障排除

### 连接问题

如果遇到连接问题，请检查：

1. MySQL服务是否正在运行
2. 环境变量配置是否正确
3. MySQL用户是否有足够的权限
4. 防火墙是否阻止了连接

### 权限问题

确保MySQL用户具有以下权限：

```sql
GRANT ALL PRIVILEGES ON yuxi_know.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```

### 字符集问题

如果遇到中文乱码问题，请确保MySQL配置使用utf8mb4字符集：

```sql
-- 检查字符集设置
SHOW VARIABLES LIKE 'character_set%';
```

## 从现有SQLite数据迁移

如果要从现有的SQLite数据库迁移数据，请使用迁移脚本：

```bash
# 设置源和目标数据库参数
SOURCE_DB_TYPE=sqlite
SOURCE_SQLITE_PATH=saves/database/server.db
TARGET_DB_TYPE=mysql
TARGET_MYSQL_HOST=localhost
TARGET_MYSQL_USER=your_username
TARGET_MYSQL_PASSWORD=your_password
TARGET_MYSQL_DATABASE=yuxi_know

# 运行迁移
python scripts/database_migration.py
```

## 生产环境建议

1. 使用强密码并定期更换
2. 配置适当的连接池参数
3. 设置数据库备份策略
4. 监控数据库性能
5. 限制数据库访问权限