@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║       使用 Python 3.11 启动 RAG 应用                  ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM 切换到批处理文件所在目录（项目根目录）
cd /d "%~dp0"
echo 📁 工作目录: %CD%
echo.

REM 检查虚拟环境
if not exist "venv311\Scripts\python.exe" (
    echo ❌ 错误: Python 3.11 虚拟环境不存在
    echo.
    echo 请运行以下命令创建环境:
    echo   py -3.11 -m venv venv311
    echo   venv311\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查 app/main.py 是否存在
if not exist "app\main.py" (
    echo ❌ 错误: 找不到 app\main.py 文件
    echo 当前目录: %CD%
    echo.
    pause
    exit /b 1
)

echo [1/4] 激活 Python 3.11 虚拟环境...
call venv311\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

echo.
echo [2/4] 验证 Python 版本...
python --version
echo.

echo [3/4] 检查 .env 配置文件...
if not exist ".env" (
    echo ⚠️ 警告: .env 文件不存在
    echo 正在从 .env.example 复制...
    copy .env.example .env
    echo.
    echo ⚠️ 请编辑 .env 文件，配置你的 DEEPSEEK_API_KEY
    echo 按任意键继续...
    pause >nul
)
echo ✅ 配置文件检查完成

echo.
echo [4/4] 启动 Streamlit 应用...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   应用将在浏览器中打开: http://localhost:8501
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python run.py

pause
