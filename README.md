# 🤖 DeepSeek AI 对话系统

一个基于 DeepSeek API 和 Streamlit 的智能对话应用，支持流式输出和实时交互。后续将集成 RAG（检索增强生成）技术，使用 BGE-Small-zh-v1.5 向量模型和 ChromaDB 知识库。

## ✨ 功能特性

### 第一阶段（已完成）
- ✅ 实时对话界面（基于 Streamlit）
- ✅ 流式输出 AI 回复
- ✅ 对话历史管理
- ✅ 可配置的对话参数（温度、最大令牌数）
- ✅ 错误处理和日志记录
- ✅ 安全的 API 密钥管理

### 第二阶段（✅ 已完成）
- ✅ BGE-Small-zh-v1.5 向量模型集成
- ✅ ChromaDB 知识库
- ✅ 文档上传和处理
- ✅ 相关文档检索
- ✅ RAG 增强对话
- ✅ **严格模式：强制使用本地知识库（推荐）**

---

## 📋 项目结构

```
RAG/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Streamlit 主应用
│   ├── config.py                # 配置管理
│   ├── services/
│   │   ├── __init__.py
│   │   └── deepseek_service.py  # DeepSeek API 服务
│   └── components/
│       ├── __init__.py
│       └── chat_ui.py           # 聊天界面组件
├── rag/                         # RAG 模块（Phase 2）
│   ├── __init__.py
│   ├── embeddings.py            # BGE 向量嵌入模块
│   ├── vector_store.py          # ChromaDB 向量存储
│   ├── document_processor.py    # 文档处理和分块
│   └── retriever.py             # RAG 检索协调器
├── data/
│   ├── documents/               # 文档存储
│   └── chroma_db/              # 向量数据库
├── logs/                        # 日志目录
├── .streamlit/
│   └── config.toml             # Streamlit 配置
├── .env.example                 # 环境变量示例
├── requirements.txt             # 基础依赖（Phase 1）
├── requirements-rag.txt         # RAG 依赖（Phase 2）
├── .gitignore                   # Git 忽略配置
├── run.py                       # 启动脚本
├── test_rag.py                 # RAG 测试脚本
└── README.md                    # 项目文档
```

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.9 或更高版本
- pip 或 conda 包管理器

### 2. 安装依赖

```bash
# 克隆或进入项目目录
cd RAG

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API 密钥

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API 密钥
# DEEPSEEK_API_KEY=your_api_key_here
```

### 4. 启动应用

```bash
# 方法 1: 使用启动脚本
python run.py

# 方法 2: 直接使用 streamlit
streamlit run app/main.py
```

应用将在 `http://localhost:8501` 打开

---

## 📖 使用说明

### 基础对话
1. 在聊天输入框输入你的问题或指令
2. 应用会实时流式展示 AI 的回复
3. 对话历史会自动保存在当前会话中

### 调整对话参数
在左侧边栏可以调整以下参数：
- **温度 (Temperature)**: 0.0-2.0
  - 值越小（如 0.3）：回复越确定、越专业
  - 值越大（如 1.5）：回复越随机、越创意
- **最大令牌数**: 100-4000
  - 控制单次回复的长度

### 管理对话
- 点击侧边栏的"清空对话"按钮可以清除所有历史记录
- 当前对话消息数显示在侧边栏

### RAG 知识库管理（Phase 2 新增）📚

#### 📤 上传文档
主页面顶部有一个醒目的"📚 知识库管理"区域：
1. 点击或拖拽选择 PDF/TXT 文件
2. 点击 **"🚀 立即上传"** 绿色大按钮
3. 查看实时进度条（0% → 100%）
4. 看到"✅ 成功导入 X 个文档块"提示

#### 🔍 启用 RAG 检索
在左侧边栏"📚 知识库"部分：
1. 勾选 "启用 RAG 检索" 开关（默认开启）
2. 勾选 "🔒 严格模式（仅知识库）"开关（**推荐开启**）
3. 查看知识库中的文档块数
4. 如果知识库为空，会提示"请上传文档"

**严格模式说明**：
- ✅ 开启后，AI 只能根据上传的文档回答，不使用预训练知识
- ✅ 确保答案 100% 来自您的本地知识库
- ✅ 知识库为空时会阻止提问，要求先上传文档
- 📖 详细说明请查看 [STRICT_MODE_GUIDE.md](STRICT_MODE_GUIDE.md)

#### 💬 使用知识库对话
启用 RAG 后，在对话时：
1. AI 会从知识库自动检索最相关的 3 个文档块
2. 在AI回复下方显示"📖 相关参考文献"
3. 可以展开查看具体的相关内容和相关度分数

#### 🗑️ 管理知识库
- **查看统计**：侧边栏显示文档块数
- **清空知识库**：知识库管理区点击"🗑️ 清空知识库"按钮
- **查看使用提示**：展开"💡 使用提示"了解详细说明

**详细教程**: 查看 [KNOWLEDGE_BASE_SETUP.md](KNOWLEDGE_BASE_SETUP.md)

#### 知识库统计
侧边栏显示当前知识库中存储的文档块数量

---

## 🚀 RAG 功能使用指南（Phase 2）

### 安装 RAG 依赖

```bash
# 安装 RAG 相关依赖
pip install -r requirements-rag.txt

# 或使用 Conda（推荐，避免编译问题）
conda create -n rag python=3.11
conda activate rag
pip install -r requirements.txt
pip install -r requirements-rag.txt
```

### 首次运行

首次启动应用时，RAG 模块会自动初始化：
1. 加载 BGE 向量模型（~400MB，首次需要下载）
2. 初始化 ChromaDB 向量存储
3. 创建 `data/chroma_db/` 目录

### 使用工作流

```
1. 启动应用
   python run.py

2. 在侧边栏启用 RAG
   ☑️ 启用知识库检索

3. 上传文档
   📄 选择 PDF/TXT 文件
   ✅ 点击"导入文档"

4. 提问并获取 RAG 增强回复
   输入问题 → 自动检索相关文档 → 显示"相关参考文献"
```

### 测试 RAG 系统

```bash
# 运行 RAG 系统测试
python test_rag.py

# 测试内容：
# - BGEEmbeddings 模块
# - VectorStore 向量存储
# - DocumentProcessor 文档处理
# - RAGRetriever 检索功能
```

### 配置 RAG 参数

编辑 `rag/document_processor.py` 中的参数：

```python
# 文档分块参数
chunk_size=800      # 每个块的大小
chunk_overlap=100   # 块之间的重叠
```

编辑 `app/main.py` 中的检索参数：

```python
# 检索参数
top_k=3             # 检索最多 N 个相关文档
```

---

## ⚙️ 配置说明

### .env 配置文件

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here         # 必需
DEEPSEEK_API_URL=https://api.deepseek.com  # 默认值
DEEPSEEK_MODEL=deepseek-chat                # 默认值

# 应用配置
APP_DEBUG=false                 # 是否启用调试模式
APP_LOG_LEVEL=INFO             # 日志级别
CHAT_HISTORY_LENGTH=20         # 保存最近N条对话
```

### Streamlit 配置

Streamlit 配置文件位于 `.streamlit/config.toml`，可以自定义：
- 主题颜色
- 字体
- 页面布局
- 上传文件大小限制等

---

## 🔧 核心模块说明

### RAG 模块（Phase 2）

#### BGEEmbeddings (`rag/embeddings.py`)
生成文本向量嵌入的模块，使用 BAAI/bge-small-zh-v1.5 模型。

**主要方法:**
- `embed_query(query)`: 对查询文本进行嵌入（带特殊前缀）
- `embed_documents(texts)`: 对文档列表进行嵌入
- `embed_batch(texts)`: 批量高效嵌入

**特点:**
- 向量维度：384
- 支持中文文本优化
- 归一化处理（Cosine相似度）

#### VectorStore (`rag/vector_store.py`)
使用 ChromaDB 的向量存储模块，用于存储和检索文档向量。

**主要方法:**
- `add_documents(documents, embeddings_manager)`: 添加文档到知识库
- `retrieve(query, top_k, embeddings_manager)`: 检索相似文档
- `get_collection_info()`: 获取知识库统计信息

**特点:**
- 持久化存储（DuckDB + Parquet）
- Cosine 相似度匹配
- 支持元数据（来源、分块ID等）

#### DocumentProcessor (`rag/document_processor.py`)
文档处理和分块模块，支持 PDF 和 TXT 文件。

**主要方法:**
- `chunk_documents(text)`: 将文本分块
- `process_file(file_path)`: 处理单个文件
- `process_directory(directory)`: 批量处理目录

**特点:**
- 中文友好的分割符
- 可配置的块大小和重叠
- 支持 PDF 文本提取
- 自动编码检测

#### RAGRetriever (`rag/retriever.py`)
RAG 检索协调器，整合所有 RAG 组件。

**主要方法:**
- `retrieve_context(query, top_k)`: 检索文档
- `build_rag_prompt(query, docs, system_prompt)`: 构建增强 Prompt
- `retrieve_and_build_prompt()`: 一体化检索和 Prompt 构建

**示例:**
```python
from rag.retriever import RAGRetriever
from rag.embeddings import BGEEmbeddings
from rag.vector_store import VectorStore

# 初始化
embeddings = BGEEmbeddings()
vector_store = VectorStore()
retriever = RAGRetriever(vector_store, embeddings)

# 检索和构建 Prompt
final_prompt, docs = retriever.retrieve_and_build_prompt(
    user_query="什么是机器学习?",
    top_k=3
)
```

---

### DeepSeekService (`app/services/deepseek_service.py`)
封装 DeepSeek API 调用的服务类

**主要方法:**
- `stream_chat()`: 流式调用（推荐用于 UI）
- `sync_chat()`: 同步调用（非流式）
- `async_stream_chat()`: 异步流式调用（高级）

**示例:**
```python
from app.services import DeepSeekService

service = DeepSeekService(
    api_key="your_key",
    api_url="https://api.deepseek.com",
    model="deepseek-chat"
)

# 流式输出
for chunk in service.stream_chat("你好"):
    print(chunk, end="", flush=True)
```

### ChatInterface (`app/components/chat_ui.py`)
管理 Streamlit 聊天界面的组件类

**主要方法:**
- `add_message()`: 添加消息到历史
- `render_messages()`: 显示所有消息
- `stream_response()`: 流式显示回复
- `clear_messages()`: 清空所有消息

---

## 📊 性能指标

| 指标 | 性能 |
|------|------|
| 首令牌响应时间 | 500-1000ms |
| 生成速度 | ~50-100 tokens/s |
| 稳定性 | 支持长文本生成 |
| 并发限制 | 单线程（Streamlit 限制） |

---

## 🐛 常见问题

### Q1: 启动时报错 "DEEPSEEK_API_KEY 未设置"
**A:** 确保：
1. 已复制 `.env.example` 为 `.env`
2. 填入了有效的 DeepSeek API 密钥
3. 未在 `.env` 中注释掉该行

### Q2: 对话卡顿或响应缓慢
**A:** 可能原因：
1. 网络连接问题
2. API 速率限制
3. 模型服务器过载
4. 尝试减小 `max_tokens` 值

### Q3: 如何保存对话记录
**A:** 当前版本对话记录在内存中。后续版本将支持：
- 导出为 JSON
- 保存到数据库
- 导出为 Markdown

### Q4: 可以离线使用吗
**A:** 不行，当前版本依赖 DeepSeek API。后续 RAG 版本支持本地文档检索。

---

## 📚 后续规划

### Phase 2: RAG 集成（✅ 已完成）
- [x] 集成 BGE-Small-zh-v1.5 向量模型
- [x] 集成 ChromaDB 知识库
- [x] 文档上传和处理界面
- [x] 文档块的向量化存储
- [x] 相关文档自动检索
- [x] RAG Prompt 融合

**已实现的组件:**
- BGEEmbeddings 向量嵌入模块
- VectorStore 向量存储模块
- DocumentProcessor 文档处理模块
- RAGRetriever RAG 检索协调器

### Phase 3: 功能增强
- [ ] 对话持久化（SQLite/PostgreSQL）
- [ ] 多知识库支持（按主题分类）
- [ ] 检索结果可视化和排序
- [ ] 对话导出功能（JSON/Markdown/PDF）
- [ ] 知识库管理界面（编辑/删除/更新文档）
- [ ] 向量模型微调支持

### Phase 4: 部署优化
- [ ] Docker 容器化部署
- [ ] 性能优化和缓存机制
- [ ] 监控和日志系统
- [ ] 多用户支持（用户认证）
- [ ] API 接口暴露
- [ ] 前端 UI 优化

---

## 🔐 安全建议

1. **API 密钥管理**
   - 永远不要在代码中硬编码 API 密钥
   - 使用 `.env` 文件管理敏感信息
   - 定期轮换 API 密钥

2. **日志和监控**
   - 检查日志文件查看 API 调用历史
   - 监控异常请求和错误

3. **网络安全**
   - 确保通过 HTTPS 与 API 通信
   - 不要在公网上暴露应用（可使用 SSH 隧道或 VPN）

---

## 📞 支持和反馈

- 遇到问题？检查常见问题部分
- 有建议？欢迎提交 Issue

---

## 📄 许可证

本项目遵循 MIT 许可证

---

## 更新日志

### v0.2.1 (2025-12-25)
- ✅ **新增严格模式**：强制使用本地知识库
- ✅ 系统提示词优化：明确指示 AI 只使用文档内容
- ✅ 知识库检查：空知识库时阻止提问
- ✅ 默认启用 RAG 检索和严格模式
- ✅ 添加测试脚本：`test_strict_mode.py`
- ✅ 详细使用指南：`STRICT_MODE_GUIDE.md`

### v0.2.0 (2025-12-25)
- ✅ Phase 2 RAG 集成完成
- ✅ BGE 向量嵌入模块
- ✅ ChromaDB 向量存储
- ✅ 文档处理和分块
- ✅ RAG 检索协调器
- ✅ 文件上传和导入
- ✅ 知识库检索界面
- ✅ 相关参考文献显示

### v0.1.0 (2025-12-25)
- ✅ 初始版本发布
- ✅ 完成基础对话功能
- ✅ 实现流式输出
- ✅ 参数配置面板

---

## 相关资源

- [Streamlit 官方文档](https://docs.streamlit.io/)
- [DeepSeek API 文档](https://api-docs.deepseek.com/)
- [RAG 技术介绍](https://arxiv.org/abs/2005.11401)
- [BGE 向量模型](https://huggingface.co/BAAI/bge-small-zh-v1.5)
