@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     RAG 依赖安装 - 简易版（使用预编译轮）            ║
echo ║                                                        ║
echo ║   如果 pip install 失败，此脚本会自动下载预编译的    ║
echo ║   依赖，避免编译问题                                  ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python
    pause
    exit /b 1
)
echo ✅ Python 已安装

REM 激活虚拟环境
echo.
echo [2/3] 激活虚拟环境...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo [3/3] 安装依赖...
echo.

REM 首先升级 pip
python -m pip install --upgrade pip --no-cache-dir

REM 使用预编译轮安装 numpy（避免编译）
echo 安装 numpy（使用预编译轮）...
python -m pip install numpy --only-binary :all: --no-cache-dir

REM 安装其他依赖
echo 安装其他依赖...
python -m pip install ^
    streamlit==1.28.1 ^
    httpx==0.25.0 ^
    requests==2.31.0 ^
    python-dotenv==1.0.0 ^
    pydantic==2.4.2 ^
    loguru==0.7.2 ^
    sentence-transformers ^
    transformers ^
    chromadb ^
    langchain ^
    langchain-community ^
    PyPDF2 ^
    --no-cache-dir

if errorlevel 1 (
    echo.
    echo ⚠️  某些依赖安装可能失败
    echo.
    echo 尝试以下解决方案：
    echo 1. 确保网络连接正常
    echo 2. 使用代理或科学上网（下载模型需要）
    echo 3. 尝试降低 pip 版本： pip install --upgrade setuptools
    echo.
) else (
    echo ✅ 依赖安装完成
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                 ✅ 安装完成！                          ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 现在可以运行：
echo   python run.py
echo.
pause
