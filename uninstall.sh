#!/bin/bash

# TeleSubmit v2 卸载脚本

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
echo "║           🗑️  TeleSubmit v2 卸载脚本                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_warning "此操作将卸载 TeleSubmit v2"
echo ""
echo "将执行以下操作："
echo "  • 停止运行中的服务/容器"
echo "  • 删除 Systemd 服务（如果存在）"
echo "  • 删除 Docker 容器和镜像（如果存在）"
echo ""
read -p "是否继续？(yes/NO): " confirm

if [[ ! "$confirm" =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "已取消卸载"
    exit 0
fi

echo ""

# 检查并停止 Systemd 服务
if systemctl is-active --quiet telesubmit 2>/dev/null; then
    print_info "停止 Systemd 服务..."
    sudo systemctl stop telesubmit
    sudo systemctl disable telesubmit
    print_success "Systemd 服务已停止"
fi

if [ -f "/etc/systemd/system/telesubmit.service" ]; then
    print_info "删除 Systemd 服务文件..."
    sudo rm /etc/systemd/system/telesubmit.service
    sudo systemctl daemon-reload
    print_success "Systemd 服务已删除"
fi

# 检查并停止 Docker 容器
if command -v docker-compose &> /dev/null; then
    if docker ps -a | grep -q "telesubmit"; then
        print_info "停止 Docker 容器..."
        docker-compose down -v 2>/dev/null || true
        print_success "Docker 容器已停止"
    fi
    
    # 删除镜像
    if docker images | grep -q "telesubmit"; then
        print_warning "是否删除 Docker 镜像？"
        read -p "删除镜像 (y/N): " remove_image
        if [[ "$remove_image" =~ ^[Yy]$ ]]; then
            docker rmi telesubmit-v2_bot 2>/dev/null || true
            docker rmi telesubmit-v2 2>/dev/null || true
            print_success "Docker 镜像已删除"
        fi
    fi
fi

# 询问是否删除数据
echo ""
print_warning "是否删除数据文件？"
echo "  • config.ini (配置文件)"
echo "  • data/ (数据库和搜索索引)"
echo "  • logs/ (日志文件)"
echo ""
read -p "删除数据 (yes/NO): " remove_data

if [[ "$remove_data" =~ ^[Yy][Ee][Ss]$ ]]; then
    # 备份数据
    print_info "创建数据备份..."
    BACKUP_FILE="telesubmit_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$BACKUP_FILE" config.ini data/ logs/ 2>/dev/null || true
    print_success "数据已备份到: $BACKUP_FILE"
    
    # 删除数据
    print_info "删除数据文件..."
    rm -rf data/ logs/ config.ini user_sessions.db 2>/dev/null || true
    print_success "数据文件已删除"
else
    print_info "保留数据文件"
fi

echo ""
print_success "🎉 卸载完成！"
echo ""

if [[ "$remove_data" =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "数据备份位置: $BACKUP_FILE"
fi

print_info "如需重新安装，运行: ./install.sh"
echo ""

