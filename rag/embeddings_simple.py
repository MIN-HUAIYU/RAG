"""简单的 TF-IDF 嵌入模块 - 无需网络，完全离线"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger
import pickle
import os
import re


def chinese_tokenizer(text):
    """
    简单的中文分词器 - 按字符和词组分割
    """
    # 提取中文字符序列
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    tokens = []
    for word in chinese_chars:
        # 添加整词
        tokens.append(word)
        # 添加单字
        for char in word:
            tokens.append(char)
        # 添加双字组合
        for i in range(len(word) - 1):
            tokens.append(word[i:i+2])
        # 添加三字组合
        for i in range(len(word) - 2):
            tokens.append(word[i:i+3])
    return tokens


class SimpleEmbeddings:
    """
    基于 TF-IDF 的简单嵌入，无需外部模型，完全离线运行。
    针对中文优化，支持人名、地名等实体检索。
    """

    def __init__(self, max_features: int = 10000):
        """
        初始化 TF-IDF 向量化器（中文优化版）

        Args:
            max_features: 最大特征数
        """
        logger.info("初始化 SimpleEmbeddings (TF-IDF 中文优化版)")
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            tokenizer=chinese_tokenizer,
            token_pattern=None,  # 使用自定义分词器
            min_df=1,
            max_df=0.95,
            ngram_range=(1, 2)
        )
        self.dimension = max_features
        self.is_fitted = False
        self.corpus_texts = []  # 保存原始文本用于关键词匹配
        logger.info(f"✅ SimpleEmbeddings 初始化完成 (维度: {self.dimension})")

    def fit(self, texts: list):
        """
        拟合 TF-IDF 向量化器

        Args:
            texts: 文本列表
        """
        logger.info(f"拟合 TF-IDF 向量化器 ({len(texts)} 个文本)...")
        self.corpus_texts = texts  # 保存原始文本
        self.vectorizer.fit(texts)
        self.is_fitted = True
        logger.info("✅ TF-IDF 向量化器拟合完成")

    def embed_query(self, query: str) -> np.ndarray:
        """
        嵌入查询文本

        Args:
            query: 查询文本

        Returns:
            嵌入向量 (numpy array)
        """
        if not self.is_fitted:
            logger.warning("向量化器未拟合，返回零向量")
            return np.zeros(self.dimension)

        vector = self.vectorizer.transform([query]).toarray()[0]
        # 将向量填充到固定维度
        if len(vector) < self.dimension:
            vector = np.pad(vector, (0, self.dimension - len(vector)), 'constant')
        return vector.astype(np.float32)

    def embed_documents(self, texts: list) -> list:
        """
        嵌入多个文档

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings

    def embed_batch(self, texts: list) -> np.ndarray:
        """
        批量嵌入文本

        Args:
            texts: 文本列表

        Returns:
            嵌入矩阵 (numpy array)
        """
        if not self.is_fitted:
            vectors = np.zeros((len(texts), self.dimension))
            return vectors

        vectors = self.vectorizer.transform(texts).toarray()
        # 填充到固定维度
        if vectors.shape[1] < self.dimension:
            vectors = np.pad(
                vectors,
                ((0, 0), (0, self.dimension - vectors.shape[1])),
                'constant'
            )
        return vectors.astype(np.float32)
