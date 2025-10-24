#!/bin/bash

# TeleSubmit v2 启动脚本
# 支持本地运行和开发环境

set -e

echo "====================================="
echo "  TeleSubmit v2 - 投稿机器人"
echo "====================================="
echo ""

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请安装 Python 3.10 或更高版本"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 检查版本是否满足要求 (>= 3.10)
required_version="3.10"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "⚠️  警告: 推荐使用 Python 3.10 或更高版本"
fi

# 检查配置文件
if [ ! -f "config.ini" ] && [ -z "$TOKEN" ]; then
    echo ""
    echo "⚠️  未找到配置文件 config.ini"
    echo ""
    
    # 检查是否有配置向导
    if [ -f "setup_wizard.py" ]; then
        echo "🎯 检测到配置向导，是否运行配置向导？"
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
            python3 setup_wizard.py
            
            # 检查配置向导是否成功
            if [ $? -ne 0 ] || [ ! -f "config.ini" ]; then
                echo ""
                echo "❌ 配置向导未完成，无法启动机器人"
                exit 1
            fi
            
            echo ""
            echo "✅ 配置完成！继续启动机器人..."
        else
            echo ""
            echo "您选择了跳过配置向导。"
            echo ""
            if [ -f "config.ini.example" ]; then
                echo "请手动配置："
                echo "  1. 复制示例配置: cp config.ini.example config.ini"
                echo "  2. 编辑配置文件: nano config.ini"
                echo "  3. 或设置环境变量: export TOKEN=your_token CHANNEL_ID=your_channel"
            else
                echo "请设置环境变量 TOKEN 和 CHANNEL_ID"
            fi
            exit 1
        fi
    else
        echo "❌ 错误: 未找到配置文件"
        echo ""
        if [ -f "config.ini.example" ]; then
            echo "请执行以下操作之一："
            echo "  1. 复制示例配置: cp config.ini.example config.ini"
            echo "  2. 设置环境变量: export TOKEN=your_token CHANNEL_ID=your_channel"
        else
            echo "请设置环境变量 TOKEN 和 CHANNEL_ID"
        fi
        exit 1
    fi
fi

echo "✓ 配置文件检查通过"

# 创建必要的目录
echo ""
echo "📁 检查必要目录..."
mkdir -p data logs data/search_index
echo "✓ 目录已就绪"

# 检查依赖
echo ""
echo "📦 检查依赖..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "⚠️  未安装 python-telegram-bot，正在安装依赖..."
    pip3 install -r requirements.txt
    echo "✓ 依赖安装完成"
else
    # 检查搜索引擎依赖
    if ! python3 -c "import whoosh" 2>/dev/null; then
        echo "⚠️  未安装搜索引擎依赖，正在安装..."
        pip3 install whoosh jieba
        echo "✓ 搜索引擎依赖安装完成"
    else
        echo "✓ 依赖已安装"
    fi
fi

# 显示功能状态
echo ""
echo "🔧 功能状态:"
echo "  • 投稿系统: 启用"
echo "  • 搜索引擎: 启用 (Whoosh + Jieba)"
echo "  • 标签系统: 启用"
echo "  • 统计功能: 启用"
if [ -f "config.ini" ]; then
    bot_mode=$(grep "^BOT_MODE" config.ini 2>/dev/null | cut -d'=' -f2 | xargs || echo "MIXED")
    echo "  • 运行模式: $bot_mode"
fi

# 启动机器人
echo ""
echo "====================================="
echo "🚀 启动机器人..."
echo "====================================="
echo ""

# 使用 -u 参数确保输出不被缓冲
python3 -u main.py

