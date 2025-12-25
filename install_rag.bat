@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║         RAG 知识库功能 - 自动安装脚本                  ║
echo ║                                                        ║
echo ║  此脚本将为您安装 RAG 所需的所有依赖                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo.
    echo 请先安装 Python 3.9+，然后重新运行此脚本
    pause
    exit /b 1
)
echo ✅ Python 环境正常

REM 检查虚拟环境
echo.
echo [2/5] 检查虚拟环境...
if not exist "venv" (
    echo ⚠️  虚拟环境不存在，正在创建...
    python -m venv venv
    echo ✅ 虚拟环境创建完成
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 升级 pip
echo.
echo [4/5] 升级 pip...
python -m pip install --upgrade pip -q
echo ✅ pip 升级完成

REM 安装依赖
echo.
echo [5/5] 安装 RAG 依赖（这可能需要 5-10 分钟）...
echo.
python -m pip install -r requirements-rag.txt

if errorlevel 1 (
    echo.
    echo ⚠️  某些依赖安装可能失败，但不影响基础功能
    echo.
    echo 常见原因：
    echo - 网络连接不稳定（模型下载需要 ~400MB）
    echo - 缺少 C/C++ 编译器（需要重新运行 pip install numpy --upgrade）
    echo.
) else (
    echo ✅ 所有依赖安装完成
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                   ✅ 安装完成！                         ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 接下来可以运行：
echo   python run.py
echo.
echo 或者直接打开：
echo   http://localhost:8501
echo.
echo 详细信息请查看: KNOWLEDGE_BASE_SETUP.md
echo.
pause
