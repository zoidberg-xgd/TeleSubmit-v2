#!/bin/bash
# 运行所有测试并生成报告的脚本

set -e

echo "=================================="
echo "  TeleSubmit-v2 测试套件"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo -e "${BLUE}📋 检查 Python 版本...${NC}"
python3 --version
echo ""

# 检查是否安装了 pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest 未安装${NC}"
    echo -e "${YELLOW}📦 正在安装测试依赖...${NC}"
    pip3 install -r requirements.txt
    echo ""
fi

# 清理旧的测试结果
echo -e "${BLUE}🧹 清理旧的测试结果...${NC}"
rm -rf .pytest_cache htmlcov .coverage *.xml
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 运行测试
echo -e "${BLUE}🧪 运行测试套件...${NC}"
echo ""

# 1. 单元测试
echo -e "${YELLOW}▸ 运行单元测试...${NC}"
if pytest -m unit -v --tb=short; then
    echo -e "${GREEN}✓ 单元测试通过${NC}"
else
    echo -e "${RED}✗ 单元测试失败${NC}"
    exit 1
fi
echo ""

# 2. 集成测试
echo -e "${YELLOW}▸ 运行集成测试...${NC}"
if pytest -m integration -v --tb=short; then
    echo -e "${GREEN}✓ 集成测试通过${NC}"
else
    echo -e "${RED}✗ 集成测试失败${NC}"
    exit 1
fi
echo ""

# 3. 生成覆盖率报告
echo -e "${YELLOW}▸ 生成代码覆盖率报告...${NC}"
pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
echo ""

# 显示覆盖率统计
if [ -f .coverage ]; then
    echo -e "${GREEN}✓ 覆盖率报告已生成${NC}"
    echo -e "  • HTML 报告: ${BLUE}htmlcov/index.html${NC}"
    echo -e "  • XML 报告: ${BLUE}coverage.xml${NC}"
else
    echo -e "${RED}✗ 覆盖率报告生成失败${NC}"
fi
echo ""

# 4. 生成 JUnit XML 报告
echo -e "${YELLOW}▸ 生成测试报告...${NC}"
pytest --junitxml=report.xml
if [ -f report.xml ]; then
    echo -e "${GREEN}✓ 测试报告已生成: ${BLUE}report.xml${NC}"
else
    echo -e "${RED}✗ 测试报告生成失败${NC}"
fi
echo ""

# 测试统计
echo "=================================="
echo -e "${GREEN}✅ 所有测试完成！${NC}"
echo "=================================="
echo ""

# 提示打开报告
echo -e "${BLUE}💡 提示:${NC}"
echo "  查看 HTML 覆盖率报告:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "    open htmlcov/index.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "    xdg-open htmlcov/index.html"
else
    echo "    浏览器打开 htmlcov/index.html"
fi
echo ""

# 询问是否自动打开报告
read -p "是否现在打开覆盖率报告? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open htmlcov/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open htmlcov/index.html
    fi
fi

exit 0
