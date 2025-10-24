#!/bin/bash

# TeleSubmit v2 - 文件名搜索功能升级脚本
# 自动完成所有升级步骤

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TeleSubmit v2 - 文件名搜索功能升级脚本               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 进度显示函数
progress() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否在项目根目录
if [ ! -f "main.py" ]; then
    error "请在 TeleSubmit-v2 项目根目录运行此脚本"
    exit 1
fi

# 步骤 1: 备份数据
echo ""
progress "步骤 1/6: 备份数据..."
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)

if [ -f "data/submissions.db" ]; then
    cp data/submissions.db "data/submissions.db.backup_${BACKUP_TIME}"
    success "数据库已备份: submissions.db.backup_${BACKUP_TIME}"
else
    warning "未找到数据库文件，跳过备份"
fi

if [ -d "data/search_index" ]; then
    cp -r data/search_index "data/search_index.backup_${BACKUP_TIME}"
    success "搜索索引已备份: search_index.backup_${BACKUP_TIME}"
fi

# 步骤 2: 停止机器人
echo ""
progress "步骤 2/6: 停止机器人..."
BOT_PIDS=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' || echo "")

if [ -n "$BOT_PIDS" ]; then
    echo "$BOT_PIDS" | while read -r PID; do
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null || true
            
            # 等待进程退出
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    success "机器人进程 $PID 已停止"
                    break
                fi
                sleep 1
            done
            
            # 强制终止
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null || true
                warning "强制停止进程 $PID"
            fi
        fi
    done
else
    warning "未找到运行中的机器人进程"
fi

# 步骤 3: 更新代码（可选）
echo ""
progress "步骤 3/6: 检查代码更新..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        warning "检测到未提交的更改"
        read -p "是否暂存并拉取最新代码？(y/n) [n]: " do_pull
        do_pull=${do_pull:-n}
        
        if [[ "$do_pull" =~ ^[Yy]$ ]]; then
            git stash
            git pull origin main
            git stash pop
            success "代码已更新"
        else
            warning "跳过代码更新"
        fi
    else
        read -p "是否拉取最新代码？(y/n) [y]: " do_pull
        do_pull=${do_pull:-y}
        
        if [[ "$do_pull" =~ ^[Yy]$ ]]; then
            git pull origin main
            success "代码已更新"
        else
            warning "跳过代码更新"
        fi
    fi
else
    warning "不是 Git 仓库，跳过代码更新"
fi

# 步骤 4: 检查并安装依赖
echo ""
progress "步骤 4/6: 检查依赖..."

if ! python3 -c "import whoosh" 2>/dev/null; then
    warning "未安装 whoosh，正在安装..."
    pip3 install whoosh jieba
    success "搜索引擎依赖已安装"
else
    success "依赖检查通过"
fi

# 步骤 5: 数据库迁移
echo ""
progress "步骤 5/6: 运行数据库迁移..."

if [ -f "migrate_add_filename.py" ]; then
    python3 migrate_add_filename.py
    if [ $? -eq 0 ]; then
        success "数据库迁移完成"
    else
        error "数据库迁移失败"
        exit 1
    fi
else
    error "未找到迁移脚本 migrate_add_filename.py"
    exit 1
fi

# 步骤 6: 重建搜索索引
echo ""
progress "步骤 6/6: 重建搜索索引..."

if [ -f "migrate_to_search.py" ]; then
    echo "y" | python3 migrate_to_search.py --clear
    if [ $? -eq 0 ]; then
        success "搜索索引重建完成"
    else
        error "搜索索引重建失败"
        exit 1
    fi
else
    error "未找到索引重建脚本 migrate_to_search.py"
    exit 1
fi

# 完成
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ 升级完成！                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 升级摘要:"
echo "  • 数据库已迁移（新增 filename 字段）"
echo "  • 搜索索引已重建（支持文件名搜索）"
echo "  • 备份已创建：${BACKUP_TIME}"
echo ""
echo "🚀 下一步："
echo "  1. 重启机器人: ./restart.sh"
echo "  2. 或后台运行: nohup python3 -u main.py > logs/bot.log 2>&1 &"
echo ""
echo "✨ 新功能："
echo "  • 搜索支持文件名字段"
echo "  • 文档上传时自动保存文件名"
echo "  • 多字段搜索：标题 + 简介 + 标签 + 文件名"
echo ""
echo "📖 详细文档："
echo "  • 快速指南: cat UPGRADE_QUICKSTART.md"
echo "  • 重新部署: cat REDEPLOY_GUIDE.md"
echo "  • 详细升级: cat FILENAME_SEARCH_UPGRADE.md"
echo ""

# 询问是否立即重启
read -p "是否立即重启机器人？(y/n) [y]: " do_restart
do_restart=${do_restart:-y}

if [[ "$do_restart" =~ ^[Yy]$ ]]; then
    echo ""
    progress "正在启动机器人..."
    
    if [ -f "restart.sh" ]; then
        ./restart.sh
    else
        python3 -u main.py
    fi
else
    echo ""
    warning "请手动启动机器人："
    echo "  ./restart.sh"
    echo "  或"
    echo "  python3 -u main.py"
fi

echo ""
echo "🎉 感谢使用 TeleSubmit v2！"
echo ""

