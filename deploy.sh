#!/bin/bash

# TeleSubmit Docker 一键部署脚本
# 用法: ./deploy.sh

set -e

echo "====================================="
echo "  TeleSubmit Docker 一键部署脚本"
echo "====================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查配置文件是否存在
if [ ! -f "config.ini" ]; then
    echo "⚠️  未找到 config.ini 文件"
    
    if [ -f "config.ini.example" ]; then
        echo "正在从 config.ini.example 创建配置文件..."
        cp config.ini.example config.ini
        echo "✅ 配置文件已创建"
        echo ""
        echo "⚠️  请编辑 config.ini 文件，填入以下必要信息："
        echo "   - TOKEN: 您的 Telegram 机器人令牌"
        echo "   - CHANNEL_ID: 目标频道 ID"
        echo "   - OWNER_ID: 您的 Telegram 用户 ID"
        echo ""
        echo "编辑完成后，请重新运行此脚本"
        exit 0
    else
        echo "❌ 错误: 未找到 config.ini.example 文件"
        exit 1
    fi
fi

echo "✅ 配置文件检查通过"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs
chmod 755 data logs
echo "✅ 目录创建完成"
echo ""

# 停止可能存在的旧容器
echo "🛑 检查并停止旧容器..."
if docker ps -a | grep -q telesubmit-bot; then
    docker-compose down
    echo "✅ 旧容器已停止"
else
    echo "✅ 未发现旧容器"
fi
echo ""

# 构建并启动容器
echo "🔨 构建 Docker 镜像..."
docker-compose build
echo "✅ 镜像构建完成"
echo ""

echo "🚀 启动容器..."
docker-compose up -d
echo "✅ 容器已启动"
echo ""

# 等待几秒让容器完全启动
echo "⏳ 等待容器启动..."
sleep 3

# 检查容器状态
echo "📊 检查容器状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 容器运行正常"
    echo ""
    echo "====================================="
    echo "  部署完成！"
    echo "====================================="
    echo ""
    echo "📝 常用命令："
    echo "   查看日志: docker-compose logs -f"
    echo "   停止容器: docker-compose stop"
    echo "   启动容器: docker-compose start"
    echo "   重启容器: docker-compose restart"
    echo "   查看状态: docker-compose ps"
    echo ""
    echo "🤖 现在可以在 Telegram 中使用您的机器人了！"
    echo "   发送 /start 命令开始使用"
    echo ""
    
    # 询问是否查看日志
    read -p "是否立即查看日志？(y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose logs -f
    fi
else
    echo "❌ 错误: 容器启动失败"
    echo "请查看日志: docker-compose logs"
    exit 1
fi

