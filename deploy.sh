#!/bin/bash
# TeleSubmit v2 Docker 部署脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装！"
        log_info "请访问 https://docs.docker.com/get-docker/ 安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装！"
        log_info "请访问 https://docs.docker.com/compose/install/ 安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 检查配置文件
check_config() {
    if [ ! -f "config.ini" ]; then
        log_warning "未找到 config.ini，从模板创建..."
        if [ -f "config.ini.example" ]; then
            cp config.ini.example config.ini
            log_info "已创建 config.ini，请编辑配置文件填入必要信息："
            log_info "  - TOKEN: 从 @BotFather 获取"
            log_info "  - CHANNEL_ID: 频道 ID"
            log_info "  - OWNER_ID: 您的 Telegram User ID"
            log_warning "配置完成后请重新运行此脚本"
            exit 0
        else
            log_error "未找到 config.ini.example 模板文件！"
            exit 1
        fi
    fi
    
    log_success "配置文件检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p data logs backups data/search_index
    log_success "目录创建完成"
}

# 停止现有容器
stop_containers() {
    log_info "停止现有容器..."
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        log_success "容器已停止"
    else
        log_info "无运行中的容器"
    fi
}

# 构建和启动
build_and_start() {
    local rebuild=$1
    
    if [ "$rebuild" = "--rebuild" ]; then
        log_info "重新构建 Docker 镜像..."
        docker-compose build --no-cache
    else
        log_info "构建 Docker 镜像..."
        docker-compose build
    fi
    
    log_info "启动容器..."
    docker-compose up -d
    
    log_success "容器启动成功！"
}

# 查看日志
show_logs() {
    log_info "查看运行日志（Ctrl+C 退出）..."
    sleep 2
    docker-compose logs -f
}

# 主函数
main() {
    echo ""
    log_info "=== TeleSubmit v2 Docker 部署 ==="
    echo ""
    
    # 检查 Docker
    check_docker
    
    # 检查配置
    check_config
    
    # 创建目录
    create_directories
    
    # 停止现有容器
    stop_containers
    
    # 构建和启动
    build_and_start "$1"
    
    echo ""
    log_success "部署完成！"
    echo ""
    log_info "管理命令："
    log_info "  查看日志: docker-compose logs -f"
    log_info "  停止容器: docker-compose down"
    log_info "  重启容器: docker-compose restart"
    log_info "  查看状态: docker-compose ps"
    echo ""
    
    # 询问是否查看日志
    read -p "是否查看运行日志？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# 运行主函数
main "$@"

