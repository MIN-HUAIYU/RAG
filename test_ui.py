#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 测试脚本 - 验证知识库界面是否正常显示
"""

import sys
import os

# 修复 Windows 中文编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def test_rag_imports():
    """测试 RAG 模块导入"""
    print("=" * 60)
    print("测试 1: RAG 模块导入")
    print("=" * 60)

    try:
        from rag.embeddings import BGEEmbeddings
        print("✅ BGEEmbeddings 导入成功")

        from rag.vector_store import VectorStore
        print("✅ VectorStore 导入成功")

        from rag.document_processor import DocumentProcessor
        print("✅ DocumentProcessor 导入成功")

        from rag.retriever import RAGRetriever
        print("✅ RAGRetriever 导入成功")

        print("\n✅ 所有 RAG 模块导入成功！")
        return True

    except ImportError as e:
        print(f"\n❌ RAG 模块导入失败: {e}")
        print("\n这意味着知识库界面不会显示！")
        print("请检查依赖是否安装: pip install -r requirements.txt")
        return False

def test_config():
    """测试配置"""
    print("\n" + "=" * 60)
    print("测试 2: 应用配置")
    print("=" * 60)

    try:
        from app.config import Config
        Config.validate()
        print(f"✅ API Key: {Config.DEEPSEEK_API_KEY[:10]}***")
        print(f"✅ Model: {Config.DEEPSEEK_MODEL}")
        print(f"✅ API URL: {Config.DEEPSEEK_API_URL}")
        return True

    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def test_streamlit_imports():
    """测试 Streamlit 相关导入"""
    print("\n" + "=" * 60)
    print("测试 3: Streamlit 组件")
    print("=" * 60)

    try:
        import streamlit as st
        print(f"✅ Streamlit 版本: {st.__version__}")

        from app.components import ChatInterface
        print("✅ ChatInterface 导入成功")

        from app.services import DeepSeekService
        print("✅ DeepSeekService 导入成功")

        return True

    except Exception as e:
        print(f"❌ Streamlit 组件导入失败: {e}")
        return False

def check_ui_logic():
    """检查 UI 逻辑"""
    print("\n" + "=" * 60)
    print("测试 4: UI 逻辑检查")
    print("=" * 60)

    # 模拟 main.py 的导入逻辑
    try:
        from rag.embeddings import BGEEmbeddings
        from rag.vector_store import VectorStore
        from rag.document_processor import DocumentProcessor
        from rag.retriever import RAGRetriever
        RAG_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ RAG modules not available: {e}")
        RAG_AVAILABLE = False

    print(f"\nRAG_AVAILABLE = {RAG_AVAILABLE}")

    if RAG_AVAILABLE:
        print("✅ 知识库界面应该会显示！")
        print("\n知识库界面位置:")
        print("  - 主页面中部有 '📚 知识库管理' 标题")
        print("  - 包含文件上传区域")
        print("  - 包含 '🚀 立即上传' 按钮")
        print("  - 右侧显示知识库统计")
    else:
        print("❌ 知识库界面不会显示！")
        print("\n原因: RAG 模块未成功导入")
        print("解决方法: 确保所有依赖已安装")

    return RAG_AVAILABLE

def check_data_directories():
    """检查数据目录"""
    print("\n" + "=" * 60)
    print("测试 5: 数据目录检查")
    print("=" * 60)

    directories = [
        "data",
        "data/documents",
        "data/chroma_db",
        "logs"
    ]

    for dir_path in directories:
        full_path = os.path.join(os.getcwd(), dir_path)
        if os.path.exists(full_path):
            print(f"✅ {dir_path}/ 存在")
        else:
            print(f"⚠️ {dir_path}/ 不存在 (将自动创建)")
            try:
                os.makedirs(full_path, exist_ok=True)
                print(f"   ✅ 已创建 {dir_path}/")
            except Exception as e:
                print(f"   ❌ 创建失败: {e}")

def main():
    """主函数"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║           RAG 应用 UI 测试                             ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    results = []

    # 运行所有测试
    results.append(("RAG 模块导入", test_rag_imports()))
    results.append(("应用配置", test_config()))
    results.append(("Streamlit 组件", test_streamlit_imports()))
    results.append(("UI 逻辑", check_ui_logic()))
    check_data_directories()

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！知识库界面应该正常显示。")
        print("\n启动应用:")
        print("  python run.py")
        print("  或")
        print("  start_with_py311.bat")
    else:
        print("\n⚠️ 部分测试失败，可能影响知识库界面显示。")
        print("请根据上述错误信息进行修复。")

    print()
    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()
