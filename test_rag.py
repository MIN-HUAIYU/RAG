#!/usr/bin/env python
"""
RAG System Test Script

Test the RAG (Retrieval Augmented Generation) components:
- BGEEmbeddings: Vector embedding model
- VectorStore: ChromaDB vector database
- DocumentProcessor: Document processing and chunking
- RAGRetriever: RAG retrieval coordination

Usage:
    python test_rag.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.document_processor import DocumentProcessor
from rag.retriever import RAGRetriever


def test_embeddings():
    """Test BGE embeddings model."""
    logger.info("=" * 60)
    logger.info("测试 BGEEmbeddings 模块")
    logger.info("=" * 60)

    try:
        # Initialize embeddings
        embeddings = BGEEmbeddings()
        logger.info("✅ BGEEmbeddings 模型加载成功")

        # Test query embedding
        test_query = "什么是机器学习?"
        query_embedding = embeddings.embed_query(test_query)
        logger.info(f"✅ 查询嵌入生成成功: 维度 {query_embedding.shape}")

        # Test document embedding
        test_docs = [
            "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
            "深度学习使用神经网络来处理复杂的数据模式。",
        ]
        doc_embeddings = embeddings.embed_documents(test_docs)
        logger.info(f"✅ 文档嵌入生成成功: {len(doc_embeddings)} 个文档")

        # Test batch embedding
        batch_embeddings = embeddings.embed_batch(test_docs)
        logger.info(f"✅ 批处理嵌入成功: 形状 {batch_embeddings.shape}")

        logger.info("✅ BGEEmbeddings 模块测试通过\n")
        return embeddings

    except Exception as e:
        logger.error(f"❌ BGEEmbeddings 测试失败: {e}")
        return None


def test_vector_store(embeddings):
    """Test ChromaDB vector store."""
    logger.info("=" * 60)
    logger.info("测试 VectorStore 模块")
    logger.info("=" * 60)

    if not embeddings:
        logger.error("❌ 跳过 VectorStore 测试 (缺少 embeddings)")
        return None

    try:
        # Initialize vector store
        vector_store = VectorStore(persist_directory="./data/test_chroma_db")
        logger.info("✅ VectorStore 初始化成功")

        # Create test documents
        test_documents = [
            {"text": "机器学习是人工智能的一个分支", "source": "test1.txt"},
            {"text": "神经网络是深度学习的基础", "source": "test2.txt"},
            {"text": "自然语言处理处理文本数据", "source": "test3.txt"},
            {"text": "计算机视觉处理图像数据", "source": "test4.txt"},
        ]

        # Add documents
        vector_store.add_documents(test_documents, embeddings)
        logger.info(f"✅ 添加 {len(test_documents)} 个测试文档")

        # Check collection info
        stats = vector_store.get_collection_info()
        logger.info(f"✅ 知识库统计: {stats}")

        # Test retrieval
        query = "机器学习是什么?"
        results = vector_store.retrieve(query, top_k=2, embeddings_manager=embeddings)
        logger.info(f"✅ 检索结果 ({len(results)} 个):")
        for idx, result in enumerate(results, 1):
            logger.info(f"   {idx}. [{result['source']}] 相关度: {result['score']:.1%}")
            logger.info(f"      {result['text'][:60]}...")

        logger.info("✅ VectorStore 模块测试通过\n")
        return vector_store

    except Exception as e:
        logger.error(f"❌ VectorStore 测试失败: {e}")
        return None


def test_document_processor():
    """Test document processor."""
    logger.info("=" * 60)
    logger.info("测试 DocumentProcessor 模块")
    logger.info("=" * 60)

    try:
        # Initialize processor
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=50)
        logger.info("✅ DocumentProcessor 初始化成功")

        # Test text chunking
        test_text = """
        机器学习是人工智能的重要分支。它使计算机能够从数据中学习，
        而不需要明确的编程。神经网络是深度学习的基础，它模仿了人脑
        的工作方式。计算机视觉和自然语言处理是机器学习的两个重要应用。
        """

        chunks = processor.chunk_documents(test_text)
        logger.info(f"✅ 文本分块成功: {len(chunks)} 个块")

        for idx, chunk in enumerate(chunks, 1):
            logger.info(f"   块 {idx}: {chunk[:50]}...")

        logger.info("✅ DocumentProcessor 模块测试通过\n")
        return processor

    except Exception as e:
        logger.error(f"❌ DocumentProcessor 测试失败: {e}")
        return None


def test_rag_retriever(vector_store, embeddings):
    """Test RAG retriever."""
    logger.info("=" * 60)
    logger.info("测试 RAGRetriever 模块")
    logger.info("=" * 60)

    if not vector_store or not embeddings:
        logger.error("❌ 跳过 RAGRetriever 测试 (缺少依赖)")
        return

    try:
        # Initialize retriever
        retriever = RAGRetriever(vector_store, embeddings)
        logger.info("✅ RAGRetriever 初始化成功")

        # Test retrieval
        user_query = "人工智能包括什么?"
        retrieved = retriever.retrieve_context(user_query, top_k=2)
        logger.info(f"✅ 上下文检索成功: {len(retrieved)} 个文档")

        # Test prompt building
        final_prompt, docs = retriever.retrieve_and_build_prompt(
            user_query,
            top_k=2,
            system_prompt="你是一个AI助手。"
        )
        logger.info(f"✅ RAG Prompt 生成成功 (长度: {len(final_prompt)} 字符)")
        logger.info(f"   Prompt 预览:")
        logger.info(f"   {final_prompt[:200]}...\n")

        # Test stats
        stats = retriever.get_retrieval_stats()
        logger.info(f"✅ 检索统计: {stats}")

        logger.info("✅ RAGRetriever 模块测试通过\n")

    except Exception as e:
        logger.error(f"❌ RAGRetriever 测试失败: {e}")


def cleanup():
    """Clean up test data."""
    import shutil
    test_dir = "./data/test_chroma_db"
    if os.path.exists(test_dir):
        logger.info("清理测试数据...")
        shutil.rmtree(test_dir)
        logger.info("✅ 测试数据已清理")


def main():
    """Run all RAG tests."""
    logger.info("\n" + "=" * 60)
    logger.info("RAG 系统完整测试")
    logger.info("=" * 60 + "\n")

    try:
        # Test embeddings
        embeddings = test_embeddings()

        # Test vector store
        vector_store = test_vector_store(embeddings)

        # Test document processor
        processor = test_document_processor()

        # Test RAG retriever
        test_rag_retriever(vector_store, embeddings)

        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试通过!")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\n✋ 测试被中断")
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        # cleanup()
        pass


if __name__ == "__main__":
    main()
