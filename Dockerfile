# TeleSubmit v2 - Telegram 投稿机器人
# 基于 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 安装系统依赖
# gcc 和 python3-dev 用于编译 Whoosh 等 Python 包
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
# data: 数据库和搜索索引
# logs: 日志文件
RUN mkdir -p logs data data/search_index

# 设置目录权限
RUN chmod -R 755 logs data

# 暴露端口（为未来的 webhook 功能预留）
# EXPOSE 8443

# 健康检查
# 检查主进程是否存在，而不仅仅是配置文件
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import os, psutil; exit(0 if any('main.py' in ' '.join(p.cmdline()) for p in psutil.process_iter(['cmdline'])) else 1)" || exit 1

# 运行机器人
CMD ["python", "-u", "main.py"]

