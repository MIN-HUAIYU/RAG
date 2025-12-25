# 🚀 RAG 快速参考指南

快速查找 RAG 功能的使用方法、API 和配置

---

## 快速开始（5 分钟）

```bash
# 1. 安装 RAG 依赖
pip install -r requirements-rag.txt

# 2. 启动应用
python run.py

# 3. 在浏览器打开 http://localhost:8501

# 4. 在侧边栏启用 RAG 并上传文档
```

---

## 核心 API

### BGEEmbeddings

```python
from rag.embeddings import BGEEmbeddings

# 初始化
embeddings = BGEEmbeddings()

# 嵌入单个查询
query_vec = embeddings.embed_query("什么是机器学习?")
# 返回: numpy array (384,)

# 嵌入文档列表
docs = ["文档1", "文档2"]
doc_vecs = embeddings.embed_documents(docs)
# 返回: list of numpy arrays

# 批量嵌入
batch_vecs = embeddings.embed_batch(docs)
# 返回: numpy array (len(docs), 384)
```

### VectorStore

```python
from rag.vector_store import VectorStore

# 初始化
vector_store = VectorStore(persist_directory="./data/chroma_db")

# 添加文档
documents = [
    {"text": "内容1", "source": "file.pdf"},
    {"text": "内容2", "source": "file.pdf"}
]
vector_store.add_documents(documents, embeddings)

# 检索相似文档
results = vector_store.retrieve(
    query="搜索词",
    top_k=3,
    embeddings_manager=embeddings
)
# 返回: [{"text": "...", "source": "...", "score": 0.85}, ...]

# 获取统计信息
stats = vector_store.get_collection_info()
# 返回: {"name": "documents", "document_count": 100, ...}
```

### DocumentProcessor

```python
from rag.document_processor import DocumentProcessor

# 初始化（自定义块大小）
processor = DocumentProcessor(chunk_size=800, chunk_overlap=100)

# 分块文本
chunks = processor.chunk_documents("长文本...")
# 返回: ["块1", "块2", ...]

# 处理单个文件
docs = processor.process_file("path/to/document.pdf")
# 返回: [{"text": "...", "source": "document.pdf", "chunk_id": 0}, ...]

# 批量处理目录
all_docs = processor.process_directory("./documents/")
# 返回: 所有文档的 chunks
```

### RAGRetriever

```python
from rag.retriever import RAGRetriever

# 初始化
retriever = RAGRetriever(vector_store, embeddings)

# 检索文档
docs = retriever.retrieve_context(
    query="用户问题",
    top_k=3
)

# 构建增强 Prompt
prompt = retriever.build_rag_prompt(
    user_query="用户问题",
    retrieved_docs=docs,
    system_prompt="你是一个助手"
)

# 一体化操作
final_prompt, docs = retriever.retrieve_and_build_prompt(
    user_query="用户问题",
    top_k=3,
    system_prompt=None
)
```

---

## 常用配置

### 文档分块参数

```python
# 在 rag/document_processor.py 中修改
processor = DocumentProcessor(
    chunk_size=800,      # 块的大小，值越大包含内容越多
    chunk_overlap=100    # 块之间的重叠，保持上下文连贯
)

# 推荐值:
# - 小文件/精细检索: chunk_size=400
# - 大文件/快速检索: chunk_size=1500
# - 一般情况: chunk_size=800
```

### 检索参数

```python
# 在 app/main.py 中的 render_main() 函数中修改
results = retriever.retrieve_context(
    query=user_input,
    top_k=3  # 检索文档数量
)

# top_k 说明:
# - 1-2: 精准检索，速度快但可能遗漏相关文档
# - 3-5: 均衡模式，推荐值
# - 5+: 全面检索，速度慢但信息全面
```

### 模型选择

```python
# 在 rag/embeddings.py 中修改
embeddings = BGEEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5"  # 384维，快速轻量
    # 可选:
    # model_name="BAAI/bge-base-zh-v1.5"    # 768维，更精准
    # model_name="BAAI/bge-large-zh-v1.5"   # 1024维，最精准但慢
)
```

---

## 文件格式支持

| 格式 | 支持 | 备注 |
|------|------|------|
| PDF | ✅ | 支持文本提取，不支持扫描件 |
| TXT | ✅ | 纯文本，自动编码检测 |
| DOCX | ⏳ | Phase 3 计划 |
| PPTX | ⏳ | Phase 3 计划 |

---

## UI 交互

### 启用 RAG
```
侧边栏 → 📚 知识库管理 → ☑️ 启用知识库检索
```

### 上传文档
```
侧边栏 → 📚 知识库管理 → 上传文档 → ✅ 导入文档
```

### 查看参考文献
```
AI 回复下方 → 📖 相关参考文献 → 展开查看
```

### 查看知识库统计
```
侧边栏 → 📚 知识库管理 → 知识库文档数
```

---

## 命令行使用

### 运行测试
```bash
python test_rag.py
```

### 启动应用
```bash
# 方式 1: 使用启动脚本
python run.py

# 方式 2: 直接使用 streamlit
streamlit run app/main.py

# 方式 3: 指定端口
streamlit run app/main.py --server.port 8888
```

### 导入文档（编程方式）
```python
from rag.document_processor import DocumentProcessor
from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore

processor = DocumentProcessor()
embeddings = BGEEmbeddings()
vector_store = VectorStore()

# 处理文件
documents = processor.process_file("path/to/file.pdf")

# 添加到知识库
vector_store.add_documents(documents, embeddings)

print(f"导入 {len(documents)} 个文档块")
```

---

## 日志位置

| 日志 | 路径 | 内容 |
|------|------|------|
| 应用日志 | `logs/app.log` | 应用运行日志 |
| 向量库日志 | `logs/chroma.log` | ChromaDB 操作 |

### 查看日志
```bash
# 实时查看日志
tail -f logs/app.log

# 查看最近 100 行
tail -100 logs/app.log

# 搜索错误
grep ERROR logs/app.log
```

---

## 性能优化

### 加快初始化

```bash
# 使用 GPU（如果可用）
# 设置环境变量
export CUDA_VISIBLE_DEVICES=0

python run.py
```

### 加快检索

```python
# 方案 1: 减少 top_k
top_k=2  # 而不是 3

# 方案 2: 减小块大小（更多小块可能更快）
chunk_size=400  # 而不是 800

# 方案 3: 使用缓存（Phase 3）
# 即将推出缓存机制
```

### 节省存储

```python
# 删除旧的向量库
from rag.vector_store import VectorStore

vector_store = VectorStore()
vector_store.delete_collection()  # 完全清空
```

---

## 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 模型下载慢 | 配置 HF 镜像源 |
| 内存不足 | 减小 chunk_size |
| 检索结果差 | 增加 top_k 或减小 chunk_overlap |
| PDF 无法提取 | 检查是否为扫描件，改用 TXT |
| 知识库为空 | 检查文件是否导入成功 |

---

## 环境变量

```bash
# .env 文件
DEEPSEEK_API_KEY=sk_xxxxx          # 必需

# 可选
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
APP_DEBUG=false
APP_LOG_LEVEL=INFO
```

---

## 依赖包版本

| 包 | 版本 | 用途 |
|-----|--------|--------|
| sentence-transformers | >=2.2.0 | BGE 向量模型 |
| transformers | >=4.30.0 | 模型框架 |
| chromadb | >=0.3.21 | 向量数据库 |
| langchain | >=0.0.300 | 文本处理 |
| PyPDF2 | >=3.0.1 | PDF 提取 |

---

## 关键文件位置

```
RAG/
├── rag/                    # RAG 模块
│   ├── embeddings.py      # BGEEmbeddings
│   ├── vector_store.py    # VectorStore
│   ├── document_processor.py  # DocumentProcessor
│   └── retriever.py       # RAGRetriever
├── app/main.py            # 主应用（包含 RAG 集成）
├── data/
│   └── chroma_db/         # 向量数据库存储
├── test_rag.py           # 测试脚本
├── requirements-rag.txt  # RAG 依赖
└── README.md             # 完整文档
```

---

## 代码示例

### 完整 RAG 工作流

```python
#!/usr/bin/env python
"""完整 RAG 工作流示例"""

from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore
from rag.document_processor import DocumentProcessor
from rag.retriever import RAGRetriever
from app.services import DeepSeekService

# 1. 初始化所有组件
embeddings = BGEEmbeddings()
vector_store = VectorStore()
processor = DocumentProcessor()
retriever = RAGRetriever(vector_store, embeddings)

# 2. 处理文档
documents = processor.process_file("path/to/document.pdf")

# 3. 添加到知识库
vector_store.add_documents(documents, embeddings)
print(f"✅ 导入 {len(documents)} 个文档块")

# 4. 用户提问
user_query = "根据文档，主要内容是什么？"

# 5. 检索并构建 Prompt
final_prompt, retrieved_docs = retriever.retrieve_and_build_prompt(
    user_query=user_query,
    top_k=3
)

# 6. 调用 DeepSeek API
service = DeepSeekService(
    api_key="your_api_key",
    model="deepseek-chat"
)

# 7. 流式获取回复
print("\n📖 相关文献:")
for i, doc in enumerate(retrieved_docs, 1):
    print(f"{i}. [{doc['source']}] 相关度: {doc['score']:.1%}")

print("\n🤖 AI 回复:")
for chunk in service.stream_chat(final_prompt):
    print(chunk, end="", flush=True)
```

---

## 最佳实践

### ✅ 文档管理

- 定期更新文档
- 使用清晰的文件名
- 在 TXT 中添加元数据注释
- 保持文档格式一致

### ✅ 检索优化

- 根据应用调整 chunk_size
- 监控检索准确率
- 定期检查知识库统计
- 清理重复或过时内容

### ✅ 性能优化

- 使用 Conda 环境避免编译问题
- 监控内存使用
- 定期重启应用（可选）
- 使用 GPU 加速（如果可用）

### ✅ 安全实践

- 不要暴露 API 密钥
- 定期备份知识库数据
- 限制文件上传大小
- 审计敏感文档访问

---

## 更新和维护

### 更新依赖
```bash
pip install --upgrade -r requirements-rag.txt
```

### 备份知识库
```bash
cp -r data/chroma_db data/chroma_db.backup.$(date +%Y%m%d)
```

### 重置知识库
```python
from rag.vector_store import VectorStore

vector_store = VectorStore()
vector_store.delete_collection()
# 知识库已清空
```

---

**最后更新**: 2025-12-25
**版本**: v0.2.0
