#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
直接运行此脚本启动 Streamlit 应用

Usage:
    python run.py
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

    # 将项目根目录添加到 PYTHONPATH，确保可以导入 app 和 rag 模块
    env = os.environ.copy()
    pythonpath = env.get('PYTHONPATH', '')
    if pythonpath:
        env['PYTHONPATH'] = f"{project_root}{os.pathsep}{pythonpath}"
    else:
        env['PYTHONPATH'] = project_root

    # 检查 .env 文件是否存在
    env_file = os.path.join(project_root, ".env")
    if not os.path.exists(env_file):
        print("❌ 错误: .env 文件不存在！")
        print("请复制 .env.example 为 .env 并配置 DEEPSEEK_API_KEY")
        print(f"  cp {os.path.join(project_root, '.env.example')} {env_file}")
        sys.exit(1)

    print("🚀 启动 Streamlit 应用...")
    print(f"📁 项目目录: {project_root}")
    print(f"🐍 PYTHONPATH: {env['PYTHONPATH']}")

    # 启动 Streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run",
             os.path.join(project_root, "app", "main.py")],
            cwd=project_root,
            env=env
        )
    except KeyboardInterrupt:
        print("\n⚠️ 应用已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
