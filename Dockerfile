# 多阶段构建 Dockerfile
# 第一阶段：构建前端应用
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# 复制前端依赖文件
COPY package.json package-lock.json ./

# 安装前端依赖
RUN npm ci

# 复制前端源代码
COPY . .

# 构建前端应用（跳过ESLint检查）
RUN npm run build -- --no-lint

# 第二阶段：构建最终镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    libsqlite3-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 安装 Playwright 依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# 复制前端构建结果
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/public ./public
COPY --from=frontend-builder /app/node_modules ./node_modules
COPY --from=frontend-builder /app/package.json ./package.json

# 复制后端代码
COPY backend ./backend
COPY business ./business

# 安装 Python 依赖
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN cd backend && python -m playwright install --with-deps chromium

# 创建 SQLite 数据库目录
RUN mkdir -p /app/backend/db/sqlite
RUN touch /app/backend/db/sqlite/case_analysis.db
RUN chmod 777 /app/backend/db/sqlite/case_analysis.db

# 设置环境变量
ENV PYTHONPATH=/app:/app/backend
ENV NODE_ENV=production

# 暴露前端和后端端口
EXPOSE 3000 8000

# 创建启动脚本
RUN echo '#!/bin/bash\n\
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \n\
cd /app && npm start\n\
wait\n' > /app/start.sh && chmod +x /app/start.sh

# 设置启动命令
CMD ["/app/start.sh"]
