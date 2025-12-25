#!/bin/bash

# RAG 知识库功能 - 自动安装脚本（macOS/Linux）

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║         RAG 知识库功能 - 自动安装脚本                  ║"
echo "║                                                        ║"
echo "║  此脚本将为您安装 RAG 所需的所有依赖                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo "[1/5] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python 3${NC}"
    echo ""
    echo "请先安装 Python 3.9+，然后重新运行此脚本"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get install python3 python3-pip python3-venv"
    echo ""
    echo "macOS (使用 Homebrew):"
    echo "  brew install python3"
    exit 1
fi
python3 --version
echo -e "${GREEN}✅ Python 环境正常${NC}"

# 检查虚拟环境
echo ""
echo "[2/5] 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo ""
echo "[3/5] 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 虚拟环境激活失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 虚拟环境已激活${NC}"

# 升级 pip
echo ""
echo "[4/5] 升级 pip..."
python -m pip install --upgrade pip -q
echo -e "${GREEN}✅ pip 升级完成${NC}"

# 安装依赖
echo ""
echo "[5/5] 安装 RAG 依赖（这可能需要 5-10 分钟）..."
echo ""
python -m pip install -r requirements-rag.txt

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  某些依赖安装可能失败，但不影响基础功能${NC}"
    echo ""
    echo "常见原因："
    echo "- 网络连接不稳定（模型下载需要 ~400MB）"
    echo "- 缺少 C/C++ 编译器"
    echo ""
    echo "解决方案："
    echo "macOS: brew install llvm"
    echo "Ubuntu/Debian: sudo apt-get install build-essential"
    echo ""
else
    echo -e "${GREEN}✅ 所有依赖安装完成${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                   ✅ 安装完成！                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "接下来可以运行："
echo "  python run.py"
echo ""
echo "或者直接访问："
echo "  http://localhost:8501"
echo ""
echo "详细信息请查看: KNOWLEDGE_BASE_SETUP.md"
echo ""

# 提示虚拟环境
echo -e "${YELLOW}💡 提示:${NC} 如果要停用虚拟环境，可以运行: deactivate"
echo ""
