#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接启动 Streamlit 应用的脚本
避免交互式提示
"""

import subprocess
import sys
import os
import io

# 修复 Windows 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 设置环境变量来禁用交互式提示
os.environ["STREAMLIT_BROWSER_SERVER_ADDRESS"] = "localhost"
os.environ["STREAMLIT_SERVER_PORT"] = "8888"
os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"

# 直接运行 streamlit
cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/main.py",
    "--server.port", "8888",
    "--logger.level", "error",
    "--client.showErrorDetails", "false"
]

print("=" * 60)
print("🚀 启动 DeepSeek AI 对话系统...")
print("=" * 60)
print(f"📱 访问地址: http://localhost:8888")
print(f"💡 按 Ctrl+C 停止应用")
print("=" * 60)
print()

# 不使用 shell，直接执行
subprocess.run(cmd, check=False)
