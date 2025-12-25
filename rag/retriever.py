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

        # Enhanced system instruction with detailed requirements (NO mention of documents/references)
        enhanced_instruction = """【系统角色与要求】
你是一个专业的知识助手。你的任务是根据知识库中的内容，为用户的问题提供详细、全面、高质量的答案。

✨ 回答质量标准：
1. 深度：深入分析问题，提供系统性的解释和多个角度的分析
2. 完整性：全面覆盖问题的各个方面，确保答案充分完整
3. 准确性：严格基于知识库内容，避免任何推测或编造
4. 清晰性：逻辑清晰，层次分明，易于理解
5. 自然性：像一个知识渊博的人直接回答，不要提及文献、参考或数据来源

📝 回答结构建议：
- 核心答案：先给出直接的、明确的答案
- 详细解释：展开说明原因、背景或相关概念
- 补充信息：提供相关的细节、例子或扩展内容
- 相关联系：说明与其他概念或领域的关联（若适用）

🎯 具体要求：
1. 回答要充分融合知识库中的所有相关信息
2. 组织答案时要确保逻辑连贯、层次清晰
3. 自然融合多个知识点，不要重复原文
4. 提供具体的数字、例子或详细信息以支持观点
5. 如果问题有多个方面，分别阐述并总结
6. 【重要】绝不要提及"根据文献"、"参考文献"、"文献中"等词汇
7. 【重要】直接表述事实，就像在讲述你知道的内容一样
"""

        # Add strict mode system instruction
        if strict_mode:
            strict_instruction = """
【⚠️ 严格模式 - 必须遵守】
你是一个基于本地知识库的专业问答助手。请严格遵守以下规则：

⛔ 禁止事项：
1. 绝对禁止使用你的预训练知识、常识或外部信息
2. 禁止根据你已知的任何知识来回答问题
3. 禁止推测、假设或编造任何信息
4. 禁止说"根据我的了解"、"据我所知"等暗示使用预训练知识的表述
5. 不要重复列出文献的原文片段，而要提炼和综合

✅ 必须做到：
1. 只能、仅能、必须根据下方【参考文献】中的内容来回答
2. 如果参考文献中没有相关信息，必须回答："抱歉，我在知识库中没有找到相关信息，无法回答这个问题。"
3. 在保证准确性的前提下，尽可能详细和全面地回答
4. 保持100%准确，只说文献中明确提到的内容
"""
            prompt_parts.append(enhanced_instruction)
            prompt_parts.append(strict_instruction)
        else:
            prompt_parts.append(enhanced_instruction)

        if system_prompt:
            prompt_parts.append(system_prompt)

        # Add retrieved context (WITHOUT showing it as "文献" - integrate seamlessly)
        if retrieved_docs:
            context_section = "\n【知识库内容】\n"

            for idx, doc in enumerate(retrieved_docs, 1):
                # Use full text for better context
                text = doc["text"].replace("\n", " ")
                context_section += f"{text}\n\n"

            prompt_parts.append(context_section)
        else:
            # No documents retrieved
            if strict_mode:
                context_section = "\n【知识库内容】\n（知识库中暂无相关内容）\n"
                prompt_parts.append(context_section)

        # Add user query
        prompt_parts.append(f"【用户问题】\n{user_query}\n")

        # Add instruction for seamless answer (NOT mentioning documents/references)
        context_linking = """【回答要求】
请基于上述知识库内容，详细、全面、逻辑清晰地直接回答用户的问题。要求：
1. 直接给出答案，不要提及"根据文献"、"参考文献"等词汇
2. 将知识库中的信息自然融合，形成连贯的答案
3. 组织答案使其层次分明、易于理解
4. 充分展现知识库中的所有相关信息
5. 不要说"根据我查询的信息"之类的话，直接表述事实
"""
        prompt_parts.append(context_linking)

        # Add final reminder for strict mode (WITHOUT mentioning documents/references)
        if strict_mode:
            if not retrieved_docs:
                reminder = "\n【⚠️ 最终提醒】\n由于知识库中没有相关内容，你必须回答：\"抱歉，我在知识库中没有找到相关信息，无法回答这个问题。\"\n绝对不要使用你的预训练知识来回答！"
                prompt_parts.append(reminder)
            else:
                reminder = "\n【⚠️ 最终提醒】\n1. 只根据上述知识库内容回答，严禁使用预训练知识\n2. 提供详细、充分、高质量的答案\n3. 确保逻辑清晰、层次分明\n4. 直接表述事实，不要提文献\n5. 必须保持100%准确性"
                prompt_parts.append(reminder)

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
