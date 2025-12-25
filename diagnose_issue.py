#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断为什么知识库界面不显示
"""

import sys
import os

# 修复 Windows 中文编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

print("=" * 70)
print("知识库界面问题诊断")
print("=" * 70)

# 1. 检查 Python 版本
print("\n【1】Python 版本")
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")

if "3.11" in sys.version:
    print("✅ 正在使用 Python 3.11")
elif "3.14" in sys.version:
    print("❌ 错误！正在使用 Python 3.14")
    print("   这可能导致 RAG 模块加载失败")
    print("\n   解决方法:")
    print("   1. 激活 venv311 环境: venv311\\Scripts\\activate")
    print("   2. 使用启动脚本: start_with_py311.bat")
else:
    print(f"⚠️ 未知版本: {sys.version}")

# 2. 检查当前目录
print(f"\n【2】当前目录")
print(f"工作目录: {os.getcwd()}")

# 3. 测试 RAG 模块导入
print("\n【3】RAG 模块导入测试")

try:
    from rag.embeddings import BGEEmbeddings
    print("✅ rag.embeddings - 导入成功")
except ImportError as e:
    print(f"❌ rag.embeddings - 导入失败: {e}")

try:
    from rag.vector_store import VectorStore
    print("✅ rag.vector_store - 导入成功")
except ImportError as e:
    print(f"❌ rag.vector_store - 导入失败: {e}")

try:
    from rag.document_processor import DocumentProcessor
    print("✅ rag.document_processor - 导入成功")
except ImportError as e:
    print(f"❌ rag.document_processor - 导入失败: {e}")

try:
    from rag.retriever import RAGRetriever
    print("✅ rag.retriever - 导入成功")
except ImportError as e:
    print(f"❌ rag.retriever - 导入失败: {e}")

# 4. 检查 app/main.py 的 RAG_AVAILABLE
print("\n【4】检查 RAG_AVAILABLE 变量")

try:
    # 模拟 main.py 的导入逻辑
    try:
        from rag.embeddings import BGEEmbeddings
        from rag.vector_store import VectorStore
        from rag.document_processor import DocumentProcessor
        from rag.retriever import RAGRetriever
        RAG_AVAILABLE = True
    except ImportError as e:
        print(f"导入失败: {e}")
        RAG_AVAILABLE = False

    print(f"RAG_AVAILABLE = {RAG_AVAILABLE}")

    if RAG_AVAILABLE:
        print("✅ RAG 模块可用，知识库界面应该显示")
    else:
        print("❌ RAG 模块不可用，知识库界面不会显示")
        print("\n可能原因:")
        print("1. 依赖包未安装")
        print("2. 使用了错误的 Python 环境")
        print("3. 依赖包版本不兼容")

except Exception as e:
    print(f"❌ 检查失败: {e}")

# 5. 检查 streamlit 是否在正确的环境
print("\n【5】检查 Streamlit")

try:
    import streamlit as st
    print(f"✅ Streamlit 版本: {st.__version__}")
    print(f"Streamlit 路径: {st.__file__}")

    # 检查 streamlit 是否在 venv311 中
    if "venv311" in st.__file__:
        print("✅ Streamlit 在 venv311 环境中")
    else:
        print("⚠️ Streamlit 不在 venv311 环境中")
        print(f"   实际路径: {st.__file__}")

except ImportError:
    print("❌ Streamlit 未安装")

# 6. 检查关键依赖
print("\n【6】检查关键依赖包")

packages = [
    "chromadb",
    "sentence_transformers",
    "transformers",
    "langchain",
    "torch"
]

for pkg in packages:
    try:
        module = __import__(pkg)
        version = getattr(module, "__version__", "未知版本")
        print(f"✅ {pkg}: {version}")
    except ImportError:
        print(f"❌ {pkg}: 未安装")

# 7. 生成建议
print("\n" + "=" * 70)
print("诊断建议")
print("=" * 70)

# 检查是否使用了正确的环境
if "3.14" in sys.version:
    print("\n🚨 主要问题: 使用了 Python 3.14 环境")
    print("\n解决方法:")
    print("1. 关闭当前应用")
    print("2. 打开命令行，执行:")
    print("   cd D:\\projects\\RAG")
    print("   venv311\\Scripts\\activate")
    print("   python run.py")
    print("\n或者直接运行:")
    print("   start_with_py311.bat")

elif "3.11" in sys.version:
    # 检查是否所有 RAG 模块都可用
    try:
        from rag.embeddings import BGEEmbeddings
        from rag.vector_store import VectorStore
        from rag.document_processor import DocumentProcessor
        from rag.retriever import RAGRetriever

        print("\n✅ Python 环境正确，所有 RAG 模块可用")
        print("\n可能的其他原因:")
        print("1. 浏览器缓存 - 尝试 Ctrl + F5 强制刷新")
        print("2. Streamlit 缓存 - 删除 .streamlit/cache 文件夹")
        print("3. 应用未重启 - 重新启动应用")
        print("\n重启应用的步骤:")
        print("1. 在运行应用的终端按 Ctrl + C 停止")
        print("2. 运行: python run.py")

    except ImportError as e:
        print(f"\n⚠️ Python 版本正确，但 RAG 模块导入失败: {e}")
        print("\n解决方法:")
        print("1. 确认在 venv311 环境中:")
        print("   venv311\\Scripts\\activate")
        print("2. 重新安装依赖:")
        print("   pip install -r requirements.txt")

else:
    print(f"\n⚠️ 未知 Python 版本: {sys.version}")
    print("\n建议使用 Python 3.11 环境:")
    print("   venv311\\Scripts\\activate")

print("\n" + "=" * 70)
