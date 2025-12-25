"""
应用配置管理
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """应用配置类"""

    # ============================================
    # DeepSeek API 配置
    # ============================================
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = os.getenv(
        "DEEPSEEK_API_URL",
        "https://api.deepseek.com"
    )
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # ============================================
    # 应用配置
    # ============================================
    APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"
    APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")
    CHAT_HISTORY_LENGTH = int(os.getenv("CHAT_HISTORY_LENGTH", 20))

    # ============================================
    # Streamlit 配置
    # ============================================
    STREAMLIT_PAGE_TITLE = "DeepSeek AI 对话"
    STREAMLIT_PAGE_ICON = "🤖"
    STREAMLIT_LAYOUT = "wide"

    # ============================================
    # 数据存储配置
    # ============================================
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

    @classmethod
    def validate(cls):
        """验证必要的配置"""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY 未设置。请在 .env 文件中配置或设置环境变量。"
            )
        return True
