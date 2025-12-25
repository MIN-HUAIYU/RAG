# 使用示例

本文档包含 DeepSeek AI 对话系统的各种使用示例和代码片段。

## 目录
1. [基础使用](#基础使用)
2. [API 服务调用](#api-服务调用)
3. [聊天界面组件](#聊天界面组件)
4. [配置示例](#配置示例)
5. [常见用例](#常见用例)

---

## 基础使用

### 启动应用

```bash
# 方法 1：使用启动脚本（推荐）
python run.py

# 方法 2：直接使用 streamlit
streamlit run app/main.py

# 方法 3：指定端口
streamlit run app/main.py --server.port 8080
```

### 在浏览器中使用
- 应用默认启动在 `http://localhost:8501`
- 在输入框输入问题并按 Enter
- AI 会实时流式返回回复

---

## API 服务调用

### 示例 1：流式对话（推荐）

```python
from app.services import DeepSeekService

# 初始化服务
service = DeepSeekService(
    api_key="your_api_key",
    api_url="https://api.deepseek.com",
    model="deepseek-chat"
)

# 流式获取回复
prompt = "请用 5 句话概括人工智能的核心概念"

for chunk in service.stream_chat(
    prompt=prompt,
    temperature=0.7,
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

**输出示例：**
```
人工智能（AI）是计算机科学的一个分支，旨在创建能够...
```

### 示例 2：同步对话（简单）

```python
from app.services import DeepSeekService

service = DeepSeekService(
    api_key="your_api_key",
    api_url="https://api.deepseek.com",
    model="deepseek-chat"
)

# 获取完整回复
response = service.sync_chat(
    prompt="Python 的 GIL 是什么？",
    temperature=0.5,  # 更少随机，更确定
    max_tokens=1000
)

print(response)
```

### 示例 3：带系统提示的对话

```python
from app.services import DeepSeekService

service = DeepSeekService(
    api_key="your_api_key",
    api_url="https://api.deepseek.com",
    model="deepseek-chat"
)

# 自定义系统提示
system_prompt = "你是一个资深的 Python 开发者，拥有 10 年的经验。"

for chunk in service.stream_chat(
    prompt="如何优化 Python 代码性能？",
    system_prompt=system_prompt,
    temperature=0.7
):
    print(chunk, end="", flush=True)
```

### 示例 4：异步对话（高级）

```python
import asyncio
from app.services import DeepSeekService

async def async_chat():
    service = DeepSeekService(
        api_key="your_api_key",
        api_url="https://api.deepseek.com",
        model="deepseek-chat"
    )

    # 异步流式获取
    async for chunk in service.async_stream_chat(
        prompt="请介绍机器学习的三个主要领域"
    ):
        print(chunk, end="", flush=True)

# 运行异步函数
asyncio.run(async_chat())
```

---

## 聊天界面组件

### 示例 1：基础聊天界面

```python
import streamlit as st
from app.components import ChatInterface

# 初始化界面
chat = ChatInterface()

# 添加消息
chat.add_message("user", "你好")
chat.add_message("assistant", "你好！有什么我可以帮助你的吗？")

# 显示所有消息
chat.render_messages()

# 获取用户输入
user_input = chat.render_input()

if user_input:
    st.write(f"你输入了: {user_input}")
```

### 示例 2：管理对话历史

```python
import streamlit as st
from app.components import ChatInterface

chat = ChatInterface()

# 获取所有消息
all_messages = chat.get_messages()
st.write(f"总共有 {len(all_messages)} 条消息")

# 获取最后一条消息
last_msg = chat.get_last_message()
if last_msg:
    st.write(f"最后的消息来自: {last_msg['role']}")

# 清空对话
if st.button("清空所有对话"):
    chat.clear_messages()
    st.rerun()
```

### 示例 3：显示加载动画

```python
import streamlit as st
from app.services import DeepSeekService
from app.components import ChatInterface

chat = ChatInterface()
service = DeepSeekService(...)

user_input = chat.render_input()

if user_input:
    chat.add_message("user", user_input)

    # 显示加载
    with chat.display_loading():
        response = service.sync_chat(user_input)

    chat.add_message("assistant", response)
    chat.render_messages()
```

### 示例 4：流式显示回复

```python
import streamlit as st
from app.services import DeepSeekService
from app.components import ChatInterface

chat = ChatInterface()
service = DeepSeekService(...)

user_input = "请写一首关于春天的诗"

if user_input:
    chat.add_message("user", user_input)

    # 流式获取响应
    response_generator = service.stream_chat(user_input)

    # 流式显示在界面上
    full_response = chat.stream_response(response_generator)

    chat.add_message("assistant", full_response)
```

---

## 配置示例

### 示例 1：读取配置

```python
from app.config import Config

print(f"API Key: {Config.DEEPSEEK_API_KEY[:10]}...")
print(f"API URL: {Config.DEEPSEEK_API_URL}")
print(f"模型: {Config.DEEPSEEK_MODEL}")
print(f"调试模式: {Config.APP_DEBUG}")
print(f"日志级别: {Config.APP_LOG_LEVEL}")
```

### 示例 2：验证配置

```python
from app.config import Config

try:
    Config.validate()
    print("✅ 配置有效")
except ValueError as e:
    print(f"❌ 配置错误: {e}")
```

### 示例 3：自定义配置

编辑 `.env` 文件：

```env
DEEPSEEK_API_KEY=sk-xxxxx

# 调整 API URL（如需要）
DEEPSEEK_API_URL=https://api.deepseek.com

# 调整模型名称
DEEPSEEK_MODEL=deepseek-chat

# 应用配置
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
CHAT_HISTORY_LENGTH=50
```

---

## 常见用例

### 用例 1：代码审查助手

```python
from app.services import DeepSeekService

service = DeepSeekService(...)

code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total
"""

system_prompt = "你是一个专业的代码审查专家，提供建议时要指出问题和改进方案。"

prompt = f"""请审查以下代码：

```python
{code}
```

请指出潜在的问题和改进建议。"""

for chunk in service.stream_chat(prompt, system_prompt=system_prompt):
    print(chunk, end="", flush=True)
```

### 用例 2：多轮对话

```python
from app.services import DeepSeekService

service = DeepSeekService(...)

# 模拟多轮对话
conversation = []

questions = [
    "什么是递归？",
    "递归有什么缺点？",
    "如何避免递归的缺点？"
]

for question in questions:
    print(f"\n用户: {question}")
    print("AI: ", end="")

    response = service.sync_chat(question)
    print(response)

    conversation.append({
        "user": question,
        "assistant": response
    })

# 查看对话历史
print("\n=== 对话历史 ===")
for i, msg in enumerate(conversation, 1):
    print(f"{i}. Q: {msg['user']}")
    print(f"   A: {msg['assistant'][:100]}...")
```

### 用例 3：批量文本生成

```python
from app.services import DeepSeekService

service = DeepSeekService(...)

topics = [
    "人工智能的未来",
    "量子计算的应用",
    "区块链技术的发展"
]

results = {}

for topic in topics:
    prompt = f"请写一篇关于'{topic}'的 500 字短文"
    response = service.sync_chat(prompt, max_tokens=2000)
    results[topic] = response
    print(f"✅ 完成: {topic}")

# 保存结果
import json
with open("generated_content.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 用例 4：交互式问答

```python
import streamlit as st
from app.services import DeepSeekService
from app.components import ChatInterface

st.set_page_config(page_title="AI 问答助手")

chat = ChatInterface()
service = DeepSeekService(...)

st.title("🤖 AI 问答助手")

# 侧边栏配置
with st.sidebar:
    temperature = st.slider("温度", 0.0, 2.0, 0.7)
    max_tokens = st.slider("最大令牌", 100, 4000, 2000)

# 显示聊天历史
chat.render_messages()

# 用户输入
user_input = chat.render_input("输入你的问题...")

if user_input:
    chat.add_message("user", user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    # 流式显示回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in service.stream_chat(
            user_input,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    chat.add_message("assistant", full_response)
```

---

## 调试和日志

### 启用调试模式

在 `.env` 文件中设置：

```env
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
```

### 查看日志

```python
from loguru import logger

# 添加到日志
logger.info("这是一条信息日志")
logger.debug("这是一条调试日志")
logger.warning("这是一条警告")
logger.error("这是一条错误")
```

---

## 性能优化建议

1. **流式输出优于同步调用**：流式输出可以更快地显示第一个令牌
2. **使用适当的 max_tokens**：更小的值会更快响应
3. **缓存频繁查询**：对相同的问题进行缓存
4. **异步调用**：对于多个请求，使用异步可以提高效率

---

## 错误处理示例

```python
from app.services import DeepSeekService
import httpx

service = DeepSeekService(...)

try:
    response = service.sync_chat("你好")
except httpx.HTTPStatusError as e:
    print(f"API 返回错误: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"网络请求失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 下一步

- 查看 [README.md](README.md) 了解更多信息
- 查看源代码中的注释获取详细说明
- 进行第二阶段的 RAG 集成
