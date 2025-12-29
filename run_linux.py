#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux/虚拟机启动脚本 - 使用虚拟环境
直接运行此脚本启动 Streamlit 应用

Usage:
    python run_linux.py
    或
    source venv/bin/activate && python run_linux.py
"""

import subprocess
import sys
import os

def main():
    """启动 Streamlit 应用"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))

    print("🚀 启动 Streamlit 应用...")
    print(f"📁 项目目录: {project_root}")
    print(f"🐍 Python: {sys.executable}")
    print(f"🐍 Python 版本: {sys.version}")

    # 将项目根目录添加到 PYTHONPATH
    env = os.environ.copy()
    pythonpath = env.get('PYTHONPATH', '')
    if pythonpath:
        env['PYTHONPATH'] = f"{project_root}:{pythonpath}"
    else:
        env['PYTHONPATH'] = project_root

    print(f"📝 PYTHONPATH: {env['PYTHONPATH']}")

    # 检查 .env 文件
    env_file = os.path.join(project_root, ".env")
    if not os.path.exists(env_file):
        print("❌ 错误: .env 文件不存在！")
        print("请执行: cp .env.example .env")
        sys.exit(1)

    # 验证依赖
    print("\n📦 验证依赖...")
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit 未找到: {e}")
        sys.exit(1)

    try:
        import chromadb
        print(f"✅ chromadb {chromadb.__version__}")
    except ImportError as e:
        print(f"⚠️ chromadb 未找到，将以纯对话模式运行: {e}")

    try:
        from rag.embeddings import BGEEmbeddings
        print(f"✅ RAG 模块可用")
    except ImportError as e:
        print(f"⚠️ RAG 模块不可用: {e}")

    # 启动 Streamlit
    print("\n🌐 启动 Streamlit 服务器...\n")

    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(project_root, "app", "main.py"),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ]

    try:
        subprocess.run(streamlit_cmd, cwd=project_root, env=env)
    except KeyboardInterrupt:
        print("\n⚠️ 应用已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
