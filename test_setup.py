#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证项目环境配置
检查依赖、配置文件、API 连接等
"""

import sys
import os

# 修复 Windows 中文编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def check_python_version():
    """检查 Python 版本"""
    print("✓ 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} 符合要求")
        return True
    else:
        print(f"  ❌ Python 版本过低: {version.major}.{version.minor} (需要 3.9+)")
        return False

def check_dependencies():
    """检查必要的依赖"""
    print("\n✓ 检查依赖包...")
    required = ["streamlit", "httpx", "dotenv", "loguru", "pydantic"]
    failed = []

    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (未安装)")
            failed.append(package)

    if failed:
        print(f"\n  运行以下命令安装缺失的包:")
        print(f"  pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """检查 .env 文件"""
    print("\n✓ 检查 .env 配置文件...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(project_root, ".env")

    if not os.path.exists(env_file):
        print(f"  ❌ .env 文件不存在")
        print(f"  请运行: cp .env.example .env")
        return False

    print(f"  ✅ .env 文件存在")
    return True

def check_api_config():
    """检查 API 配置"""
    print("\n✓ 检查 API 配置...")
    try:
        from app.config import Config
        Config.validate()
        print(f"  ✅ DeepSeek API Key 已配置")
        print(f"  ✅ API URL: {Config.DEEPSEEK_API_URL}")
        print(f"  ✅ Model: {Config.DEEPSEEK_MODEL}")
        return True
    except ValueError as e:
        print(f"  ❌ API 配置错误: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ 读取配置失败: {str(e)}")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n✓ 检查项目结构...")
    required_dirs = [
        "app",
        "app/services",
        "app/components",
        "data",
        "logs",
        ".streamlit"
    ]

    project_root = os.path.dirname(os.path.abspath(__file__))
    all_exist = True

    for dir_path in required_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.isdir(full_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} (不存在)")
            all_exist = False

    return all_exist

def check_api_connection():
    """检查 API 连接（可选）"""
    print("\n✓ 检查 API 连接...")
    try:
        from app.config import Config
        from app.services import DeepSeekService

        print("  正在测试 API 连接...")
        service = DeepSeekService(
            api_key=Config.DEEPSEEK_API_KEY,
            api_url=Config.DEEPSEEK_API_URL,
            model=Config.DEEPSEEK_MODEL
        )

        # 测试连接
        response = service.sync_chat("你好", max_tokens=10)
        if response:
            print(f"  ✅ API 连接成功")
            print(f"  回复预览: {response[:50]}...")
            return True
        else:
            print(f"  ⚠️ API 返回为空")
            return False

    except Exception as e:
        print(f"  ⚠️ API 连接失败: {str(e)}")
        print(f"  这可能是网络问题或 API Key 错误")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 DeepSeek AI 对话系统 - 环境检查")
    print("=" * 60)

    checks = [
        ("Python 版本", check_python_version),
        ("依赖包", check_dependencies),
        (".env 配置", check_env_file),
        ("项目结构", check_project_structure),
        ("API 配置", check_api_config),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"  ❌ 检查失败: {str(e)}")
            results[name] = False

    # API 连接检查（可选）
    print("\n" + "=" * 60)
    print("⚙️ 可选检查")
    print("=" * 60)
    try:
        api_ok = check_api_connection()
        results["API 连接"] = api_ok
    except Exception as e:
        print(f"  ⚠️ 跳过 API 连接检查: {str(e)}")

    # 总结
    print("\n" + "=" * 60)
    print("📋 检查总结")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n✨ 环境检查完成！")
        print("现在可以启动应用:")
        print("  python run.py")
        print("  或")
        print("  streamlit run app/main.py")
        return 0
    else:
        print("\n❌ 存在未通过的检查，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
