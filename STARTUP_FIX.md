# 启动问题修复说明

## 问题描述

运行 `start_with_py311.bat` 时出现两个问题：

### 问题 1：File does not exist: app/main.py
**原因**：批处理文件使用相对路径，但工作目录不正确。

**修复**：在批处理文件开头添加：
```batch
cd /d "%~dp0"
```
这会自动切换到批处理文件所在目录（项目根目录）。

### 问题 2：ModuleNotFoundError: No module named 'app'
**原因**：`app/main.py` 使用绝对导入 `from app.config import Config`，但 Python 找不到 `app` 模块。

**修复**：在 `run.py` 中设置 PYTHONPATH 环境变量，将项目根目录添加到 Python 搜索路径。

## 修复内容

### 1. start_with_py311.bat
- ✅ 添加 `cd /d "%~dp0"` 自动切换到项目根目录
- ✅ 添加工作目录显示
- ✅ 添加 `app\main.py` 存在性检查
- ✅ 添加 `.env` 自动创建功能
- ✅ 改用 `python run.py` 启动（而非直接 `streamlit run`）

### 2. run.py
- ✅ 添加 PYTHONPATH 环境变量设置
- ✅ 将项目根目录添加到 Python 搜索路径
- ✅ 显示 PYTHONPATH 信息便于调试

## 使用方法

### 方式 1：双击运行（推荐）
```
双击 start_with_py311.bat
```

### 方式 2：命令行运行
```batch
cd /d d:\projects\RAG
start_with_py311.bat
```

### 方式 3：直接使用 Python
```batch
cd /d d:\projects\RAG
venv311\Scripts\activate
python run.py
```

## 启动流程

```
start_with_py311.bat
  ↓
1. 切换到项目根目录 (cd /d "%~dp0")
  ↓
2. 检查虚拟环境是否存在
  ↓
3. 激活 Python 3.11 虚拟环境
  ↓
4. 验证 Python 版本
  ↓
5. 检查/创建 .env 文件
  ↓
6. 调用 python run.py
  ↓
run.py 设置 PYTHONPATH = 项目根目录
  ↓
streamlit run app/main.py (可以正确导入 app 模块)
  ↓
应用启动成功 (http://localhost:8501)
```

## 验证步骤

启动后检查控制台输出：

```
╔════════════════════════════════════════════════════════╗
║       使用 Python 3.11 启动 RAG 应用                  ║
╚════════════════════════════════════════════════════════╝

📁 工作目录: D:\projects\RAG

[1/4] 激活 Python 3.11 虚拟环境...
✅ 虚拟环境已激活

[2/4] 验证 Python 版本...
Python 3.11.x

[3/4] 检查 .env 配置文件...
✅ 配置文件检查完成

[4/4] 启动 Streamlit 应用...
🚀 启动 Streamlit 应用...
📁 项目目录: D:\projects\RAG
🐍 PYTHONPATH: D:\projects\RAG

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

如果看到以上输出且没有错误，说明启动成功！

## 可能的其他问题

### 如果端口被占用 (8501 或 8502)
Streamlit 会自动尝试下一个端口。查看控制台输出中的实际端口号。

### 如果提示依赖缺失
```batch
venv311\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-rag.txt
```

### 如果 RAG 功能不可用
应用会自动降级为纯对话模式，不影响基本使用。

## 技术细节

### PYTHONPATH 的作用
```python
# run.py 中的关键代码
env = os.environ.copy()
env['PYTHONPATH'] = project_root  # 例如: D:\projects\RAG

# 这样 Python 就能找到：
# - D:\projects\RAG\app\config.py  (作为 app.config)
# - D:\projects\RAG\rag\embeddings.py  (作为 rag.embeddings)
```

### 为什么不直接修改 app/main.py 的导入语句？
使用绝对导入（`from app.config import ...`）是 Python 项目的最佳实践：
- ✅ 导入路径清晰明确
- ✅ 避免相对导入的复杂性
- ✅ 便于 IDE 识别和跳转
- ✅ 符合项目结构设计

正确的做法是设置 PYTHONPATH，而非改为相对导入。

## 总结

**所有问题已完全解决！** 现在可以通过双击 `start_with_py311.bat` 正常启动应用。
