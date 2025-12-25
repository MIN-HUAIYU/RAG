# Python 3.11 环境设置指南

## ✅ 环境已配置完成

你的 Python 3.11 虚拟环境已经成功创建并安装好所有依赖！

---

## 📁 虚拟环境位置

```
D:\projects\RAG\venv311\
```

---

## 🚀 快速启动

### 方法 1：使用启动脚本（推荐）

双击运行：
```
start_with_py311.bat
```

### 方法 2：手动启动

```cmd
# 1. 激活虚拟环境
venv311\Scripts\activate

# 2. 启动应用
streamlit run app/main.py
```

---

## ✅ 已安装的关键包

| 包名 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.11.9 | 运行环境 |
| **pip** | 25.3 | 包管理器（最新版） |
| **streamlit** | 1.28.1 | Web 框架 |
| **chromadb** | 0.5.0 | 向量数据库 |
| **sentence-transformers** | 5.2.0 | BGE 向量模型 |
| **transformers** | 4.57.3 | HuggingFace 转换器 |
| **langchain** | 0.2.17 | 文档处理框架 |
| **torch** | 2.9.1 | PyTorch 深度学习框架 |
| **httpx** | 0.25.0 | HTTP 客户端 |
| **pydantic** | 2.4.2 | 数据验证 |

完整包列表：129 个包已安装

---

## 🔧 环境验证

验证环境是否正常：

```cmd
# 激活环境
venv311\Scripts\activate

# 验证 Python 版本
python --version
# 应显示: Python 3.11.9

# 验证 RAG 模块
python -c "import chromadb; import sentence_transformers; print('RAG modules OK')"
# 应显示: RAG modules OK

# 运行测试脚本
python test_setup.py
```

---

## 📝 日常使用

### 启动应用

```cmd
# 进入项目目录
cd D:\projects\RAG

# 激活环境
venv311\Scripts\activate

# 启动应用
python run.py
```

### 安装新包

```cmd
# 激活环境
venv311\Scripts\activate

# 安装包
pip install <package-name>

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 更新依赖

```cmd
# 激活环境
venv311\Scripts\activate

# 更新所有包
pip install --upgrade -r requirements.txt
```

---

## ⚠️ 重要提示

### Python 3.14.2 vs Python 3.11.9

你的系统中有两个 Python 版本：

1. **Python 3.14.2** - 系统默认（预发布版本，不推荐用于生产）
2. **Python 3.11.9** - venv311 虚拟环境（稳定版本，✅ 推荐使用）

**务必使用 venv311 环境！**

### 确认你在正确的环境中

在激活虚拟环境后，命令提示符应该显示：

```cmd
(venv311) D:\projects\RAG>
```

### 环境变量配置

确保 `.env` 文件包含：

```env
DEEPSEEK_API_KEY=sk_your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

---

## 🐛 常见问题

### Q1: 双击 start_with_py311.bat 闪退

**原因**: 环境配置问题

**解决**:
```cmd
# 手动激活环境查看错误信息
venv311\Scripts\activate
python run.py
```

### Q2: 提示 "No module named 'xxx'"

**原因**: 可能使用了系统 Python 而非虚拟环境

**解决**:
```cmd
# 确认虚拟环境已激活
venv311\Scripts\activate

# 验证 Python 路径
where python
# 应显示: D:\projects\RAG\venv311\Scripts\python.exe

# 重新安装依赖
pip install -r requirements.txt
```

### Q3: API 调用失败

**检查**:
1. `.env` 文件中的 API Key 是否正确
2. 网络连接是否正常
3. API Key 是否有效

---

## 📊 性能对比

| 指标 | Python 3.14.2 | Python 3.11.9 |
|------|---------------|---------------|
| **稳定性** | ⚠️ 预发布版 | ✅ 稳定版 |
| **包兼容性** | ❌ 部分不兼容 | ✅ 完全兼容 |
| **RAG 支持** | ❌ 可能失败 | ✅ 完整支持 |
| **生产就绪** | ❌ 不推荐 | ✅ 推荐使用 |

---

## 🎯 下一步

1. **配置 API Key**（如果还没有）
   ```cmd
   # 编辑 .env 文件
   notepad .env
   ```

2. **启动应用**
   ```cmd
   start_with_py311.bat
   ```

3. **访问应用**

   浏览器打开：http://localhost:8501

4. **上传文档测试 RAG**

   在应用中上传 PDF 或 TXT 文件测试知识库功能

---

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [KNOWLEDGE_BASE_SETUP.md](KNOWLEDGE_BASE_SETUP.md) - 知识库设置
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 部署清单

---

## 🎉 环境配置完成

你现在可以使用稳定的 Python 3.11 环境运行完整的 RAG 应用了！

所有依赖已安装：
- ✅ 基础依赖（streamlit, httpx, requests 等）
- ✅ RAG 依赖（chromadb, sentence-transformers, langchain）
- ✅ 深度学习框架（torch, transformers）
- ✅ 文档处理（PyPDF2, python-docx, python-pptx）

祝使用愉快！🚀
