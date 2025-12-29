"""ChromaDB vector store for document embeddings storage and retrieval."""

import os
import chromadb
from loguru import logger


class VectorStore:
    """
    Vector store using ChromaDB for efficient document storage and retrieval.

    Supports:
    - Adding documents with embeddings
    - Similarity search for query retrieval
    - Persistent storage with SQLite
    """

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_directory: Path to persist ChromaDB data
        """
        # Create directory if not exists
        os.makedirs(persist_directory, exist_ok=True)

        logger.info(f"Initializing ChromaDB with persist_directory: {persist_directory}")

        # Use new ChromaDB API (0.4.0+)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection for documents
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Collection initialized. Current documents: {self.collection.count()}")

    def add_documents(self, documents: list, embeddings_manager):
        """
        Add documents with their embeddings to the vector store.

        Args:
            documents: List of document dicts with 'text', 'source' (optional), 'chunk_id' (optional)
            embeddings_manager: BGEEmbeddings instance for generating embeddings

        Example:
            docs = [
                {"text": "Machine learning is a subset of AI", "source": "paper1.pdf"},
                {"text": "Deep learning uses neural networks", "source": "paper1.pdf"}
            ]
            vector_store.add_documents(docs, embeddings_manager)
        """
        if not documents:
            logger.warning("No documents to add")
            return

        ids = []
        texts = []
        embeddings_list = []
        metadatas = []

        logger.info(f"Processing {len(documents)} documents...")

        for idx, doc in enumerate(documents):
            doc_id = f"doc_{idx}_{id(doc)}"  # Unique ID
            text = doc.get("text", "")

            if not text:
                logger.warning(f"Document {idx} has empty text, skipping")
                continue

            # Generate embedding
            embedding = embeddings_manager.embed_documents([text])[0]

            # Prepare metadata
            metadata = {
                "source": doc.get("source", "unknown"),
                "chunk_id": doc.get("chunk_id", 0),
            }

            ids.append(doc_id)
            texts.append(text)
            embeddings_list.append(embedding.tolist())
            metadatas.append(metadata)

        # Add to collection
        if ids:
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings_list,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} documents to vector store")
        else:
            logger.warning("No valid documents to add")

    def retrieve(self, query: str, top_k: int = 3, embeddings_manager=None, similarity_threshold: float = 0.01) -> list:
        """
        Retrieve top-k most similar documents for a query.
        使用向量检索 + 关键词匹配双重策略。

        Args:
            query: Query text
            top_k: Number of top results to retrieve (default: 3)
            embeddings_manager: BGEEmbeddings instance for query embedding
            similarity_threshold: Minimum similarity score (default: 0.01)

        Returns:
            List of retrieved documents with scores
        """
        if not embeddings_manager:
            logger.error("embeddings_manager is required")
            return []

        # Check if collection has documents
        doc_count = self.collection.count()
        if doc_count == 0:
            logger.warning("Vector store is empty, no documents to retrieve")
            return []

        logger.info(f"🔍 检索查询: '{query}', 知识库文档数: {doc_count}")

        retrieved = []

        # 策略1: 关键词匹配（优先）
        keyword_results = self._keyword_search(query, top_k * 2)
        if keyword_results:
            logger.info(f"✅ 关键词匹配找到 {len(keyword_results)} 个结果")
            retrieved.extend(keyword_results)

        # 策略2: 向量检索
        try:
            query_embedding = embeddings_manager.embed_query(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k * 2, doc_count),
                include=["documents", "distances", "metadatas"]
            )

            if results["documents"] and results["documents"][0]:
                for doc, distance, metadata in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0]
                ):
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        # 检查是否已经在结果中
                        if not any(r["text"] == doc for r in retrieved):
                            retrieved.append({
                                "text": doc,
                                "source": metadata.get("source", "unknown"),
                                "chunk_id": metadata.get("chunk_id", 0),
                                "score": round(similarity, 4)
                            })
                logger.info(f"✅ 向量检索完成，当前结果数: {len(retrieved)}")
        except Exception as e:
            logger.warning(f"向量检索失败: {e}")

        # 按分数排序，取 top_k
        retrieved.sort(key=lambda x: x["score"], reverse=True)
        retrieved = retrieved[:top_k]

        logger.info(f"📚 最终检索结果: {len(retrieved)} 个文档")
        for idx, doc in enumerate(retrieved, 1):
            logger.debug(f"  [{idx}] {doc['source']} - 相关度: {doc['score']:.2%}")

        return retrieved

    def _keyword_search(self, query: str, top_k: int = 5) -> list:
        """
        关键词匹配搜索 - 直接在文档中搜索查询关键词
        """
        try:
            # 获取所有文档
            all_docs = self.collection.get(
                limit=self.collection.count(),
                include=["documents", "metadatas"]
            )

            if not all_docs["documents"]:
                return []

            results = []
            query_lower = query.lower()

            for doc, metadata in zip(all_docs["documents"], all_docs["metadatas"]):
                doc_lower = doc.lower()

                # 计算关键词匹配分数
                score = 0

                # 完整查询匹配
                if query in doc:
                    score = 0.95

                # 查询词在文档中
                elif query_lower in doc_lower:
                    score = 0.9

                # 分词匹配（每个字符）
                else:
                    matched_chars = sum(1 for char in query if char in doc)
                    if matched_chars > 0:
                        score = matched_chars / len(query) * 0.8

                if score > 0.3:  # 至少匹配30%
                    results.append({
                        "text": doc,
                        "source": metadata.get("source", "unknown"),
                        "chunk_id": metadata.get("chunk_id", 0),
                        "score": round(score, 4)
                    })

            # 按分数排序
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.warning(f"关键词搜索失败: {e}")
            return []

    def delete_collection(self, collection_name: str = "documents"):
        """
        Delete entire collection (useful for reset).

        Args:
            collection_name: Name of collection to delete
        """
        logger.warning(f"Deleting collection: {collection_name}")
        self.client.delete_collection(name=collection_name)
        # Recreate empty collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def get_collection_info(self) -> dict:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection metadata and statistics
        """
        return {
            "name": self.collection.name,
            "document_count": self.collection.count(),
            "metadata": self.collection.metadata
        }
