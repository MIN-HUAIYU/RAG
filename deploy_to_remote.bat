@echo off
REM 远程部署脚本 - 升级 Python 并安装依赖

setlocal enabledelayedexpansion

REM 连接到远程服务器
ssh root@139.224.207.84 << 'EOF'

echo ===== 开始远程部署 =====

REM 检查当前 Python 版本
echo [1/5] 检查 Python 版本...
python --version

REM 下载 Python 3.11 安装程序
echo [2/5] 下载 Python 3.11...
cd %TEMP%
powershell -Command "Start-BitsTransfer -Source 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -Destination 'python-3.11.0-amd64.exe'"

REM 安装 Python 3.11
echo [3/5] 安装 Python 3.11...
python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

REM 更新 PATH
set PATH=C:\Python311;C:\Python311\Scripts;!PATH!

REM 验证安装
echo [4/5] 验证 Python 安装...
python --version

REM 进入项目目录
echo [5/5] 进入项目目录并安装依赖...
cd /root/RAG

REM 创建虚拟环境
python -m venv venv

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt
pip install -r requirements-rag.txt

echo ===== 部署完成 =====
echo 虚拟环境已创建在: /root/RAG/venv
echo 依赖已安装
echo 下一步: 启动应用
echo 命令: streamlit run app/main.py

EOF

endlocal
