"""
DeepSeek AI 对话应用主入口
Streamlit + DeepSeek API
"""

import streamlit as st
from loguru import logger
from config import Config
from services import DeepSeekService
from components import ChatInterface

# RAG 模块（可选 - 如果安装失败则使用纯对话模式）
RAG_AVAILABLE = False
try:
    import chromadb
    from rag.embeddings import BGEEmbeddings
    from rag.vector_store import VectorStore
    from rag.document_processor import DocumentProcessor
    from rag.retriever import RAGRetriever
    RAG_AVAILABLE = True
    logger.info("RAG modules loaded successfully!")
except ImportError as e:
    logger.warning(f"RAG modules not available: {e}. Running in chat-only mode.")
    RAG_AVAILABLE = False
except Exception as e:
    logger.error(f"Error loading RAG modules: {e}")
    RAG_AVAILABLE = False

# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title=Config.STREAMLIT_PAGE_TITLE,
    page_icon=Config.STREAMLIT_PAGE_ICON,
    layout=Config.STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded",
)

# 自定义 CSS 样式
st.markdown(
    """
    <style>
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .message-user {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .message-assistant {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_app():
    """初始化应用"""
    try:
        # 验证配置
        Config.validate()
        logger.info("应用配置验证成功")
    except ValueError as e:
        st.error(f"❌ 配置错误: {str(e)}")
        st.stop()

    # 初始化聊天界面
    if "chat_interface" not in st.session_state:
        st.session_state.chat_interface = ChatInterface()

    # 初始化 DeepSeek 服务
    if "deepseek_service" not in st.session_state:
        st.session_state.deepseek_service = DeepSeekService(
            api_key=Config.DEEPSEEK_API_KEY,
            api_url=Config.DEEPSEEK_API_URL,
            model=Config.DEEPSEEK_MODEL,
        )

    # 初始化 RAG 模块 (Phase 2)
    if RAG_AVAILABLE:
        if "embeddings_manager" not in st.session_state:
            try:
                with st.spinner("正在加载向量模型..."):
                    st.session_state.embeddings_manager = BGEEmbeddings()
                    logger.info("BGEEmbeddings 模型加载成功")
            except Exception as e:
                logger.warning(f"向量模型加载失败: {e}. 将在纯对话模式下运行")
                st.session_state.embeddings_manager = None

        if "vector_store" not in st.session_state:
            try:
                st.session_state.vector_store = VectorStore()
                logger.info("VectorStore 初始化成功")
            except Exception as e:
                logger.warning(f"向量存储初始化失败: {e}")
                st.session_state.vector_store = None

        if "doc_processor" not in st.session_state:
            st.session_state.doc_processor = DocumentProcessor()

        if "rag_retriever" not in st.session_state:
            if st.session_state.vector_store and st.session_state.embeddings_manager:
                st.session_state.rag_retriever = RAGRetriever(
                    st.session_state.vector_store,
                    st.session_state.embeddings_manager
                )
                logger.info("RAG Retriever 创建成功")
            else:
                st.session_state.rag_retriever = None
                logger.warning("RAG Retriever 创建失败：vector_store 或 embeddings_manager 为 None")
    else:
        # RAG 不可用时，设置为 None
        st.session_state.embeddings_manager = None
        st.session_state.vector_store = None
        st.session_state.doc_processor = None
        st.session_state.rag_retriever = None

    # 初始化 RAG 控制标志 - 默认启用
    if "enable_rag" not in st.session_state:
        st.session_state.enable_rag = True

    # 初始化严格模式标志 - 强制使用知识库
    if "strict_mode" not in st.session_state:
        st.session_state.strict_mode = True

    logger.info("应用初始化完成")


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.markdown("# ⚙️ 设置")

    # API 配置显示
    st.sidebar.markdown("### API 信息")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("模型", Config.DEEPSEEK_MODEL)
    with col2:
        api_key_masked = (
            Config.DEEPSEEK_API_KEY[:10] + "***" if Config.DEEPSEEK_API_KEY else "未设置"
        )
        st.metric("API Key", api_key_masked)

    st.sidebar.divider()

    # 对话参数
    st.sidebar.markdown("### 对话参数")
    temperature = st.sidebar.slider(
        "温度 (Temperature)",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="值越高，回复越随机；值越低，回复越确定性",
    )

    max_tokens = st.sidebar.slider(
        "最大令牌数",
        min_value=100,
        max_value=4000,
        value=2000,
        step=100,
        help="单次回复的最大长度",
    )

    st.sidebar.divider()

    # 对话历史管理
    st.sidebar.markdown("### 对话历史")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        msg_count = len(st.session_state.chat_interface.get_messages())
        st.metric("消息数", msg_count)

    with col2:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.chat_interface.clear_messages()
            st.rerun()

    st.sidebar.divider()

    # RAG 知识库管理 (Phase 2)
    # 检查 RAG 组件状态
    rag_ready = (
        RAG_AVAILABLE and
        st.session_state.get('vector_store') is not None and
        st.session_state.get('embeddings_manager') is not None
    )

    if rag_ready:
        st.sidebar.markdown("### 📚 知识库")

        # 启用/禁用 RAG（强制启用）
        enable_rag = st.sidebar.toggle(
            "启用 RAG 检索",
            value=st.session_state.enable_rag,
            help="启用后，AI 会从知识库中检索相关信息来回答问题",
            disabled=False  # 可以关闭，但默认开启
        )
        st.session_state.enable_rag = enable_rag

        # 严格模式开关
        strict_mode = st.sidebar.toggle(
            "🔒 严格模式（仅知识库）",
            value=st.session_state.strict_mode,
            help="开启后，AI 只能根据本地知识库回答，不使用预训练知识。推荐保持开启。"
        )
        st.session_state.strict_mode = strict_mode

        # 显示知识库统计
        if st.session_state.vector_store:
            try:
                stats = st.session_state.vector_store.get_collection_info()
                doc_count = stats.get("document_count", 0)

                if doc_count > 0:
                    st.sidebar.metric("📖 知识库文档", doc_count, delta="已导入")
                else:
                    st.sidebar.info("📭 知识库为空，请上传文档")

            except Exception as e:
                logger.debug(f"获取知识库统计失败: {e}")

        # 检索日志仅在后台维护，不在界面显示
        if "retrieval_log" not in st.session_state:
            st.session_state.retrieval_log = []

    elif RAG_AVAILABLE:
        # 显示详细的失败原因
        st.sidebar.warning("⚠️ RAG 模块加载失败")

        # 检查具体是哪个组件失败
        if st.session_state.get('embeddings_manager') is None:
            st.sidebar.error("向量模型加载失败")
            st.sidebar.caption("💡 **解决方法**：刷新页面重试")

        if st.session_state.get('vector_store') is None:
            st.sidebar.error("向量存储初始化失败")

    else:
        st.sidebar.info("📭 RAG 功能不可用\n请安装依赖:\n`pip install -r requirements-rag.txt`")

    # 保存参数到 session_state
    st.session_state.temperature = temperature
    st.session_state.max_tokens = max_tokens

    return temperature, max_tokens


def render_document_manager():
    """渲染文档管理区域"""
    # 注意：即使 RAG 模块未完全加载，我们也显示 UI
    # 用户可以看到上传界面，如果依赖缺失会有清晰的错误提示

    # 知识库标题和描述
    st.markdown("""
    ## 📚 知识库管理
    上传文档到知识库，让 AI 可以从您的文档中检索相关信息来提供更准确的答案。
    """)

    # 上传区域 - 使用容器突出显示
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### 📤 上传文档")
            st.markdown("支持 PDF 和 TXT 格式的文档")

            uploaded_file = st.file_uploader(
                "选择文档",
                type=["pdf", "txt"],
                key="main_uploader",
                help="拖拽或点击选择 PDF/TXT 文件",
                label_visibility="collapsed"
            )

            if uploaded_file:
                st.info(f"📄 已选择: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

                if st.button("🚀 立即上传", use_container_width=True, key="main_upload_btn", type="primary"):
                    # 检查必要组件
                    if not st.session_state.doc_processor:
                        st.error("❌ 文档处理器未初始化")
                        return
                    if not st.session_state.vector_store:
                        st.error("❌ 向量存储未初始化")
                        return
                    if not st.session_state.embeddings_manager:
                        st.error("❌ 向量模型未加载")
                        return

                    try:
                        progress_bar = st.progress(0, text="处理中... 0%")

                        # 保存临时文件
                        import os
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_path = tmp_file.name

                        progress_bar.progress(20, text="处理中... 20%")

                        # 处理文件
                        documents = st.session_state.doc_processor.process_file(tmp_path)
                        progress_bar.progress(50, text=f"处理中... 50% ({len(documents)} 个文档块)")

                        # 添加到向量库
                        st.session_state.vector_store.add_documents(
                            documents,
                            st.session_state.embeddings_manager
                        )
                        progress_bar.progress(90, text="处理中... 90%")

                        # 清理临时文件
                        os.unlink(tmp_path)

                        progress_bar.progress(100, text="处理中... 100%")

                        # 显示成功提示
                        st.success(f"✅ 成功导入 {len(documents)} 个文档块到知识库！", icon="✅")
                        logger.info(f"导入文档: {uploaded_file.name}, {len(documents)} 个块")

                        # 提示用户刷新页面以继续上传
                        st.info("💡 刷新页面可继续上传更多文档")

                    except Exception as e:
                        st.error(f"❌ 上传失败: {str(e)}", icon="❌")
                        logger.error(f"文档上传失败: {e}")

        with col2:
            st.markdown("### 📊 知识库统计")
            # 显示知识库统计
            if st.session_state.vector_store:
                try:
                    stats = st.session_state.vector_store.get_collection_info()
                    doc_count = stats.get("document_count", 0)
                    st.metric("文档块", doc_count, delta=None)

                    # 清空知识库按钮
                    if st.button("🗑️ 清空知识库", use_container_width=True, key="clear_kb_btn"):
                        st.session_state.vector_store.delete_collection()
                        st.success("✅ 知识库已清空")
                        st.rerun()

                except Exception as e:
                    logger.debug(f"获取知识库统计失败: {e}")
                    st.error("❌ 无法获取统计信息")
            else:
                st.error("向量存储未初始化")

    # 使用提示
    st.markdown("### 💡 使用提示")
    with st.expander("点击查看详细说明"):
        st.markdown("""
        **支持的文件格式：**
        - 📄 **PDF** 文件：自动提取文本
        - 📝 **TXT** 文件：纯文本文件

        **文件处理流程：**
        1. 上传文件后自动分块（800字符/块，100字符重叠）
        2. 文档块通过 BGE 模型转换为向量表示
        3. 向量存储在 ChromaDB 中（持久化保存）

        **性能建议：**
        - 单个文件大小：< 50MB
        - 推荐文档数量：5-20 个文档
        - 首次使用可能较慢（模型下载 ~400MB）

        **RAG 工作原理：**
        提交问题后，系统会：
        1. 在知识库中搜索 3 个最相关的文档块
        2. 将这些上下文注入到提示词
        3. 让 AI 基于您的文档来回答问题
        """)

    st.divider()


def render_main():
    """渲染主聊天区域"""
    st.markdown("# 🤖 DeepSeek AI 对话助手")
    st.markdown(
        "基于 DeepSeek API 的智能对话系统，支持流式输出和实时交互。"
    )

    st.divider()

    # 渲染文档管理区域（如果 RAG 模块可用）
    if RAG_AVAILABLE:
        render_document_manager()
        st.divider()

    # 显示聊天历史
    chat_interface = st.session_state.chat_interface
    chat_interface.render_messages()

    # 处理用户输入
    user_input = chat_interface.render_input()

    if user_input:
        # 添加用户消息到历史
        chat_interface.add_message("user", user_input)

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_input)

        # 获取参数
        temperature = st.session_state.get("temperature", 0.7)
        max_tokens = st.session_state.get("max_tokens", 2000)

        # RAG 检索 (如果启用)
        retrieved_docs = []
        final_prompt = user_input
        strict_mode = st.session_state.get("strict_mode", True)

        # 记录 RAG 状态
        logger.info(f"=== RAG 状态检查 ===")
        logger.info(f"enable_rag: {st.session_state.enable_rag}")
        logger.info(f"strict_mode: {strict_mode}")
        logger.info(f"rag_retriever 存在: {st.session_state.rag_retriever is not None}")

        if st.session_state.enable_rag and st.session_state.rag_retriever:
            logger.info("✅ RAG 检索已启用，开始检索流程")

            # 检查知识库是否为空
            try:
                kb_stats = st.session_state.vector_store.get_collection_info()
                doc_count = kb_stats.get("document_count", 0)
                logger.info(f"知识库文档数: {doc_count}")

                if doc_count == 0 and strict_mode:
                    # 严格模式下，知识库为空则不允许提问
                    logger.warning("⚠️ 严格模式下知识库为空，阻止提问")
                    st.error("❌ 知识库为空！请先上传文档后再提问。")
                    st.info("💡 在上方【知识库管理】区域上传 PDF 或 TXT 文档")
                    st.stop()

            except Exception as e:
                logger.error(f"检查知识库状态失败: {e}")

            try:
                with st.spinner("正在思考..."):
                    logger.info(f"开始检索: 查询='{user_input}', top_k=5, strict_mode={strict_mode}")
                    final_prompt, retrieved_docs = st.session_state.rag_retriever.retrieve_and_build_prompt(
                        user_input,
                        top_k=5,  # 增加检索数量以获得更多上下文
                        system_prompt=None,
                        strict_mode=strict_mode
                    )
                    logger.info(f"✅ RAG 检索完成: 获得 {len(retrieved_docs)} 个相关内容 (strict_mode={strict_mode})")

                    # 记录检索到的文档
                    if retrieved_docs:
                        for idx, doc in enumerate(retrieved_docs, 1):
                            logger.info(f"  [{idx}] {doc['source']} - 相关度: {doc['score']:.2%} - 内容长度: {len(doc['text'])} 字符")
                    else:
                        logger.warning("⚠️ 未检索到任何文档")

                    # 记录检索日志
                    if retrieved_docs:
                        avg_score = sum(doc.get('score', 0) for doc in retrieved_docs) / len(retrieved_docs)
                        log_entry = {
                            'query': user_input,
                            'count': len(retrieved_docs),
                            'avg_score': avg_score,
                            'docs': retrieved_docs
                        }
                        st.session_state.retrieval_log.append(log_entry)
                        # 只保留最近 20 条记录
                        if len(st.session_state.retrieval_log) > 20:
                            st.session_state.retrieval_log = st.session_state.retrieval_log[-20:]
                    elif strict_mode:
                        # 严格模式下没有检索到文档
                        logger.warning(f"严格模式：未检索到相关文档")

            except Exception as e:
                logger.warning(f"RAG 检索失败: {e}. 使用原始prompt")
                final_prompt = user_input

        # 调用 API 获取 AI 回复
        try:
            with st.spinner("AI 正在思考..."):
                deepseek_service = st.session_state.deepseek_service

                # 使用流式输出
                with st.chat_message("assistant"):
                    # 参考文献在后台使用，不在前端显示
                    # 只记录到日志中供开发者查看
                    if retrieved_docs:
                        logger.info(f"使用了 {len(retrieved_docs)} 个知识库文档作为上下文（不在界面显示）")
                        for idx, doc in enumerate(retrieved_docs, 1):
                            logger.debug(f"  [{idx}] {doc.get('source', '未知')} - 相关度: {doc.get('score', 0):.2%}")

                    message_placeholder = st.empty()
                    full_response = ""

                    # 流式获取响应
                    for chunk in deepseek_service.stream_chat(
                        prompt=final_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    ):
                        full_response += chunk
                        # 显示流式内容
                        message_placeholder.markdown(full_response + "▌")

                    # 移除光标
                    message_placeholder.markdown(full_response)

                # 将完整回复添加到历史
                chat_interface.add_message("assistant", full_response)

                logger.info(f"生成回复: {len(full_response)} 个字符")

        except Exception as e:
            logger.error(f"API 调用失败: {str(e)}")
            chat_interface.display_error(
                f"❌ 发生错误: {str(e)}",
                error_type="error"
            )
            st.stop()


def main():
    """主函数"""
    initialize_app()

    # 渲染侧边栏并获取参数
    temperature, max_tokens = render_sidebar()

    # 渲染主区域
    render_main()


if __name__ == "__main__":
    main()
