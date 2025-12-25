"""
Streamlit 聊天界面组件
"""

import streamlit as st
from typing import List, Dict, Callable


class ChatInterface:
    """聊天界面管理类"""

    def __init__(self, session_state_key: str = "messages"):
        """
        初始化聊天界面

        Args:
            session_state_key: Streamlit session_state 中存储消息的键
        """
        self.session_state_key = session_state_key
        self._initialize_session_state()

    def _initialize_session_state(self):
        """初始化 session_state"""
        if self.session_state_key not in st.session_state:
            st.session_state[self.session_state_key] = []

    def add_message(self, role: str, content: str):
        """
        添加消息到聊天历史

        Args:
            role: 消息角色 ("user" 或 "assistant")
            content: 消息内容
        """
        message = {"role": role, "content": content}
        st.session_state[self.session_state_key].append(message)

    def get_messages(self) -> List[Dict]:
        """获取所有消息"""
        return st.session_state[self.session_state_key]

    def get_last_message(self) -> Dict or None:
        """获取最后一条消息"""
        messages = self.get_messages()
        return messages[-1] if messages else None

    def clear_messages(self):
        """清空所有消息"""
        st.session_state[self.session_state_key] = []

    def render_messages(self):
        """
        渲染消息到 Streamlit 界面
        支持不同样式的用户和助手消息
        """
        messages = self.get_messages()

        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render_input(self, placeholder: str = "输入你的问题...") -> str:
        """
        渲染输入框

        Args:
            placeholder: 占位符文本

        Returns:
            用户输入的文本，如果没有输入则返回空字符串
        """
        user_input = st.chat_input(placeholder)
        return user_input or ""

    def display_loading(self):
        """显示加载动画"""
        return st.spinner("AI 正在思考...")

    def stream_response(self, response_generator, container=None):
        """
        流式显示 AI 响应

        Args:
            response_generator: 生成器对象，逐个产生响应文本
            container: Streamlit 容器（如果为 None 则自动创建）

        Returns:
            完整的响应文本
        """
        if container is None:
            container = st.container()

        with container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                for chunk in response_generator:
                    full_response += chunk
                    # 显示完整回复加光标效果
                    message_placeholder.markdown(full_response + "▌")

                # 移除光标，显示最终回复
                message_placeholder.markdown(full_response)

        return full_response

    def display_error(self, error_message: str, error_type: str = "error"):
        """
        显示错误信息

        Args:
            error_message: 错误消息
            error_type: 错误类型 ("error", "warning", "info", "success")
        """
        if error_type == "error":
            st.error(error_message)
        elif error_type == "warning":
            st.warning(error_message)
        elif error_type == "info":
            st.info(error_message)
        elif error_type == "success":
            st.success(error_message)

    @staticmethod
    def create_sidebar_section(title: str):
        """
        在侧边栏创建一个部分

        Args:
            title: 部分标题

        Example:
            ChatInterface.create_sidebar_section("⚙️ 设置")
        """
        with st.sidebar:
            st.markdown(f"### {title}")
            return st.container()

    @staticmethod
    def create_columns(num_columns: int = 2):
        """
        创建并排的列

        Args:
            num_columns: 列数

        Returns:
            Streamlit 列对象的列表
        """
        return st.columns(num_columns)
