"""BGE Embeddings module for generating vector representations of text."""

import os
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger

# 离线模式：尝试从本地缓存或使用预下载的模型
# 设置 transformers 和 sentence-transformers 的缓存目录
os.environ['HF_HOME'] = os.path.expanduser('~/.cache/huggingface')
os.environ['SENTENCE_TRANSFORMERS_HOME'] = os.path.expanduser('~/.cache/sentence-transformers')

# 禁用网络检查，使用本地缓存
os.environ['HF_DATASETS_OFFLINE'] = '0'
os.environ['TRANSFORMERS_OFFLINE'] = '0'


class BGEEmbeddings:
    """
    BGE (BAAI General Embeddings) embeddings for Chinese text.

    在网络不可用时，自动降级到 TF-IDF 方案。
    """

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", offline_mode: bool = True, vector_store=None):
        """
        Initialize embeddings model with fallback to TF-IDF.

        Args:
            model_name: HuggingFace model name. Default: BAAI/bge-small-zh-v1.5
            offline_mode: If True, prefer simple offline methods
            vector_store: Optional VectorStore instance for fitting TF-IDF
        """
        logger.info(f"初始化嵌入模型 (offline_mode={offline_mode})")

        # 首先尝试加载神经网络模型
        model_loaded = False
        if not offline_mode:
            try:
                logger.info(f"尝试加载 {model_name}...")
                self.model = SentenceTransformer(
                    model_name,
                    device='cpu',
                    cache_folder=os.path.expanduser('~/.cache/sentence-transformers')
                )
                self.dimension = 384
                self.use_neural = True
                model_loaded = True
                logger.info(f"✅ {model_name} 加载成功")
            except Exception as e:
                logger.warning(f"神经网络模型加载失败: {e}")

        # 如果神经网络模型加载失败，使用 TF-IDF
        if not model_loaded:
            logger.info("降级到 TF-IDF 嵌入方案（完全离线）...")
            from rag.embeddings_simple import SimpleEmbeddings
            self.model = SimpleEmbeddings()
            self.dimension = 5000  # TF-IDF 维度
            self.use_neural = False
            logger.info("✅ TF-IDF 嵌入已就绪")

            # 如果提供了 vector_store，自动使用知识库文档训练 TF-IDF
            if vector_store:
                self._fit_from_vector_store(vector_store)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query.

        Args:
            query: Query text to embed

        Returns:
            Embedding as numpy array
        """
        if self.use_neural:
            # 神经网络模型
            query_with_prefix = f"Represent this sentence: {query}"
            embedding = self.model.encode(
                query_with_prefix,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
        else:
            # TF-IDF 模型
            embedding = self.model.embed_query(query)
        return embedding

    def embed_documents(self, texts: list) -> list:
        """
        Embed multiple documents.

        Args:
            texts: List of document texts to embed

        Returns:
            List of embeddings as numpy arrays
        """
        if self.use_neural:
            # 神经网络模型
            embeddings = []
            for text in texts:
                doc_with_prefix = f"Represent this document: {text}"
                embedding = self.model.encode(
                    doc_with_prefix,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
                embeddings.append(embedding)
        else:
            # TF-IDF 模型
            embeddings = self.model.embed_documents(texts)

        logger.debug(f"嵌入了 {len(texts)} 个文档")
        return embeddings

    def embed_batch(self, texts: list) -> np.ndarray:
        """
        Efficiently embed multiple texts in batch mode.

        Args:
            texts: List of texts to embed

        Returns:
            Array of embeddings
        """
        if self.use_neural:
            # 神经网络模型
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
        else:
            # TF-IDF 模型
            embeddings = self.model.embed_batch(texts)
        return embeddings

    def _fit_from_vector_store(self, vector_store):
        """
        Fit TF-IDF model using documents from vector store.

        Args:
            vector_store: VectorStore instance containing documents
        """
        if self.use_neural:
            return  # Neural models don't need fitting

        try:
            doc_count = vector_store.collection.count()
            if doc_count == 0:
                logger.warning("⚠️ 知识库为空，跳过 TF-IDF 训练")
                return

            logger.info(f"📚 从知识库加载 {doc_count} 个文档用于训练 TF-IDF...")

            # Get all documents from vector store
            results = vector_store.collection.get(
                limit=doc_count,
                include=['documents']
            )

            if results and results['documents']:
                texts = results['documents']
                logger.info(f"开始训练 TF-IDF 模型 ({len(texts)} 个文档)...")
                self.model.fit(texts)
                logger.info("✅ TF-IDF 模型训练完成，现在可以进行检索了")
            else:
                logger.warning("⚠️ 无法从知识库获取文档")

        except Exception as e:
            logger.error(f"❌ TF-IDF 训练失败: {e}")
