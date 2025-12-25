#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek AI 对话系统 - 命令行演示脚本
演示基础对话功能（无需启动 Streamlit）
"""

import sys
import io

# 修复 Windows 中文编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.config import Config
from app.services import DeepSeekService

def demo_basic_chat():
    """演示基础对话"""
    print("\n" + "=" * 60)
    print("🤖 DeepSeek AI 对话系统 - 命令行演示")
    print("=" * 60)

    # 验证配置
    try:
        Config.validate()
        print("✅ 配置验证成功\n")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return

    # 初始化服务
    service = DeepSeekService(
        api_key=Config.DEEPSEEK_API_KEY,
        api_url=Config.DEEPSEEK_API_URL,
        model=Config.DEEPSEEK_MODEL
    )

    # 演示问题
    questions = [
        "你好，请自我介绍一下",
        "Python 和 JavaScript 的主要区别是什么？",
        "什么是 RAG 技术？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n📝 问题 {i}: {question}")
        print("-" * 60)
        print("💬 回复: ", end="", flush=True)

        try:
            # 流式获取响应
            full_response = ""
            for chunk in service.stream_chat(
                prompt=question,
                temperature=0.7,
                max_tokens=300
            ):
                print(chunk, end="", flush=True)
                full_response += chunk

            print("\n")

        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")
            break

    print("=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    print("\n💡 下一步:")
    print("   运行 Streamlit 应用获得完整的 UI 体验:")
    print("   python run.py")
    print("   或")
    print("   streamlit run app/main.py")

if __name__ == "__main__":
    demo_basic_chat()
