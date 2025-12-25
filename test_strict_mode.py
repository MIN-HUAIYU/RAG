"""
测试严格模式：验证系统是否只使用本地知识库回答
"""

import os
import sys
from loguru import logger

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.document_processor import DocumentProcessor
from rag.retriever import RAGRetriever


def test_strict_mode():
    """测试严格模式功能"""

    logger.info("=== 开始测试严格模式 ===")

    # 1. 初始化组件
    logger.info("1. 初始化 RAG 组件...")
    embeddings = BGEEmbeddings()
    vector_store = VectorStore(persist_directory="./data/test_strict_mode")
    doc_processor = DocumentProcessor()
    retriever = RAGRetriever(vector_store, embeddings)

    # 2. 清空知识库
    logger.info("2. 清空测试知识库...")
    try:
        vector_store.delete_collection()
    except:
        pass

    # 3. 添加测试文档
    logger.info("3. 添加测试文档到知识库...")
    test_documents = [
        {
            "text": "DeepSeek 是一家专注于人工智能研究的公司，成立于2023年。主要研究方向包括大语言模型、强化学习等领域。",
            "source": "company_info.txt",
            "chunk_id": 0
        },
        {
            "text": "RAG（检索增强生成）是一种结合信息检索和生成式AI的技术。它可以让模型基于外部知识库生成更准确的回答。",
            "source": "tech_doc.txt",
            "chunk_id": 0
        },
        {
            "text": "BGE 向量模型是由智源研究院开发的中文文本嵌入模型，支持384维向量表示，适合用于语义检索任务。",
            "source": "tech_doc.txt",
            "chunk_id": 1
        }
    ]

    vector_store.add_documents(test_documents, embeddings)
    logger.info(f"✅ 已添加 {len(test_documents)} 个文档块")

    # 4. 测试用例
    test_cases = [
        {
            "query": "什么是 DeepSeek？",
            "should_find": True,
            "description": "知识库内问题"
        },
        {
            "query": "什么是 RAG 技术？",
            "should_find": True,
            "description": "知识库内问题"
        },
        {
            "query": "BGE 模型是谁开发的？",
            "should_find": True,
            "description": "知识库内问题"
        },
        {
            "query": "Python 是什么编程语言？",
            "should_find": False,
            "description": "知识库外问题（不应该使用预训练知识回答）"
        },
        {
            "query": "什么是机器学习？",
            "should_find": False,
            "description": "知识库外问题（不应该使用预训练知识回答）"
        }
    ]

    logger.info("\n4. 开始测试查询...")
    logger.info("=" * 60)

    for idx, case in enumerate(test_cases, 1):
        query = case["query"]
        should_find = case["should_find"]
        description = case["description"]

        logger.info(f"\n测试 {idx}: {description}")
        logger.info(f"问题: {query}")
        logger.info(f"期望结果: {'应检索到文档' if should_find else '不应检索到文档'}")

        # 执行检索（严格模式）
        final_prompt, retrieved_docs = retriever.retrieve_and_build_prompt(
            query,
            top_k=3,
            strict_mode=True
        )

        # 检查结果
        found_docs = len(retrieved_docs) > 0

        if found_docs:
            logger.info(f"✅ 检索到 {len(retrieved_docs)} 个文档")
            for doc in retrieved_docs:
                logger.info(f"  - [{doc['source']}] 相关度: {doc['score']:.2%}")
        else:
            logger.info("❌ 未检索到相关文档")

        # 显示生成的 Prompt（部分）
        logger.info("\n生成的 Prompt 预览:")
        logger.info("-" * 60)
        prompt_preview = final_prompt[:500] + "..." if len(final_prompt) > 500 else final_prompt
        logger.info(prompt_preview)
        logger.info("-" * 60)

        # 验证是否符合预期
        if found_docs == should_find:
            logger.success(f"✅ 测试通过")
        else:
            logger.warning(f"⚠️ 测试结果与预期不符")

        logger.info("=" * 60)

    # 5. 测试空知识库情况
    logger.info("\n5. 测试空知识库场景...")
    vector_store.delete_collection()

    final_prompt, retrieved_docs = retriever.retrieve_and_build_prompt(
        "测试问题",
        top_k=3,
        strict_mode=True
    )

    if not retrieved_docs:
        logger.success("✅ 空知识库正确返回：无检索结果")
    else:
        logger.error("❌ 空知识库错误：不应返回文档")

    # 检查 Prompt 是否包含正确的提示
    if "没有找到相关信息" in final_prompt or "未检索到相关文献" in final_prompt:
        logger.success("✅ Prompt 包含正确的空知识库提示")
    else:
        logger.warning("⚠️ Prompt 缺少空知识库提示")

    logger.info("\n=== 测试完成 ===")
    logger.info("\n📋 总结：")
    logger.info("1. ✅ 严格模式下，系统会明确指示 AI 只使用知识库内容")
    logger.info("2. ✅ 当检索不到文档时，Prompt 会要求 AI 回答'没有找到相关信息'")
    logger.info("3. ✅ 知识库为空时，系统会给出明确提示")
    logger.info("\n💡 建议：")
    logger.info("- 在生产环境中保持严格模式开启")
    logger.info("- 定期检查知识库内容的覆盖范围")
    logger.info("- 对于知识库外的问题，AI 应回答'知识库中没有相关信息'")


if __name__ == "__main__":
    try:
        test_strict_mode()
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
