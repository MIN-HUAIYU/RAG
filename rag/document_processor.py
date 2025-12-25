"""Document processing module for text extraction and chunking."""

import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger


class DocumentProcessor:
    """
    Process documents by extracting text and splitting into chunks.

    Supports:
    - Text files (.txt)
    - PDF files (.pdf)
    - Automatic text chunking with overlap
    """

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 150):
        """
        Initialize document processor with optimized settings for better knowledge extraction.

        Args:
            chunk_size: Size of each text chunk (default: 600 - optimized for better granularity)
            chunk_overlap: Overlap between chunks for context continuity (default: 150 - ensures context preservation)

        Note:
            - Reduced chunk_size from 800 to 600 to prevent splitting important information
            - Increased overlap from 100 to 150 to ensure context continuity across chunks
            - This helps preserve relationships between related concepts
        """
        logger.info(f"Initializing DocumentProcessor (chunk_size={chunk_size}, overlap={chunk_overlap})")
        logger.info("✨ 优化配置：更小的块尺寸和更大的重叠，确保知识完整性")

        # Initialize text splitter with optimized Chinese-aware separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "，", "；", "：", " ", ""]  # Enhanced Chinese separators
        )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, text: str) -> list:
        """
        Split text into chunks.

        Args:
            text: Raw text to split

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []

        chunks = self.text_splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks

    def _extract_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.error("PyPDF2 not installed. Install it with: pip install PyPDF2")
            raise ImportError("PyPDF2 is required for PDF processing")

        logger.info(f"Extracting text from PDF: {file_path}")

        try:
            reader = PdfReader(file_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                else:
                    logger.warning(f"No text extracted from page {page_num}")

            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {len(reader.pages)} pages")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise

    def _extract_txt(self, file_path: str) -> str:
        """
        Extract text from text file.

        Args:
            file_path: Path to text file

        Returns:
            File content as string
        """
        logger.info(f"Reading text file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Read {len(text)} characters from file")
            return text
        except UnicodeDecodeError:
            # Try alternative encoding
            logger.warning("UTF-8 decode failed, trying GBK encoding")
            with open(file_path, 'r', encoding='gbk') as f:
                text = f.read()
            return text
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise

    def process_file(self, file_path: str) -> list:
        """
        Process a single document file (PDF or TXT).

        Args:
            file_path: Path to file

        Returns:
            List of document chunks with metadata:
            [
                {
                    "text": "chunk content",
                    "source": "filename.pdf",
                    "chunk_id": 0
                },
                ...
            ]

        Raises:
            ValueError: If file format not supported
            FileNotFoundError: If file does not exist
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        file_ext = file_path_obj.suffix.lower()

        logger.info(f"Processing file: {file_name}")

        # Extract text based on file type
        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.txt':
            text = self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported: .pdf, .txt")

        # Split into chunks
        chunks = self.chunk_documents(text)

        # Create document objects with metadata
        documents = []
        for idx, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "source": file_name,
                "chunk_id": idx
            })

        logger.info(f"File processing complete. Created {len(documents)} chunks from {file_name}")
        return documents

    def process_directory(self, directory: str, file_extensions: list = None) -> list:
        """
        Process all documents in a directory.

        Args:
            directory: Path to directory containing files
            file_extensions: List of file extensions to process (default: ['.pdf', '.txt'])

        Returns:
            Combined list of all document chunks from all files
        """
        if file_extensions is None:
            file_extensions = ['.pdf', '.txt']

        logger.info(f"Processing directory: {directory}")

        all_documents = []
        directory_path = Path(directory)

        if not directory_path.exists():
            logger.error(f"Directory not found: {directory}")
            return []

        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    docs = self.process_file(str(file_path))
                    all_documents.extend(docs)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    continue

        logger.info(f"Directory processing complete. Total documents: {len(all_documents)}")
        return all_documents
