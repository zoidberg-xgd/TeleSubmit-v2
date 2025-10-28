# TeleSubmit v2 - Telegram 投稿机器人
# 基于 Python 3.11 slim 镜像
FROM python:3.11-slim

# 代理参数（可选，构建时通过 --build-arg 传入）
ARG HTTP_PROXY
ARG HTTPS_PROXY

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai \
    HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY}

# 安装系统依赖
# gcc 和 python3-dev 用于编译 Whoosh 等 Python 包
# 注意：apt-get 不使用代理，直接连接 Debian 源
RUN HTTP_PROXY="" HTTPS_PROXY="" http_proxy="" https_proxy="" apt-get update && \
    HTTP_PROXY="" HTTPS_PROXY="" http_proxy="" https_proxy="" apt-get install -y --no-install-recommends \
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

# 清除代理环境变量（避免影响运行时）
ENV HTTP_PROXY="" \
    HTTPS_PROXY=""

# 暴露端口（健康检查端口）
EXPOSE 8080

# 健康检查
# 通过 HTTP 健康检查端点检查服务状态
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# 运行机器人
CMD ["python", "-u", "main.py"]

