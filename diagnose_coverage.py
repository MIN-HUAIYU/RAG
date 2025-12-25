#!/usr/bin/env python3
"""
📊 文档知识覆盖率诊断工具

用途：上传文档后，使用此工具诊断知识库中的知识是否被正确识别和索引。

使用方法：
    python diagnose_coverage.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | {message}",
    level="INFO"
)


def main():
    """Run diagnostic tests on document coverage."""

    print("\n" + "="*70)
    print("📊 文档知识覆盖率诊断工具")
    print("="*70 + "\n")

    try:
        # Initialize components
        print("🔧 初始化组件...")
        embeddings = BGEEmbeddings()
        vector_store = VectorStore()
        retriever = RAGRetriever(vector_store, embeddings)

        # Check knowledge base status
        print("\n📚 知识库状态：")
        stats = retriever.get_retrieval_stats()
        print(f"   - 文档总数: {stats.get('document_count', 0)}")
        print(f"   - 集合名称: {stats.get('collection_name', 'N/A')}")

        if stats.get('document_count', 0) == 0:
            print("\n⚠️  知识库为空，请先上传文档！")
            return

        # Define test queries for coverage diagnosis
        print("\n🔍 执行诊断查询...\n")

        test_queries = [
            "这是什么？",
            "请介绍一下主要内容",
            "文档中的关键信息是什么？",
            "有哪些重要概念？",
            "请总结文档的核心内容",
        ]

        # Run diagnostic
        results = retriever.diagnose_document_coverage(test_queries)

        # Print results
        print("\n" + "="*70)
        print("📈 诊断结果")
        print("="*70)

        print(f"\n覆盖率: {results['coverage_rate']:.1%} ({results['covered_queries']}/{results['total_queries']})")

        if results['uncovered_queries']:
            print(f"\n❌ 未被覆盖的查询 ({len(results['uncovered_queries'])} 个):")
            for query in results['uncovered_queries']:
                print(f"   - {query}")
        else:
            print("\n✅ 所有测试查询都有覆盖！")

        print("\n📊 详细结果:")
        print("-" * 70)

        for detail in results['details']:
            query = detail.get('query', 'N/A')
            is_covered = detail.get('is_covered', False)
            doc_count = detail.get('document_count', 0)
            scores = detail.get('top_scores', [])

            status = "✅" if is_covered else "❌"
            avg_score = sum(scores) / len(scores) if scores else 0

            print(f"\n{status} 查询: \"{query}\"")
            print(f"   检索到: {doc_count} 个文档")
            if scores:
                print(f"   相关度: {scores[0]:.1%} (最高) / {avg_score:.1%} (平均)")

        print("\n" + "="*70)
        print("💡 建议：")
        print("="*70)

        if results['coverage_rate'] >= 0.8:
            print("✅ 知识库覆盖率很好！")
        elif results['coverage_rate'] >= 0.5:
            print("⚠️  知识库覆盖率中等，建议：")
            print("   1. 检查文档是否被正确解析")
            print("   2. 尝试调整文档分块大小（chunk_size）")
            print("   3. 上传更多相关文档")
        else:
            print("❌ 知识库覆盖率较低，建议：")
            print("   1. 上传更多相关文档")
            print("   2. 清空知识库重新上传（确保文档格式正确）")
            print("   3. 检查文档内容是否与查询相关")

        print("\n" + "="*70 + "\n")

    except Exception as e:
        print(f"\n❌ 诊断失败: {e}")
        logger.exception("Diagnostic error")
        sys.exit(1)


if __name__ == "__main__":
    main()
