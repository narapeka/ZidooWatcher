# 多阶段构建 Dockerfile for ZidooWatcher
# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm ci --only=production

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# 阶段2: 运行后端 + 前端静态文件
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 从前端构建阶段复制构建结果
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 复制配置文件
COPY config/ /config/

# 创建日志目录
RUN mkdir -p /config/logs

# 暴露端口
EXPOSE 7502

# 设置环境变量
ENV PYTHONPATH=/app/backend

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7502/api/health || exit 1

# 启动命令 - 使用 uvicorn 直接启动，生产环境优化
CMD ["uvicorn", "backend.main:fastapi_app", "--host", "0.0.0.0", "--port", "7502", "--workers", "1"] 