#!/bin/bash

# TeleSubmit v2 重启脚本
# 用于在修改配置文件后快速重启机器人
#
# 用法:
#   ./restart.sh          # 重启机器人
#   ./restart.sh --stop   # 仅停止机器人

set -e

echo "====================================="
echo "  TeleSubmit v2 - 重启脚本"
echo "====================================="
echo ""

# 解析参数
STOP_ONLY=false
if [ "$1" = "--stop" ] || [ "$1" = "-s" ]; then
    STOP_ONLY=true
fi

# 查找并停止现有进程
echo "🔍 查找运行中的机器人进程..."
BOT_PIDS=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' || echo "")

if [ -n "$BOT_PIDS" ]; then
    # 可能有多个进程，逐个处理
    echo "$BOT_PIDS" | while read -r PID; do
        if [ -n "$PID" ]; then
            echo "✓ 找到进程 PID: $PID"
            echo "⏹️  正在停止机器人..."
            
            # 优雅停止
            kill $PID 2>/dev/null || true
            
            # 等待进程退出（最多10秒）
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo "✅ 进程 $PID 已停止"
                    break
                fi
                sleep 1
            done
            
            # 如果还在运行，强制终止
            if ps -p $PID > /dev/null 2>&1; then
                echo "⚠️  进程 $PID 未响应，强制终止..."
                kill -9 $PID 2>/dev/null || true
                sleep 1
                
                if ps -p $PID > /dev/null 2>&1; then
                    echo "❌ 无法停止进程 $PID，请手动处理"
                else
                    echo "✅ 进程 $PID 已强制停止"
                fi
            fi
        fi
    done
    
    echo ""
    echo "✅ 所有机器人进程已停止"
else
    echo "ℹ️  未找到运行中的机器人进程"
fi

# 如果是仅停止模式，退出
if [ "$STOP_ONLY" = true ]; then
    echo ""
    echo "====================================="
    echo "✅ 已停止机器人（未重启）"
    echo "====================================="
    exit 0
fi

# 检查配置文件
echo ""
echo "🔧 检查配置文件..."
if [ ! -f "config.ini" ]; then
    echo "❌ 错误: 未找到 config.ini"
    echo "请先创建配置文件再启动机器人"
    exit 1
fi

# 可选：验证配置文件
if [ -f "check_config.py" ]; then
    echo "🔍 验证配置文件..."
    if python3 check_config.py > /dev/null 2>&1; then
        echo "✓ 配置文件验证通过"
    else
        echo "⚠️  配置文件可能存在问题，但将继续启动"
    fi
fi

# 重新启动
echo ""
echo "🚀 重新启动机器人..."
echo "====================================="
echo ""

# 检查 start.sh 是否存在
if [ ! -f "start.sh" ]; then
    echo "⚠️  未找到 start.sh，使用直接启动方式"
    echo ""
    python3 -u main.py
else
    ./start.sh
fi

