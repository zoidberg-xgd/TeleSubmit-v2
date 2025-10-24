#!/bin/bash

# TeleSubmit v2 一键快速启动脚本
# 自动检测环境，提供最佳启动方式

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🤖 TeleSubmit v2 快速启动向导                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检测是否首次运行
FIRST_RUN=false
if [ ! -f "config.ini" ]; then
    FIRST_RUN=true
fi

# 步骤 1: 配置检查
echo "📋 步骤 1/3: 配置检查"
echo "────────────────────────────────────────────────────────────────"

if [ "$FIRST_RUN" = true ]; then
    echo "✨ 检测到这是首次运行！"
    echo ""
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python 3 已安装"
        
        # 运行配置向导
        if [ -f "setup_wizard.py" ]; then
            echo ""
            echo "🎯 准备启动配置向导..."
            echo ""
            echo "配置向导将引导您完成以下配置："
            echo "  1️⃣  输入 Telegram Bot Token"
            echo "  2️⃣  设置投稿频道 ID"
            echo "  3️⃣  配置所有者 User ID"
            echo "  4️⃣  选择可选功能（搜索、通知等）"
            echo ""
            read -p "按回车键开始配置..." dummy
            
            python3 setup_wizard.py
            
            if [ $? -ne 0 ] || [ ! -f "config.ini" ]; then
                echo ""
                echo "❌ 配置未完成，无法继续"
                echo ""
                echo "💡 提示: 您也可以手动创建配置文件："
                echo "   cp config.ini.example config.ini"
                echo "   nano config.ini"
                exit 1
            fi
        else
            echo "⚠️  未找到配置向导，使用手动配置"
            if [ -f "config.ini.example" ]; then
                cp config.ini.example config.ini
                echo "✅ 已创建配置文件模板"
                echo ""
                echo "⚠️  请编辑 config.ini 填入真实配置，然后重新运行此脚本"
                exit 0
            fi
        fi
    else
        echo "⚠️  未找到 Python 3"
        if [ -f "config.ini.example" ]; then
            cp config.ini.example config.ini
            echo "✅ 已创建配置文件模板"
            echo ""
            echo "⚠️  请编辑 config.ini 填入真实配置，然后重新运行此脚本"
            exit 0
        fi
    fi
else
    echo "✅ 找到配置文件 config.ini"
fi

echo ""
echo "✅ 配置检查完成"
echo ""

# 步骤 2: 环境检测
echo "📋 步骤 2/3: 环境检测"
echo "────────────────────────────────────────────────────────────────"

DEPLOY_METHOD=""

# 检查 Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker 和 Docker Compose 已安装"
    DEPLOY_METHOD="docker"
elif command -v python3 &> /dev/null; then
    echo "✅ Python 3 已安装"
    DEPLOY_METHOD="python"
else
    echo "❌ 错误: 未找到 Docker 或 Python 3"
    echo ""
    echo "请安装以下任一环境："
    echo "  • Docker + Docker Compose (推荐)"
    echo "  • Python 3.10 或更高版本"
    exit 1
fi

echo ""
echo "✅ 环境检测完成"
echo ""

# 步骤 3: 选择部署方式
echo "📋 步骤 3/3: 选择部署方式"
echo "────────────────────────────────────────────────────────────────"
echo ""

if [ "$DEPLOY_METHOD" = "docker" ]; then
    echo "🐳 推荐使用 Docker 部署（更稳定、易管理）"
    echo ""
    echo "可用选项："
    echo "  1. Docker 部署（推荐）"
    echo "  2. 直接运行（开发模式）"
    echo "  3. 退出"
    echo ""
    read -p "请选择 [1-3]: " choice
    
    case $choice in
        1)
            echo ""
            echo "🐳 使用 Docker 部署..."
            echo ""
            
            # 检查是否需要重新构建
            if docker images | grep -q "telesubmit-v2"; then
                read -p "是否强制重新构建镜像？(y/N): " rebuild
                if [[ "$rebuild" =~ ^[Yy]$ ]]; then
                    exec ./deploy.sh --rebuild
                else
                    exec ./deploy.sh
                fi
            else
                exec ./deploy.sh
            fi
            ;;
        2)
            echo ""
            echo "💻 直接运行模式..."
            echo ""
            exec ./start.sh
            ;;
        3)
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo "❌ 无效选择"
            exit 1
            ;;
    esac
    
elif [ "$DEPLOY_METHOD" = "python" ]; then
    echo "💻 使用 Python 直接运行"
    echo ""
    read -p "按回车键继续..." dummy
    exec ./start.sh
fi

# 不应该到达这里
echo "❌ 未知错误"
exit 1

