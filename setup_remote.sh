#!/bin/bash

# 远程部署脚本 - 升级 Python 3.11 并安装项目依赖

echo "===== 开始远程部署 ====="

# 1. 检查当前 Python 版本
echo "[1/6] 检查当前 Python 版本..."
python --version

# 2. 删除旧的虚拟环境（如果存在）以节省空间
echo "[2/6] 清理旧虚拟环境..."
cd /root/RAG
rm -rf venv venv311

# 3. 下载 Python 3.11 安装程序
echo "[3/6] 下载 Python 3.11..."
cd /tmp
curl -O https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

# 注: 如果是 Windows，需要使用 .exe 安装程序
# 下面是 Windows 环境的安装命令（如果 PowerShell 可用）
if command -v powershell.exe &> /dev/null; then
    echo "[4/6] 使用 PowerShell 安装 Python 3.11..."
    powershell.exe -Command "Start-Process python-3.11.0-amd64.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait"
else
    echo "[4/6] 警告: PowerShell 不可用，需要手动安装 Python 3.11"
    echo "     请从以下链接下载并安装: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
fi

# 5. 验证 Python 安装
echo "[5/6] 验证 Python 版本..."
python --version
which python

# 6. 创建虚拟环境并安装依赖
echo "[6/6] 创建虚拟环境并安装依赖..."
cd /root/RAG

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（对于 bash）
source venv/Scripts/activate || . venv/bin/activate

# 升级 pip
python -m pip install --upgrade pip wheel setuptools

# 安装项目依赖
echo "安装 requirements.txt..."
pip install -r requirements.txt

echo "安装 requirements-rag.txt..."
pip install -r requirements-rag.txt

echo ""
echo "===== 部署完成 ====="
echo "虚拟环境已创建: /root/RAG/venv"
echo "依赖已安装"
echo ""
echo "下一步操作:"
echo "1. 激活虚拟环境: source /root/RAG/venv/Scripts/activate"
echo "2. 启动应用: streamlit run /root/RAG/app/main.py"
echo ""
