"""RAG Retriever for integrating retrieved documents into prompts."""

from loguru import logger


class RAGRetriever:
    """
    RAG (Retrieval Augmented Generation) retriever for document-augmented generation.

    Coordinates:
    - Document retrieval from vector store
    - Prompt building with retrieved context
    - Integration with language models
    """

    def __init__(self, vector_store, embeddings_manager):
        """
        Initialize RAG retriever.

        Args:
            vector_store: VectorStore instance
            embeddings_manager: BGEEmbeddings instance
        """
        self.vector_store = vector_store
        self.embeddings_manager = embeddings_manager
        logger.info("RAG Retriever initialized")

    def retrieve_context(self, query: str, top_k: int = 3) -> list:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query
            top_k: Number of top documents to retrieve

        Returns:
            List of retrieved documents with scores
        """
        logger.debug(f"Retrieving documents for query: {query[:50]}...")

        retrieved = self.vector_store.retrieve(
            query,
            top_k=top_k,
            embeddings_manager=self.embeddings_manager
        )

        logger.debug(f"Retrieved {len(retrieved)} documents")
        return retrieved

    def build_rag_prompt(self, user_query: str, retrieved_docs: list, system_prompt: str = None, strict_mode: bool = True) -> str:
        """
        Build a RAG prompt by combining user query with retrieved context.

        Args:
            user_query: Original user query
            retrieved_docs: List of retrieved documents
            system_prompt: Optional system prompt
            strict_mode: If True, enforce strict knowledge-base-only answering

        Returns:
            Enhanced prompt with context
        """
        # Start with system prompt if provided
        prompt_parts = []

        # Enhanced system instruction with detailed requirements
        enhanced_instruction = """【系统角色】
你是一个**只能根据下方提供的知识库内容回答问题**的助手。

⚠️ 核心规则（必须遵守）：
- 你**只能**使用下方【知识库内容】中的信息来回答
- **禁止**使用你的预训练知识、常识或任何外部信息
- 如果知识库中没有相关内容，**必须说**：'抱歉，知识库中没有这方面的信息。'
"""

        # Always use strict instruction
        prompt_parts.append(enhanced_instruction)

        if system_prompt:
            prompt_parts.append(system_prompt)

        # Add retrieved context
        if retrieved_docs:
            context_section = "\n【知识库内容 - 你只能使用以下内容回答】\n"
            context_section += "=" * 50 + "\n"

            for idx, doc in enumerate(retrieved_docs, 1):
                text = doc["text"].replace("\n", " ")
                source = doc.get("source", "未知")
                context_section += f"[文档{idx}] 来源: {source}\n{text}\n\n"

            context_section += "=" * 50 + "\n"
            prompt_parts.append(context_section)
        else:
            # No documents retrieved
            context_section = "\n【知识库内容】\n⚠️ 知识库中没有找到相关内容。你必须回答：'抱歉，知识库中没有这方面的信息。'\n"
            prompt_parts.append(context_section)

        # Add user query
        prompt_parts.append(f"【用户问题】\n{user_query}\n")

        # Final instruction
        if retrieved_docs:
            final_instruction = """【回答要求】
请**只根据上方知识库内容**回答用户问题。
- 如果知识库内容能回答问题，请详细回答
- 如果知识库内容不足以回答，请说'知识库中的信息有限，只能告诉你...'然后说知识库里有的内容
- **绝对禁止**编造或使用知识库以外的信息"""
        else:
            final_instruction = """【回答要求】
知识库中没有相关内容，你**必须**回答：
'抱歉，知识库中没有这方面的信息，无法回答您的问题。'
**禁止**使用任何其他知识回答！"""
        prompt_parts.append(final_instruction)

        final_prompt = "\n".join(prompt_parts)
        logger.debug(f"Built RAG prompt (strict_mode={strict_mode}, docs={len(retrieved_docs)}, length: {len(final_prompt)})")

        return final_prompt

    def retrieve_and_build_prompt(
        self,
        user_query: str,
        top_k: int = 3,
        system_prompt: str = None,
        strict_mode: bool = True
    ) -> tuple:
        """
        Combined method to retrieve documents and build RAG prompt.

        Args:
            user_query: User query
            top_k: Number of documents to retrieve
            system_prompt: Optional system prompt
            strict_mode: If True, enforce strict knowledge-base-only answering

        Returns:
            Tuple of (final_prompt, retrieved_docs)
        """
        logger.info(f"RAG retrieval for: {user_query[:50]}... (strict_mode={strict_mode})")

        # Retrieve documents
        retrieved_docs = self.retrieve_context(user_query, top_k=top_k)

        # Build prompt
        final_prompt = self.build_rag_prompt(user_query, retrieved_docs, system_prompt, strict_mode)

        return final_prompt, retrieved_docs

    def get_retrieval_stats(self) -> dict:
        """
        Get statistics about vector store and retrieval.

        Returns:
            Dictionary with collection statistics
        """
        return self.vector_store.get_collection_info()

    def diagnose_document_coverage(self, queries: list) -> dict:
        """
        Diagnose document coverage by testing retrieval with multiple query variations.

        This helps identify if certain knowledge in your documents is being missed.

        Args:
            queries: List of test queries to check coverage

        Returns:
            Dictionary with diagnostic results:
            {
                'total_queries': int,
                'covered_queries': int,
                'coverage_rate': float,
                'uncovered_queries': list,
                'details': list of detailed results
            }
        """
        logger.info(f"🔍 开始诊断文档覆盖率，测试 {len(queries)} 个查询")

        results = {
            'total_queries': len(queries),
            'covered_queries': 0,
            'coverage_rate': 0.0,
            'uncovered_queries': [],
            'details': []
        }

        for query in queries:
            try:
                retrieved = self.retrieve_context(query, top_k=3)
                is_covered = len(retrieved) > 0

                detail = {
                    'query': query,
                    'is_covered': is_covered,
                    'document_count': len(retrieved),
                    'top_scores': [doc.get('score', 0) for doc in retrieved[:3]]
                }

                if is_covered:
                    results['covered_queries'] += 1
                    logger.debug(f"✅ 覆盖: '{query}' - 检索到 {len(retrieved)} 个文档，最高相关度: {retrieved[0].get('score', 0):.1%}")
                else:
                    results['uncovered_queries'].append(query)
                    logger.warning(f"❌ 未覆盖: '{query}' - 没有检索到相关文档")

                results['details'].append(detail)

            except Exception as e:
                logger.error(f"诊断查询失败: {query} - {e}")
                results['details'].append({
                    'query': query,
                    'error': str(e)
                })

        results['coverage_rate'] = results['covered_queries'] / results['total_queries'] if results['total_queries'] > 0 else 0

        logger.info(f"📊 诊断完成: 覆盖率 {results['coverage_rate']:.1%} ({results['covered_queries']}/{results['total_queries']})")

        return results
