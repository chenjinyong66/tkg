## 本地启动

### 后端启动（FastAPI）

1. **安装依赖管理工具 uv**：
   ```bash
   pip install uv
   ```


2. **安装项目依赖**：
   ```bash
   uv sync
   ```


3. **配置环境变量**：
   ```bash
   cp .env.template .env
   ```

   然后编辑 `.env` 文件，配置必要的环境变量。

4. **启动后端服务**：
   ```bash
   uv run python server/main.py
   ```


或者使用 uvicorn 直接启动：
   ```bash
   uv run uvicorn server.main:app --host 0.0.0.0 --port 5050 --reload
   ```


后端服务将在 `http://localhost:5050` 上运行。

### 前端启动（Vue.js）

1. **安装 Node.js 和 pnpm**：
   确保你已经安装了 Node.js（推荐版本 16+）和 pnpm。如果没有安装 pnpm：
   ```bash
   npm install -g pnpm
   ```


2. **进入 web 目录并安装依赖**：
   ```bash
   cd web
   pnpm install
   ```


3. **启动前端开发服务器**：
   ```bash
   pnpm run dev
   ```


或者使用指定主机的方式：
   ```bash
   pnpm run server
   ```


前端服务将在 `http://localhost:5173` 上运行。

### 必需的依赖服务

由于项目依赖多个数据库和存储服务，即使在本地运行前后端，也需要运行这些依赖服务。建议使用混合模式：

1. **使用 Docker 运行依赖服务**：
   ```bash
   # 只启动依赖服务（数据库等）
   docker compose up -d graph milvus minio etcd
   ```


2. **配置环境变量**：
   在 `.env` 文件中设置正确的数据库连接信息：
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=0123456789
   MILVUS_URI=http://localhost:19530
   MINIO_URI=http://localhost:9000
   ```


### 注意事项

1. **环境变量配置**：
  - 确保正确配置了所有服务的连接信息
  - 特别注意数据库连接参数

2. **端口冲突**：
  - 确保本地没有其他程序占用项目所需端口（5050、5173、7474、7687、19530、9000、9001）

3. **跨域问题**：
  - 前端默认配置了代理，将 `/api` 请求转发到后端服务
  - 确保 `VITE_API_URL` 环境变量设置正确

4. **依赖服务健康检查**：
  - 确认 Neo4j、Milvus 和 MinIO 服务正常运行
  - 可以通过 `docker logs` 命令查看服务状态

通过以上步骤，您就可以在本地不使用 Docker 容器运行项目的核心前后端服务，同时使用 Docker 运行依赖服务，这样既能享受本地开发的便利，又能保证依赖服务的稳定运行。

# todo
知识图谱查询、页面展示、智能助手