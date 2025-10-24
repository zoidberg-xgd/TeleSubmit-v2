#!/bin/bash

# TeleSubmit v2 Docker 一键部署脚本
# 用法: ./deploy.sh [选项]
# 选项:
#   --rebuild  强制重新构建镜像
#   --clean    清理旧数据后重新部署

set -e

echo "====================================="
echo "  TeleSubmit v2 Docker 部署脚本"
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
    echo ""
    
    # 检查是否有配置向导
    if [ -f "setup_wizard.py" ]; then
        echo "🎯 检测到配置向导，推荐使用配置向导快速配置！"
        echo ""
        echo "配置向导将帮助您："
        echo "  • 交互式输入 Bot Token、频道 ID 等配置"
        echo "  • 自动验证配置格式"
        echo "  • 创建必要的数据目录"
        echo ""
        read -p "是否运行配置向导？(y/n) [y]: " run_wizard
        run_wizard=${run_wizard:-y}
        
        if [[ "$run_wizard" =~ ^[Yy]$ ]]; then
            echo ""
            echo "🚀 启动配置向导..."
            echo ""
            
            # 检查 Python 是否可用
            if ! command -v python3 &> /dev/null; then
                echo "❌ 错误: 需要 Python 3 运行配置向导"
                echo "请手动创建配置文件或安装 Python 3"
                exit 1
            fi
            
            python3 setup_wizard.py
            
            # 检查配置向导是否成功
            if [ $? -ne 0 ] || [ ! -f "config.ini" ]; then
                echo ""
                echo "❌ 配置向导未完成，无法部署"
                exit 1
            fi
            
            echo ""
            echo "✅ 配置完成！继续部署..."
            echo ""
        else
            echo ""
            echo "您选择了跳过配置向导。"
            echo ""
        fi
    fi
    
    # 如果还是没有配置文件，尝试使用示例配置
    if [ ! -f "config.ini" ]; then
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
fi

echo "✅ 配置文件检查通过"
echo ""

# 解析命令行参数
REBUILD=false
CLEAN=false
for arg in "$@"; do
    case $arg in
        --rebuild)
            REBUILD=true
            ;;
        --clean)
            CLEAN=true
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --rebuild  强制重新构建 Docker 镜像"
            echo "  --clean    清理旧数据后重新部署（谨慎使用！）"
            echo "  --help     显示此帮助信息"
            exit 0
            ;;
        *)
            echo "⚠️  未知选项: $arg"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs data/search_index
chmod -R 755 data logs
echo "✅ 目录创建完成"
echo ""

# 如果启用了清理选项
if [ "$CLEAN" = true ]; then
    echo "⚠️  警告: 将清理所有数据（数据库和搜索索引）"
    read -p "确定要继续吗？(yes/NO): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "🗑️  清理旧数据..."
        rm -rf data/*.db data/search_index/*
        echo "✅ 数据已清理"
    else
        echo "❌ 已取消清理"
        exit 0
    fi
    echo ""
fi

# 停止可能存在的旧容器
echo "🛑 检查并停止旧容器..."
if docker ps -a | grep -q -E "telesubmit-bot|telesubmit-v2"; then
    docker-compose down
    echo "✅ 旧容器已停止"
else
    echo "✅ 未发现旧容器"
fi
echo ""

# 构建并启动容器
if [ "$REBUILD" = true ]; then
    echo "🔨 强制重新构建 Docker 镜像..."
    docker-compose build --no-cache
else
    echo "🔨 构建 Docker 镜像..."
    docker-compose build
fi
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
    echo "  🎉 部署完成！"
    echo "====================================="
    echo ""
    echo "📝 常用命令："
    echo "   查看日志:   docker-compose logs -f"
    echo "   停止容器:   docker-compose stop"
    echo "   启动容器:   docker-compose start"
    echo "   重启容器:   docker-compose restart"
    echo "   查看状态:   docker-compose ps"
    echo "   进入容器:   docker exec -it telesubmit-v2 /bin/bash"
    echo ""
    echo "🔧 数据迁移（如果需要）："
    echo "   docker exec telesubmit-v2 python migrate_to_search.py"
    echo ""
    echo "🤖 TeleSubmit v2 功能："
    echo "   • 投稿管理 - /submit, /status"
    echo "   • 搜索功能 - /search, /tags"
    echo "   • 统计分析 - /stats"
    echo "   • 帮助信息 - /help"
    echo ""
    echo "💡 在 Telegram 中发送 /start 开始使用"
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

