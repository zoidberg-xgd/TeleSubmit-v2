#!/bin/bash

##############################################################################
# GitHub 推送脚本 - TeleSubmit v2.1.0
# 
# 用途：一键推送项目到 GitHub
# 使用：./push_to_github.sh <your_github_username> [ssh|https]
##############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

# 检查参数
if [ $# -lt 1 ]; then
    print_error "使用方法: $0 <github_username> [ssh|https]"
    echo ""
    echo "示例："
    echo "  $0 zoidberg-xgd ssh      # 使用 SSH（推荐）"
    echo "  $0 zoidberg-xgd https    # 使用 HTTPS"
    echo ""
    exit 1
fi

GITHUB_USERNAME="$1"
METHOD="${2:-ssh}"  # 默认使用 SSH

# 验证方法
if [[ "$METHOD" != "ssh" && "$METHOD" != "https" ]]; then
    print_error "方法必须是 'ssh' 或 'https'"
    exit 1
fi

# 仓库名称
REPO_NAME="TeleSubmit"

# 构建远程仓库 URL
if [ "$METHOD" = "ssh" ]; then
    REMOTE_URL="git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    REMOTE_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

echo ""
print_info "=========================================="
print_info "  TeleSubmit v2.1.0 GitHub 推送工具"
print_info "=========================================="
echo ""

# 步骤 1: 检查 Git 状态
print_info "检查 Git 状态..."
git status

echo ""
read -p "$(echo -e ${YELLOW}是否继续推送到 GitHub? [y/N]: ${NC})" confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    print_warning "已取消推送"
    exit 0
fi

# 步骤 2: 检查是否已有远程仓库
print_info "检查远程仓库配置..."
if git remote get-url origin > /dev/null 2>&1; then
    CURRENT_REMOTE=$(git remote get-url origin)
    print_warning "检测到已配置的远程仓库: $CURRENT_REMOTE"
    
    read -p "$(echo -e ${YELLOW}是否要替换为新的远程仓库? [y/N]: ${NC})" replace
    if [[ "$replace" =~ ^[Yy]$ ]]; then
        git remote remove origin
        print_success "已删除旧的远程仓库配置"
        git remote add origin "$REMOTE_URL"
        print_success "已添加新的远程仓库: $REMOTE_URL"
    else
        print_info "保持现有远程仓库配置"
    fi
else
    print_info "添加远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
    print_success "远程仓库添加成功"
fi

echo ""

# 步骤 3: 推送主分支
print_info "推送主分支到 GitHub..."
if git push -u origin main 2>&1; then
    print_success "主分支推送成功！"
else
    print_error "主分支推送失败"
    echo ""
    print_info "可能的原因："
    echo "  1. 远程仓库不存在，请先在 GitHub 创建"
    echo "  2. 认证失败（SSH 密钥或 Token 问题）"
    echo "  3. 网络连接问题"
    echo ""
    print_info "解决方案："
    if [ "$METHOD" = "ssh" ]; then
        echo "  1. 检查 SSH 密钥: ssh -T git@github.com"
        echo "  2. 参考: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    else
        echo "  1. 使用 Personal Access Token 而不是密码"
        echo "  2. 参考: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
    fi
    exit 1
fi

echo ""

# 步骤 4: 推送标签
print_info "推送标签到 GitHub..."
if git push origin --tags 2>&1; then
    print_success "标签推送成功！"
else
    print_warning "标签推送失败（可能已存在）"
fi

echo ""

# 步骤 5: 显示结果
print_success "=========================================="
print_success "  推送完成！"
print_success "=========================================="
echo ""
print_info "仓库地址: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
print_info "下一步："
echo "  1. 访问您的仓库: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo "  2. 创建 Release: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}/releases/new"
echo "  3. 更新 README.md 中的 GitHub 链接"
echo "  4. 添加仓库 Topics（标签）"
echo ""
print_info "详细说明请查看: GITHUB_UPLOAD_GUIDE.md"
echo ""

# 询问是否在浏览器中打开
read -p "$(echo -e ${YELLOW}是否在浏览器中打开仓库页面? [y/N]: ${NC})" open_browser
if [[ "$open_browser" =~ ^[Yy]$ ]]; then
    if command -v open > /dev/null 2>&1; then
        open "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    elif command -v xdg-open > /dev/null 2>&1; then
        xdg-open "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    else
        print_warning "无法自动打开浏览器，请手动访问上述链接"
    fi
fi

print_success "完成！🎉"

