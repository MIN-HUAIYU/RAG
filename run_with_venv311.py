#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本 - 强制使用 Python 3.11 虚拟环境
确保使用正确的 Python 环境启动应用

Usage:
    python run_with_venv311.py
"""

import subprocess
import sys
import os
import io

# 修复 Windows 中文编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    """启动 Streamlit 应用"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))

    # venv311 Python 可执行文件路径
    venv_python = os.path.join(project_root, "venv311", "Scripts", "python.exe")

    # 检查 venv311 是否存在
    if not os.path.exists(venv_python):
        print("❌ 错误: venv311 虚拟环境不存在！")
        print(f"   路径: {venv_python}")
        print("\n请先创建虚拟环境:")
        print("   py -3.11 -m venv venv311")
        print("   venv311\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    # 检查 .env 文件
    env_file = os.path.join(project_root, ".env")
    if not os.path.exists(env_file):
        print("❌ 错误: .env 文件不存在！")
        print("请复制 .env.example 为 .env 并配置 DEEPSEEK_API_KEY")
        sys.exit(1)

    print("=" * 70)
    print("🚀 启动 Streamlit 应用（强制使用 Python 3.11）")
    print("=" * 70)
    print(f"📁 项目目录: {project_root}")
    print(f"🐍 Python 路径: {venv_python}")

    # 验证 Python 版本
    try:
        version_check = subprocess.run(
            [venv_python, "--version"],
            capture_output=True,
            text=True
        )
        print(f"✅ Python 版本: {version_check.stdout.strip()}")

        if "3.11" not in version_check.stdout:
            print("⚠️ 警告: 不是 Python 3.11 版本")

    except Exception as e:
        print(f"⚠️ 无法验证 Python 版本: {e}")

    print("\n正在启动 Streamlit...")
    print("浏览器将自动打开: http://localhost:8501")
    print("按 Ctrl + C 停止应用\n")
    print("=" * 70)

    # 启动 Streamlit
    try:
        subprocess.run(
            [venv_python, "-m", "streamlit", "run",
             os.path.join(project_root, "app", "main.py")],
            cwd=project_root
        )
    except KeyboardInterrupt:
        print("\n⚠️ 应用已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
