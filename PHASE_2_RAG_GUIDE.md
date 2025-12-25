# 📚 第二阶段：RAG 系统集成指南

## 现状总结

✅ **第一阶段完成！**
- 基础对话系统已运行
- DeepSeek API 集成成功
- 流式输出工作正常

⏳ **第二阶段任务**
- 集成 BGE-Small-zh-v1.5 向量模型
- 集成 ChromaDB 知识库
- 实现文档上传和检索

---

## 环境问题说明

你的 Windows 环境缺少 C++ 编译工具，导致某些 Python 包（如 numpy、tokenizers）无法编译。

### 解决方案（三选一）

#### 方案 A：安装 Visual C++ Build Tools（推荐）
1. 下载 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. 安装时选择"Desktop development with C++"
3. 重启计算机
4. 重新安装依赖：
   ```bash
   python -m pip install -r requirements-rag.txt
   ```

#### 方案 B：使用 Miniconda/Conda（最简单）
Conda 提供预编译的 wheel 文件，避免编译问题。

1. 安装 [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
2. 创建新环境：
   ```bash
   conda create -n rag python=3.11
   conda activate rag
   pip install -r requirements.txt
   ```
3. 所有包会自动下载预编译版本

#### 方案 C：使用 Google Colab（无需本地安装）
在 Google Colab 中运行应用，完全避免本地环境问题。

```python
# 在 Colab notebook 中
!git clone https://github.com/你的用户名/RAG
%cd RAG
!pip install -r requirements.txt
!python demo.py
```

---

## Phase 2 实现步骤

### 步骤 1️⃣：创建 RAG 模块结构

创建以下文件和目录：

```bash
mkdir -p rag/{embeddings,vector_store,processors}
touch rag/__init__.py
touch rag/embeddings.py
touch rag/vector_store.py
touch rag/document_processor.py
touch rag/retriever.py
```

### 步骤 2️⃣：实现 BGE 嵌入模块

**文件：`rag/embeddings.py`**

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class BGEEmbeddings:
    def __init__(self, model_name="BAAI/bge-small-zh-v1.5"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384

    def embed_query(self, query: str) -> np.ndarray:
        """对查询进行特殊处理"""
        query = f"Represent this sentence: {query}"
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding

    def embed_documents(self, texts: list) -> list:
        """对文档进行嵌入"""
        embeddings = []
        for text in texts:
            doc_text = f"Represent this document: {text}"
            embedding = self.model.encode(
                doc_text,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            embeddings.append(embedding)
        return embeddings
```

### 步骤 3️⃣：实现 ChromaDB 向量存储

**文件：`rag/vector_store.py`**

```python
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False
        )

        self.client = chromadb.Client(settings)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: list, embeddings_manager):
        """添加文档到向量库"""
        ids = []
        texts = []
        embeddings_list = []

        for idx, doc in enumerate(documents):
            doc_id = f"doc_{idx}"
            text = doc["text"]

            embedding = embeddings_manager.embed_documents([text])[0]

            ids.append(doc_id)
            texts.append(text)
            embeddings_list.append(embedding.tolist())

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings_list
        )

    def retrieve(self, query: str, top_k: int = 3, embeddings_manager = None):
        """检索相关文档"""
        query_embedding = embeddings_manager.embed_query(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "distances"]
        )

        retrieved = []
        if results["documents"]:
            for doc, distance in zip(results["documents"][0], results["distances"][0]):
                similarity = 1 - distance
                retrieved.append({
                    "text": doc,
                    "score": round(similarity, 3)
                })

        return retrieved
```

### 步骤 4️⃣：实现文档处理器

**文件：`rag/document_processor.py`**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )

    def chunk_documents(self, text: str) -> list:
        """文本分块"""
        chunks = self.text_splitter.split_text(text)
        return chunks

    def process_file(self, file_path: str) -> list:
        """处理文件"""
        # 根据文件类型提取文本
        if file_path.endswith('.pdf'):
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages])
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        # 分块
        chunks = self.chunk_documents(text)

        # 返回文档对象
        documents = []
        for idx, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "source": file_path,
                "chunk_id": idx
            })

        return documents
```

### 步骤 5️⃣：集成到主应用

在 `app/main.py` 中添加：

```python
# 导入 RAG 模块
from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.document_processor import DocumentProcessor

# 在 initialize_app() 中初始化
if "embeddings_manager" not in st.session_state:
    st.session_state.embeddings_manager = BGEEmbeddings()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()

if "doc_processor" not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
```

### 步骤 6️⃣：添加文件上传功能

在 `app/main.py` 的侧边栏添加：

```python
# 知识库管理
st.sidebar.markdown("### 📚 知识库管理")

uploaded_file = st.sidebar.file_uploader(
    "上传文档 (PDF/TXT)",
    type=["pdf", "txt"],
    help="上传文档以增强对话能力"
)

if uploaded_file:
    st.sidebar.info(f"📄 已上传: {uploaded_file.name}")

    # 处理文件
    with st.spinner("正在处理文档..."):
        temp_path = f"./data/documents/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 提取和分块
        documents = st.session_state.doc_processor.process_file(temp_path)

        # 添加到向量库
        st.session_state.vector_store.add_documents(
            documents,
            st.session_state.embeddings_manager
        )

        st.sidebar.success(f"✅ 已导入 {len(documents)} 个文档块")
```

### 步骤 7️⃣：修改 RAG 对话逻辑

在处理用户输入时：

```python
if user_input:
    chat_interface.add_message("user", user_input)

    # 1. 检索相关文档
    retrieved = st.session_state.vector_store.retrieve(
        user_input,
        top_k=3,
        embeddings_manager=st.session_state.embeddings_manager
    )

    # 2. 构建 RAG Prompt
    context = ""
    if retrieved:
        context = "【相关知识】\n"
        for item in retrieved:
            context += f"- {item['text'][:200]}...\n"

    # 3. 合并 prompt
    final_prompt = f"{context}\n\n用户问题：{user_input}"

    # 4. 获取回复
    response = service.stream_chat(final_prompt)
```

---

## 依赖安装

创建 `requirements-rag.txt`：

```
# Phase 2 RAG 依赖
sentence-transformers>=2.2.0
transformers>=4.30.0
chromadb>=0.3.21
langchain>=0.0.300
PyPDF2>=3.0.1
```

安装：

```bash
python -m pip install -r requirements-rag.txt
```

---

## 测试 RAG 系统

创建 `test_rag.py`：

```python
from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.document_processor import DocumentProcessor

# 初始化
embeddings = BGEEmbeddings()
vector_store = VectorStore()
processor = DocumentProcessor()

# 测试文档处理
test_text = "机器学习是人工智能的重要分支..."
chunks = processor.chunk_documents(test_text)

# 添加到向量库
docs = [{"text": chunk} for chunk in chunks]
vector_store.add_documents(docs, embeddings)

# 测试检索
results = vector_store.retrieve("什么是机器学习", embeddings_manager=embeddings)
print(results)
```

---

## 完整的实施时间表

| 任务 | 时间 | 复杂度 |
|------|------|--------|
| 安装环境 | 1 天 | ⭐ |
| 实现 BGE 模块 | 1 天 | ⭐⭐ |
| 实现 ChromaDB 模块 | 1 天 | ⭐⭐ |
| 实现文档处理 | 1 天 | ⭐⭐ |
| 集成到主应用 | 1 天 | ⭐⭐⭐ |
| 测试和优化 | 2 天 | ⭐⭐ |
| **总计** | **7 天** | |

---

## 常见问题

### Q1: 模型下载很慢怎么办？

配置 HuggingFace 镜像源：

```bash
export HF_ENDPOINT=https://huggingface.co

# 或在代码中
import os
os.environ['HF_ENDPOINT'] = 'https://huggingface.co'
```

### Q2: 向量库占用空间太大？

调整参数：
- `chunk_size`: 减小块大小
- `chunk_overlap`: 减小重叠
- 只保存重要文档

### Q3: 检索速度慢？

优化策略：
- 增加 `top_k` 值
- 使用缓存
- 定期清理旧数据

---

## 下一步选项

选择你想继续的方向：

1. **立即实现** - 如果你已安装 Visual C++ Build Tools
2. **使用 Conda** - 更简单的环境管理
3. **Google Colab** - 云端开发，无需本地配置

告诉我你的选择，我会提供详细指导！

---

最后更新: 2025-12-25
