@echo off
REM ============================================
REM RAG 项目远程 Python 升级脚本
REM 目的: 自动下载并安装 Python 3.11
REM 使用方式: 在远程服务器（Windows）上运行此脚本
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ===== RAG 项目 Python 升级脚本 =====
echo.

REM 第一步：检查当前 Python 版本
echo [1/5] 检查当前 Python 版本...
python --version
if %errorlevel% neq 0 (
    echo 警告: Python 未在 PATH 中找到
)
echo.

REM 第二步：下载 Python 3.11
echo [2/5] 下载 Python 3.11...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
set INSTALLER=%TEMP%\python-3.11.0-amd64.exe

echo 下载地址: %PYTHON_URL%
echo 保存位置: %INSTALLER%
echo.

REM 使用 PowerShell 下载（如果可用）
powershell.exe -NoProfile -Command "Start-BitsTransfer -Source '%PYTHON_URL%' -Destination '%INSTALLER%'" 2>nul
if %errorlevel% neq 0 (
    echo PowerShell 下载失败，尝试使用 certutil...
    certutil -urlcache -split -f %PYTHON_URL% %INSTALLER%
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 无法下载 Python 3.11
        echo 请手动从以下链接下载:
        echo %PYTHON_URL%
        echo 然后将安装程序保存到: %INSTALLER%
        pause
        exit /b 1
    )
)

if not exist %INSTALLER% (
    echo [错误] 下载失败或文件不存在: %INSTALLER%
    pause
    exit /b 1
)

echo 下载完成: %INSTALLER%
echo.

REM 第三步：安装 Python 3.11
echo [3/5] 安装 Python 3.11...
echo 这可能需要几分钟，请稍候...
echo.

REM 静默安装 Python 3.11
"%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1

if %errorlevel% neq 0 (
    echo [警告] 安装过程返回非零状态: %errorlevel%
    echo 这可能表示安装未完全成功
)

REM 等待安装完成
timeout /t 5 /nobreak

echo.
echo [4/5] 验证 Python 3.11 安装...

REM 刷新环境变量（重新启动 cmd.exe）
call "%COMSPEC%" /c "python --version"

if %errorlevel% neq 0 (
    echo [错误] Python 3.11 验证失败
    echo 可能需要重启计算机后才能使用 Python 3.11
    echo.
    echo 请进行以下操作之一:
    echo 1. 重启计算机后重新运行本脚本
    echo 2. 手动验证: python --version
    echo 3. 检查 C:\Program Files\Python311\ 是否存在
    pause
    exit /b 1
)

REM 第五步：完成
echo.
echo [5/5] 安装完成！
echo.
echo ===== 下一步 =====
echo.
echo 1. 进入 RAG 项目目录:
echo    cd /root/RAG
echo.
echo 2. 激活虚拟环境:
echo    venv\Scripts\activate
echo.
echo 3. 升级 pip:
echo    python -m pip install --upgrade pip wheel setuptools
echo.
echo 4. 安装依赖:
echo    pip install -r requirements.txt
echo    pip install -r requirements-rag.txt
echo.
echo 5. 启动应用:
echo    streamlit run app/main.py --server.address 0.0.0.0
echo.
echo ===== 完成 =====
echo.

REM 清理临时文件（可选）
REM del /q "%INSTALLER%"

pause
endlocal
