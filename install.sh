#!/bin/bash

# TeleSubmit v2 一键安装脚本
# 支持多种部署方式：Docker、Systemd、直接运行

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
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

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           🤖 TeleSubmit v2 一键安装脚本                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

# 检查系统类型
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            VER=$VERSION_ID
        fi
        print_info "检测到系统: $OS $VER"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "检测到系统: macOS"
    else
        print_error "不支持的系统: $OSTYPE"
        exit 1
    fi
}

# 检查是否以 root 运行
check_root() {
    if [ "$EUID" -eq 0 ] && [ "$INSTALL_METHOD" = "systemd" ]; then
        print_info "以 root 权限运行（Systemd 安装需要）"
        IS_ROOT=true
    else
        IS_ROOT=false
    fi
}

# 检查 Docker
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        COMPOSE_VERSION=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        print_success "Docker 已安装: $DOCKER_VERSION"
        print_success "Docker Compose 已安装: $COMPOSE_VERSION"
        HAS_DOCKER=true
    else
        print_warning "Docker 未安装"
        HAS_DOCKER=false
    fi
}

# 检查 Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+\.\d+')
        print_success "Python 已安装: $PYTHON_VERSION"
        
        # 检查版本是否满足要求
        required_version="3.10"
        if [ "$(printf '%s\n' "$required_version" "$PYTHON_VERSION" | sort -V | head -n1)" = "$required_version" ]; then
            HAS_PYTHON=true
        else
            print_warning "Python 版本过低，推荐 3.10+"
            HAS_PYTHON=false
        fi
    else
        print_warning "Python 3 未安装"
        HAS_PYTHON=false
    fi
}

# 检查 systemd
check_systemd() {
    if command -v systemctl &> /dev/null; then
        print_success "Systemd 已安装"
        HAS_SYSTEMD=true
    else
        print_warning "Systemd 未安装（macOS 不支持）"
        HAS_SYSTEMD=false
    fi
}

# 安装 Docker
install_docker() {
    print_info "开始安装 Docker..."
    
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        # 安装 Docker (Ubuntu/Debian)
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg lsb-release
        
        # 添加 Docker 官方 GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 设置仓库
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装 Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # 安装 docker-compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # 启动 Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 添加当前用户到 docker 组
        sudo usermod -aG docker $USER
        
        print_success "Docker 安装完成"
        print_warning "请注销并重新登录以使 Docker 组权限生效"
        
    elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
        # 安装 Docker (CentOS/RHEL)
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        
        # 安装 docker-compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
        
        print_success "Docker 安装完成"
        
    elif [[ "$OS" == "macos" ]]; then
        print_warning "请手动安装 Docker Desktop for Mac:"
        print_info "https://docs.docker.com/desktop/mac/install/"
        exit 1
    else
        print_error "不支持的系统: $OS"
        exit 1
    fi
}

# 安装 Python 依赖
install_python() {
    print_info "开始安装 Python 和依赖..."
    
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
        sudo yum install -y python3 python3-pip
    elif [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            print_error "请先安装 Homebrew: https://brew.sh"
            exit 1
        fi
        brew install python@3.11
    fi
    
    print_success "Python 安装完成"
}

# 选择安装方法
choose_install_method() {
    print_info "请选择部署方式:"
    echo ""
    
    methods=()
    
    if [ "$HAS_DOCKER" = true ]; then
        echo "  1. Docker Compose（推荐，容器化部署）"
        methods+=("docker")
    fi
    
    if [ "$HAS_SYSTEMD" = true ] && [ "$HAS_PYTHON" = true ]; then
        echo "  2. Systemd 服务（生产环境，开机自启）"
        methods+=("systemd")
    fi
    
    if [ "$HAS_PYTHON" = true ]; then
        echo "  3. 直接运行（开发测试）"
        methods+=("direct")
    fi
    
    echo "  0. 安装依赖后退出"
    echo ""
    
    read -p "请选择 [1-3/0]: " choice
    
    case $choice in
        1)
            if [ "$HAS_DOCKER" = true ]; then
                INSTALL_METHOD="docker"
            else
                print_error "Docker 未安装"
                read -p "是否现在安装 Docker? (y/N): " install_docker_choice
                if [[ "$install_docker_choice" =~ ^[Yy]$ ]]; then
                    install_docker
                    INSTALL_METHOD="docker"
                else
                    exit 1
                fi
            fi
            ;;
        2)
            if [ "$HAS_SYSTEMD" = true ] && [ "$HAS_PYTHON" = true ]; then
                INSTALL_METHOD="systemd"
            else
                print_error "Systemd 或 Python 未安装"
                exit 1
            fi
            ;;
        3)
            if [ "$HAS_PYTHON" = true ]; then
                INSTALL_METHOD="direct"
            else
                print_error "Python 未安装"
                read -p "是否现在安装 Python? (y/N): " install_python_choice
                if [[ "$install_python_choice" =~ ^[Yy]$ ]]; then
                    install_python
                    INSTALL_METHOD="direct"
                else
                    exit 1
                fi
            fi
            ;;
        0)
            print_info "仅安装依赖，不进行部署"
            exit 0
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac
}

# 配置向导
run_setup_wizard() {
    if [ ! -f "config.ini" ]; then
        print_info "运行配置向导..."
        
        if [ -f "setup_wizard.py" ]; then
            python3 setup_wizard.py
            
            if [ $? -ne 0 ] || [ ! -f "config.ini" ]; then
                print_error "配置未完成"
                exit 1
            fi
        else
            print_warning "未找到配置向导，使用示例配置"
            if [ -f "config.ini.example" ]; then
                cp config.ini.example config.ini
                print_warning "请编辑 config.ini 填入真实配置"
                nano config.ini || vi config.ini
            fi
        fi
    else
        print_success "找到现有配置文件"
    fi
}

# Docker 部署
deploy_docker() {
    print_info "使用 Docker Compose 部署..."
    
    # 创建必要目录
    mkdir -p data logs data/search_index
    
    # 运行部署脚本
    if [ -f "deploy.sh" ]; then
        chmod +x deploy.sh
        ./deploy.sh
    else
        print_error "未找到 deploy.sh 脚本"
        exit 1
    fi
}

# Systemd 部署
deploy_systemd() {
    print_info "使用 Systemd 部署..."
    
    # 获取当前目录
    INSTALL_DIR=$(pwd)
    
    # 创建必要目录
    mkdir -p data logs data/search_index
    
    # 安装 Python 依赖
    print_info "安装 Python 依赖..."
    pip3 install -r requirements.txt
    
    # 创建 systemd 服务文件
    print_info "创建 Systemd 服务..."
    
    SERVICE_FILE="/etc/systemd/system/telesubmit.service"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=TeleSubmit v2 - Telegram Submission Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 -u $INSTALL_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/bot.log
StandardError=append:$INSTALL_DIR/logs/error.log

# 环境变量
Environment="PYTHONUNBUFFERED=1"

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    sudo systemctl daemon-reload
    
    # 启用并启动服务
    sudo systemctl enable telesubmit
    sudo systemctl start telesubmit
    
    print_success "Systemd 服务已创建并启动"
    print_info "使用以下命令管理服务:"
    echo "  sudo systemctl status telesubmit  # 查看状态"
    echo "  sudo systemctl restart telesubmit # 重启服务"
    echo "  sudo systemctl stop telesubmit    # 停止服务"
    echo "  sudo journalctl -u telesubmit -f  # 查看日志"
}

# 直接运行
deploy_direct() {
    print_info "直接运行模式..."
    
    # 创建必要目录
    mkdir -p data logs data/search_index
    
    # 安装依赖
    print_info "安装 Python 依赖..."
    pip3 install -r requirements.txt
    
    # 运行启动脚本
    if [ -f "start.sh" ]; then
        chmod +x start.sh
        ./start.sh
    else
        print_error "未找到 start.sh 脚本"
        exit 1
    fi
}

# 主函数
main() {
    print_header
    
    # 检测系统
    print_info "步骤 1/5: 系统检测"
    detect_os
    echo ""
    
    # 检查依赖
    print_info "步骤 2/5: 环境检查"
    check_docker
    check_python
    check_systemd
    echo ""
    
    # 选择安装方法
    print_info "步骤 3/5: 选择部署方式"
    choose_install_method
    echo ""
    
    # 配置向导
    print_info "步骤 4/5: 配置"
    run_setup_wizard
    echo ""
    
    # 部署
    print_info "步骤 5/5: 部署"
    case $INSTALL_METHOD in
        docker)
            deploy_docker
            ;;
        systemd)
            deploy_systemd
            ;;
        direct)
            deploy_direct
            ;;
        *)
            print_error "未知的安装方法: $INSTALL_METHOD"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "🎉 安装完成！"
    echo ""
}

# 运行主函数
main "$@"

