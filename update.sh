#!/bin/bash

# TeleSubmit v2 更新脚本
# 用于从 Git 仓库拉取最新代码并重新部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🔄 TeleSubmit v2 更新脚本                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    print_error "当前目录不是 Git 仓库"
    print_info "请从 GitHub 克隆项目: git clone https://github.com/zoidberg-xgd/TeleSubmit-v2.git"
    exit 1
fi

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    print_warning "检测到未提交的更改"
    echo ""
    git status --short
    echo ""
    read -p "是否暂存这些更改并继续更新？(y/N): " stash_changes
    
    if [[ "$stash_changes" =~ ^[Yy]$ ]]; then
        print_info "暂存更改..."
        git stash push -m "Auto-stash before update $(date +%Y%m%d_%H%M%S)"
        STASHED=true
    else
        print_error "请先提交或暂存更改"
        exit 1
    fi
fi

# 创建备份
print_info "创建配置和数据备份..."
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"

tar -czf "$BACKUP_FILE" \
    config.ini \
    data/ \
    logs/ \
    2>/dev/null || true

print_success "备份已创建: $BACKUP_FILE"
echo ""

# 获取当前版本
if [ -f "CHANGELOG.md" ]; then
    CURRENT_VERSION=$(grep -m 1 "## \[" CHANGELOG.md | grep -oP '\[\K[^\]]+' || echo "unknown")
    print_info "当前版本: $CURRENT_VERSION"
fi

# 拉取最新代码
print_info "拉取最新代码..."
git fetch origin

# 检查是否有更新
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    print_success "已是最新版本，无需更新"
    
    # 恢复暂存的更改
    if [ "$STASHED" = true ]; then
        print_info "恢复暂存的更改..."
        git stash pop
    fi
    
    exit 0
fi

print_info "发现新版本，开始更新..."
echo ""

# 显示更新内容
print_info "更新内容预览:"
git log --oneline HEAD..origin/main | head -10
echo ""

read -p "是否继续更新？(Y/n): " continue_update
continue_update=${continue_update:-y}

if [[ ! "$continue_update" =~ ^[Yy]$ ]]; then
    print_info "已取消更新"
    
    if [ "$STASHED" = true ]; then
        git stash pop
    fi
    
    exit 0
fi

# 执行更新
print_info "执行 git pull..."
git pull origin main

# 获取新版本
if [ -f "CHANGELOG.md" ]; then
    NEW_VERSION=$(grep -m 1 "## \[" CHANGELOG.md | grep -oP '\[\K[^\]]+' || echo "unknown")
    print_success "已更新到版本: $NEW_VERSION"
fi

echo ""

# 检测部署方式并重新部署
print_info "检测部署方式..."

DEPLOY_METHOD=""

# 检查 Docker
if docker ps 2>/dev/null | grep -q "telesubmit"; then
    DEPLOY_METHOD="docker"
    print_info "检测到 Docker 部署"
fi

# 检查 Systemd
if systemctl is-active --quiet telesubmit 2>/dev/null; then
    DEPLOY_METHOD="systemd"
    print_info "检测到 Systemd 部署"
fi

if [ -z "$DEPLOY_METHOD" ]; then
    print_warning "未检测到运行中的服务"
    echo ""
    echo "请选择重新部署方式："
    echo "  1. Docker Compose"
    echo "  2. Systemd"
    echo "  3. 直接运行"
    echo "  0. 仅更新代码，不重新部署"
    echo ""
    read -p "请选择 [0-3]: " deploy_choice
    
    case $deploy_choice in
        1) DEPLOY_METHOD="docker" ;;
        2) DEPLOY_METHOD="systemd" ;;
        3) DEPLOY_METHOD="direct" ;;
        0) 
            print_success "代码更新完成"
            if [ "$STASHED" = true ]; then
                git stash pop
            fi
            exit 0
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac
fi

echo ""
print_info "重新部署..."

case $DEPLOY_METHOD in
    docker)
        print_info "停止旧容器..."
        docker-compose down
        
        print_info "重新构建镜像..."
        docker-compose build --no-cache
        
        print_info "启动新容器..."
        docker-compose up -d
        
        sleep 3
        
        if docker-compose ps | grep -q "Up"; then
            print_success "Docker 容器已更新并启动"
            print_info "查看日志: docker-compose logs -f"
        else
            print_error "容器启动失败"
            print_info "查看错误: docker-compose logs"
            exit 1
        fi
        ;;
        
    systemd)
        print_info "更新 Python 依赖..."
        pip3 install -r requirements.txt --upgrade
        
        print_info "重启 Systemd 服务..."
        sudo systemctl restart telesubmit
        
        sleep 2
        
        if systemctl is-active --quiet telesubmit; then
            print_success "Systemd 服务已重启"
            print_info "查看状态: sudo systemctl status telesubmit"
            print_info "查看日志: sudo journalctl -u telesubmit -f"
        else
            print_error "服务启动失败"
            print_info "查看错误: sudo journalctl -u telesubmit -n 50"
            exit 1
        fi
        ;;
        
    direct)
        print_info "更新 Python 依赖..."
        pip3 install -r requirements.txt --upgrade
        
        print_success "依赖已更新"
        print_warning "请手动重启应用程序"
        ;;
esac

# 恢复暂存的更改
if [ "$STASHED" = true ]; then
    print_info "恢复暂存的更改..."
    git stash pop || print_warning "无法自动恢复更改，请手动处理: git stash list"
fi

echo ""
print_success "🎉 更新完成！"
echo ""

# 显示更新日志
if [ -f "CHANGELOG.md" ]; then
    print_info "更新日志（最近的更改）:"
    echo ""
    head -30 CHANGELOG.md
fi

echo ""
print_info "备份文件位置: $BACKUP_FILE"
echo ""

