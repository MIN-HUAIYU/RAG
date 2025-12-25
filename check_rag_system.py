"""
完整检查 RAG 系统功能是否满足 DeepSeek 需求
"""

import os
import sys
from loguru import logger

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))


def check_file_upload():
    """检查文件上传功能"""
    logger.info("\n" + "=" * 60)
    logger.info("1. 检查文件上传功能")
    logger.info("=" * 60)

    try:
        from rag.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        logger.success("✅ DocumentProcessor 初始化成功")

        # 测试文本处理
        test_text = "这是一个测试文档。包含多个句子。用于测试文档分块功能。" * 30
        chunks = processor.chunk_documents(test_text)

        if len(chunks) > 0:
            logger.success(f"✅ 文档分块功能正常：生成了 {len(chunks)} 个文档块")
        else:
            logger.error("❌ 文档分块功能异常：未生成文档块")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ 文件上传功能检查失败: {e}")
        return False


def check_vector_embedding():
    """检查向量嵌入功能"""
    logger.info("\n" + "=" * 60)
    logger.info("2. 检查向量嵌入功能")
    logger.info("=" * 60)

    try:
        from rag.embeddings import BGEEmbeddings

        logger.info("正在加载 BGE 模型...")
        embeddings = BGEEmbeddings()
        logger.success("✅ BGE 模型加载成功")

        # 测试查询嵌入
        test_query = "测试查询"
        query_embedding = embeddings.embed_query(test_query)

        if query_embedding is not None and len(query_embedding) == 384:
            logger.success(f"✅ 查询嵌入功能正常：向量维度 {len(query_embedding)}")
        else:
            logger.error("❌ 查询嵌入功能异常")
            return False

        # 测试文档嵌入
        test_docs = ["文档1", "文档2"]
        doc_embeddings = embeddings.embed_documents(test_docs)

        if len(doc_embeddings) == 2:
            logger.success(f"✅ 文档嵌入功能正常：嵌入了 {len(doc_embeddings)} 个文档")
        else:
            logger.error("❌ 文档嵌入功能异常")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ 向量嵌入功能检查失败: {e}")
        return False


def check_vector_store():
    """检查向量存储功能"""
    logger.info("\n" + "=" * 60)
    logger.info("3. 检查向量存储功能")
    logger.info("=" * 60)

    try:
        from rag.vector_store import VectorStore
        from rag.embeddings import BGEEmbeddings

        # 使用测试目录
        test_dir = "./data/test_check_system"
        vector_store = VectorStore(persist_directory=test_dir)
        embeddings = BGEEmbeddings()

        logger.success("✅ VectorStore 初始化成功")

        # 清空测试数据
        try:
            vector_store.delete_collection()
        except:
            pass

        # 测试添加文档
        test_documents = [
            {"text": "DeepSeek 是一个 AI 模型", "source": "test.txt", "chunk_id": 0},
            {"text": "RAG 是检索增强生成技术", "source": "test.txt", "chunk_id": 1},
        ]

        vector_store.add_documents(test_documents, embeddings)
        logger.success(f"✅ 文档添加功能正常：添加了 {len(test_documents)} 个文档")

        # 测试检索
        retrieved = vector_store.retrieve("什么是 DeepSeek", top_k=2, embeddings_manager=embeddings)

        if len(retrieved) > 0:
            logger.success(f"✅ 文档检索功能正常：检索到 {len(retrieved)} 个文档")
            for idx, doc in enumerate(retrieved, 1):
                logger.info(f"  [{idx}] 相关度: {doc['score']:.2%} - {doc['text'][:50]}...")
        else:
            logger.error("❌ 文档检索功能异常：未检索到文档")
            return False

        # 测试统计
        stats = vector_store.get_collection_info()
        doc_count = stats.get("document_count", 0)

        if doc_count == len(test_documents):
            logger.success(f"✅ 知识库统计功能正常：{doc_count} 个文档")
        else:
            logger.warning(f"⚠️ 知识库统计不匹配：预期 {len(test_documents)}，实际 {doc_count}")

        return True

    except Exception as e:
        logger.error(f"❌ 向量存储功能检查失败: {e}")
        return False


def check_rag_retriever():
    """检查 RAG 检索协调器"""
    logger.info("\n" + "=" * 60)
    logger.info("4. 检查 RAG 检索协调器")
    logger.info("=" * 60)

    try:
        from rag.retriever import RAGRetriever
        from rag.vector_store import VectorStore
        from rag.embeddings import BGEEmbeddings

        test_dir = "./data/test_check_system"
        embeddings = BGEEmbeddings()
        vector_store = VectorStore(persist_directory=test_dir)
        retriever = RAGRetriever(vector_store, embeddings)

        logger.success("✅ RAG Retriever 初始化成功")

        # 测试检索和 Prompt 构建（非严格模式）
        query = "什么是 DeepSeek"
        final_prompt, docs = retriever.retrieve_and_build_prompt(
            query,
            top_k=2,
            strict_mode=False
        )

        if len(docs) > 0 and len(final_prompt) > 0:
            logger.success(f"✅ RAG 检索和 Prompt 构建正常（非严格模式）")
            logger.info(f"  - 检索到 {len(docs)} 个文档")
            logger.info(f"  - Prompt 长度: {len(final_prompt)} 字符")
        else:
            logger.error("❌ RAG 检索功能异常")
            return False

        # 测试严格模式
        final_prompt_strict, docs_strict = retriever.retrieve_and_build_prompt(
            query,
            top_k=2,
            strict_mode=True
        )

        if "严格模式" in final_prompt_strict and "禁止" in final_prompt_strict:
            logger.success(f"✅ 严格模式 Prompt 包含正确的指令")
        else:
            logger.warning(f"⚠️ 严格模式 Prompt 可能缺少关键指令")

        # 测试知识库外问题（应该检索不到）
        empty_query = "量子力学是什么"
        final_prompt_empty, docs_empty = retriever.retrieve_and_build_prompt(
            empty_query,
            top_k=2,
            strict_mode=True
        )

        if len(docs_empty) == 0:
            logger.success(f"✅ 知识库外问题正确处理：未检索到文档")
            if "没有找到相关信息" in final_prompt_empty:
                logger.success(f"✅ Prompt 包含正确的空结果提示")

        return True

    except Exception as e:
        logger.error(f"❌ RAG 检索协调器检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_deepseek_integration():
    """检查与 DeepSeek 的集成"""
    logger.info("\n" + "=" * 60)
    logger.info("5. 检查与 DeepSeek 的集成")
    logger.info("=" * 60)

    try:
        from app.services import DeepSeekService
        from app.config import Config

        # 检查配置
        if not Config.DEEPSEEK_API_KEY:
            logger.warning("⚠️ DeepSeek API Key 未配置")
            logger.info("  提示：需要在 .env 文件中设置 DEEPSEEK_API_KEY")
            return False

        logger.success("✅ DeepSeek API Key 已配置")

        service = DeepSeekService(
            api_key=Config.DEEPSEEK_API_KEY,
            api_url=Config.DEEPSEEK_API_URL,
            model=Config.DEEPSEEK_MODEL
        )

        logger.success("✅ DeepSeek Service 初始化成功")
        logger.info(f"  - API URL: {Config.DEEPSEEK_API_URL}")
        logger.info(f"  - 模型: {Config.DEEPSEEK_MODEL}")

        return True

    except Exception as e:
        logger.error(f"❌ DeepSeek 集成检查失败: {e}")
        return False


def check_strict_mode_prompt():
    """检查严格模式的 Prompt 质量"""
    logger.info("\n" + "=" * 60)
    logger.info("6. 检查严格模式 Prompt 质量")
    logger.info("=" * 60)

    try:
        from rag.retriever import RAGRetriever
        from rag.vector_store import VectorStore
        from rag.embeddings import BGEEmbeddings

        test_dir = "./data/test_check_system"
        embeddings = BGEEmbeddings()
        vector_store = VectorStore(persist_directory=test_dir)
        retriever = RAGRetriever(vector_store, embeddings)

        # 获取严格模式 Prompt
        final_prompt, docs = retriever.retrieve_and_build_prompt(
            "测试问题",
            top_k=2,
            strict_mode=True
        )

        # 检查关键词
        required_keywords = [
            "严格模式",
            "禁止",
            "参考文献",
            "用户问题",
            "不要使用你的预训练知识"
        ]

        missing_keywords = []
        for keyword in required_keywords:
            if keyword not in final_prompt:
                missing_keywords.append(keyword)

        if not missing_keywords:
            logger.success("✅ 严格模式 Prompt 包含所有关键指令")
        else:
            logger.warning(f"⚠️ 严格模式 Prompt 缺少关键词: {', '.join(missing_keywords)}")

        # 显示 Prompt 摘要
        logger.info("\n📝 严格模式 Prompt 预览（前 500 字符）：")
        logger.info("-" * 60)
        logger.info(final_prompt[:500])
        logger.info("-" * 60)

        return len(missing_keywords) == 0

    except Exception as e:
        logger.error(f"❌ Prompt 质量检查失败: {e}")
        return False


def main():
    """主检查流程"""
    logger.info("=" * 60)
    logger.info("🔍 RAG 系统功能完整性检查")
    logger.info("=" * 60)

    results = {
        "文件上传": check_file_upload(),
        "向量嵌入": check_vector_embedding(),
        "向量存储": check_vector_store(),
        "RAG 检索": check_rag_retriever(),
        "DeepSeek 集成": check_deepseek_integration(),
        "严格模式 Prompt": check_strict_mode_prompt(),
    }

    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("📊 检查结果总结")
    logger.info("=" * 60)

    for feature, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"{feature:<15} : {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    logger.info("\n" + "=" * 60)
    logger.info(f"总计: {passed_count}/{total_count} 项检查通过")
    logger.info("=" * 60)

    if passed_count == total_count:
        logger.success("\n🎉 所有功能检查通过！系统可以满足 DeepSeek 的需求。")
        logger.info("\n✅ 系统已准备就绪，可以：")
        logger.info("  1. 上传文档到知识库")
        logger.info("  2. 启用 RAG 检索和严格模式")
        logger.info("  3. 提问时 AI 将只使用知识库内容回答")
        return 0
    else:
        logger.error(f"\n❌ {total_count - passed_count} 项检查失败，请修复后重试。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
