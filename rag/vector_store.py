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

    def retrieve(self, query: str, top_k: int = 3, embeddings_manager=None, similarity_threshold: float = 0.3) -> list:
        """
        Retrieve top-k most similar documents for a query.

        Supports both semantic search and fuzzy matching for better knowledge discovery.

        Args:
            query: Query text
            top_k: Number of top results to retrieve (default: 3)
            embeddings_manager: BGEEmbeddings instance for query embedding
            similarity_threshold: Minimum similarity score (default: 0.3 for fuzzy matching)

        Returns:
            List of retrieved documents with scores:
            [
                {"text": "...", "source": "...", "score": 0.85},
                ...
            ]
        """
        if not embeddings_manager:
            logger.error("embeddings_manager is required")
            return []

        # Check if collection has documents
        doc_count = self.collection.count()
        if doc_count == 0:
            logger.warning("Vector store is empty, no documents to retrieve")
            return []

        # Generate query embedding
        query_embedding = embeddings_manager.embed_query(query).tolist()

        # Query with lower threshold initially to capture more results
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 2, doc_count),  # Retrieve more to filter
            include=["documents", "distances", "metadatas"]
        )

        # Process results with threshold filtering
        retrieved = []
        if results["documents"] and results["documents"][0]:
            for doc, distance, metadata in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0]
            ):
                # Convert distance to similarity (cosine distance to similarity)
                similarity = 1 - distance

                # Include results above threshold
                if similarity >= similarity_threshold:
                    retrieved.append({
                        "text": doc,
                        "source": metadata.get("source", "unknown"),
                        "chunk_id": metadata.get("chunk_id", 0),
                        "score": round(similarity, 4)
                    })

            # Keep only top_k results
            retrieved = retrieved[:top_k]

        logger.debug(f"Retrieved {len(retrieved)} documents for query (threshold: {similarity_threshold})")
        return retrieved

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
