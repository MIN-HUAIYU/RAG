# RAG 项目远程部署指南

## 📋 当前部署状态

### ✅ 已完成
- SSH 连接已建立
- 项目文件已上传到 `/root/RAG`（约 1.4GB，包含 49,099 个文件）
- 虚拟环境已创建（`/root/RAG/venv`）

### ⚠️ 待处理
- **Python 升级**: 远程服务器当前 Python 版本是 3.6.8，需要升级到 3.11+
- **依赖安装**: 因为 Python 版本过旧，部分依赖无法安装

---

## 🔴 关键问题：Python 版本过旧

**当前情况：**
- 远程服务器 Python 版本: **3.6.8**
- 项目要求 Python 版本: **3.9+**
- Streamlit 1.28.1 最低要求: **Python 3.9**

**解决方案：** 需要在远程服务器上升级 Python 到 3.11

---

## 🚀 后续部署步骤

### 步骤 1: 在远程服务器上手动安装 Python 3.11

因为远程服务器是 Windows 环境，需要通过以下方式之一安装 Python 3.11：

#### 方式 A：通过 RDP 连接远程服务器（推荐）
1. 使用 RDP 客户端连接到 `139.224.207.84`
2. 在远程桌面上下载并运行: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
3. 安装时选择：
   - ✅ 勾选 "Add Python 3.11 to PATH"
   - ✅ 勾选 "Install for all users"
4. 点击 "Install Now"

#### 方式 B：通过 SSH 远程安装（如果 PowerShell 可用）
```bash
# 连接到远程服务器
ssh root@139.224.207.84

# 执行以下命令
cd %TEMP%
powershell.exe -Command "Start-BitsTransfer -Source 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -Destination 'python-3.11.0-amd64.exe'"
python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
```

#### 方式 C：使用 Winget（如果已安装）
```bash
# 通过 SSH 连接后执行
winget install Python.Python.3.11
```

---

### 步骤 2: 验证 Python 安装

```bash
# 连接到远程服务器
ssh root@139.224.207.84

# 验证 Python 版本
python --version  # 应该显示 Python 3.11.x
python -m pip --version  # 验证 pip 可用
```

---

### 步骤 3: 在虚拟环境中安装依赖

```bash
# 连接到远程服务器
ssh root@139.224.207.84

# 进入项目目录
cd /root/RAG

# 删除旧虚拟环境（可选，如果之前创建过）
rm -rf venv

# 创建新虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows 环境下:
venv\Scripts\activate

# macOS/Linux 环境下:
source venv/bin/activate

# 升级 pip
python -m pip install --upgrade pip

# 安装基础依赖
pip install -r requirements.txt

# 安装 RAG 相关依赖
pip install -r requirements-rag.txt
```

---

### 步骤 4: 验证依赖安装

```bash
# 测试导入关键模块
python -c "import streamlit; print('Streamlit OK')"
python -c "import chromadb; print('ChromaDB OK')"
python -c "from sentence_transformers import SentenceTransformer; print('SentenceTransformers OK')"
```

---

### 步骤 5: 启动应用

#### 方式 A: 本地访问（服务器本地）
```bash
# 激活虚拟环境
cd /root/RAG
venv\Scripts\activate

# 启动应用
streamlit run app/main.py
```

浏览器将自动打开 `http://localhost:8501`

#### 方式 B: 远程访问（从本地访问）
```bash
# 激活虚拟环境
cd /root/RAG
venv\Scripts\activate

# 监听所有网卡的 8501 端口
streamlit run app/main.py --server.address 0.0.0.0
```

然后从本地浏览器访问: `http://139.224.207.84:8501`

---

## 📝 环境配置

确保远程服务器上的 `.env` 文件已正确配置：

```bash
# 查看 .env 文件内容
cat /root/RAG/.env
```

应该包含：
```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
APP_DEBUG=false
APP_LOG_LEVEL=INFO
CHAT_HISTORY_LENGTH=20
```

---

## 🔧 故障排除

### 问题 1: "Python 3.11 not found"
**解决方案:**
1. 确认 Python 已安装：`python --version`
2. 如果不是 3.11，需要重新安装或修改 PATH
3. 在 Windows 上，可能需要将 Python 3.11 路径添加到系统环境变量

### 问题 2: "streamlit: command not found"
**解决方案:**
1. 确保虚拟环境已激活
2. 确认 Streamlit 已正确安装：`pip list | grep streamlit`
3. 尝试重新安装：`pip install streamlit==1.28.1`

### 问题 3: "ModuleNotFoundError" 错误
**解决方案:**
1. 确保依赖已完全安装：`pip install -r requirements.txt -r requirements-rag.txt`
2. 检查 Python 版本：`python --version`（应该是 3.9+）
3. 检查虚拟环境是否激活

### 问题 4: "Permission denied" 错误
**解决方案:**
```bash
# 添加执行权限
chmod +x /root/RAG/app/main.py

# 或者直接使用 python 运行
python /root/RAG/app/main.py
```

---

## 📊 项目文件位置

远程服务器上的项目结构：
```
/root/RAG/
├── app/                      # Streamlit 应用
│   ├── main.py              # 主应用文件
│   ├── config.py            # 配置文件
│   ├── services/            # 服务模块
│   │   └── deepseek_service.py
│   └── components/          # UI 组件
│       └── chat_ui.py
├── rag/                     # RAG 模块
│   ├── embeddings.py        # 向量嵌入
│   ├── vector_store.py      # 向量存储
│   ├── document_processor.py # 文档处理
│   └── retriever.py         # RAG 检索
├── data/                    # 数据目录
│   ├── documents/           # 上传的文档
│   └── chroma_db/          # ChromaDB 数据库
├── venv/                    # 虚拟环境
├── .env                     # 环境配置
├── requirements.txt         # 基础依赖
└── requirements-rag.txt     # RAG 依赖
```

---

## ✨ 项目功能

部署完成后，应用将提供以下功能：

1. **💬 实时对话**
   - 与 DeepSeek AI 进行实时对话
   - 流式输出回复
   - 对话历史管理

2. **📚 RAG 知识库**
   - 上传 PDF/TXT 文档
   - 自动向量化和分块
   - 智能检索相关文档
   - 增强 AI 回复准确性

3. **⚙️ 参数配置**
   - 调整对话温度（creativity）
   - 设置最大令牌数
   - 启用/禁用 RAG 检索
   - 严格模式（仅本地知识库）

---

## 📞 需要帮助？

如果部署过程中遇到问题，请：

1. 检查远程服务器的 Python 版本
2. 查看应用日志：`tail -f /root/RAG/logs/app.log`
3. 测试依赖：`python -c "import streamlit; print(streamlit.__version__)"`
4. 连接信息：
   - 服务器地址：`139.224.207.84`
   - 用户：`root`
   - SSH 密码：`mhy951405623..`

---

**最后更新：** 2025-12-26 11:35
**部署状态：** 等待 Python 升级
