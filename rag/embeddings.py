"""BGE Embeddings module for generating vector representations of text."""

import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger


class BGEEmbeddings:
    """
    BGE (BAAI General Embeddings) embeddings for Chinese text.

    Uses BAAI/bge-small-zh-v1.5 model for efficient text embedding.
    Embedding dimension: 384
    """

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        Initialize BGE embeddings model.

        Args:
            model_name: HuggingFace model name. Default: BAAI/bge-small-zh-v1.5
        """
        logger.info(f"Loading BGE model: {model_name}")
        try:
            # 使用 device='cpu' 避免 CUDA/meta tensor 问题
            self.model = SentenceTransformer(model_name, device='cpu')
            self.dimension = 384
            logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"BGE model loading failed: {e}") from e

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query with special prefix for query representation.

        BGE model expects query prefix for better retrieval performance.

        Args:
            query: Query text to embed

        Returns:
            Normalized embedding as numpy array (shape: 384,)
        """
        # Add instruction prefix for queries as per BGE documentation
        query_with_prefix = f"Represent this sentence: {query}"

        embedding = self.model.encode(
            query_with_prefix,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding

    def embed_documents(self, texts: list) -> list:
        """
        Embed multiple documents with document prefix.

        BGE model expects document prefix for better embedding quality.

        Args:
            texts: List of document texts to embed

        Returns:
            List of normalized embeddings as numpy arrays
        """
        embeddings = []
        for text in texts:
            # Add instruction prefix for documents
            doc_with_prefix = f"Represent this document: {text}"

            embedding = self.model.encode(
                doc_with_prefix,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            embeddings.append(embedding)

        logger.debug(f"Embedded {len(texts)} documents")
        return embeddings

    def embed_batch(self, texts: list) -> np.ndarray:
        """
        Efficiently embed multiple texts in batch mode.

        Args:
            texts: List of texts to embed

        Returns:
            Array of embeddings (shape: [len(texts), 384])
        """
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings
