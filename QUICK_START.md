# 🚀 快速开始指南 (5 分钟)

这是最简洁的启动指南，只包含必要的步骤。

---

## 前置要求

- Python 3.9+
- DeepSeek API Key（[申请地址](https://www.deepseek.com/)）
- 网络连接

---

## 步骤 1: 安装依赖 (1 分钟)

```bash
# 进入项目目录
cd RAG

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 步骤 2: 配置 API (1 分钟)

```bash
# 复制配置文件
cp .env.example .env

# 使用编辑器打开 .env 文件，找到这一行：
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 替换为你的实际 API Key:
# DEEPSEEK_API_KEY=sk_xxxxxxxxxxxxx
```

**Windows 用户**: 也可以用记事本打开 `.env` 文件编辑。

---

## 步骤 3: 验证配置 (1 分钟)

```bash
# 可选：验证环境配置
python test_setup.py
```

应该看到类似的输出：
```
✅ Python 版本符合要求
✅ 依赖包完整
✅ .env 文件存在
✅ 项目结构正确
✅ API 配置有效
✅ API 连接成功

总计: 6/6 通过
```

---

## 步骤 4: 启动应用 (2 分钟)

```bash
# 方式 1: 使用启动脚本（推荐）
python run.py

# 方式 2: 直接启动
streamlit run app/main.py
```

应该看到：
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

---

## 步骤 5: 使用应用

1. 浏览器自动打开 `http://localhost:8501`
2. 在下方的输入框输入问题，如：
   ```
   你好，请介绍一下你自己
   ```
3. 按 Enter 或点击发送
4. 看到 AI 流式回复

---

## 常见问题快速解决

### ❌ 错误: "DEEPSEEK_API_KEY 未设置"
**解决**:
- 检查 `.env` 文件是否存在
- 检查 API Key 是否正确填入（不要有空格）
- 重启应用

### ❌ 错误: "ModuleNotFoundError"
**解决**:
```bash
# 重新安装依赖
pip install -r requirements.txt

# 确认在虚拟环境中
```

### ❌ 应用启动很慢
**原因**: 首次启动需要加载依赖（正常）

### ❌ 对话没有回复
**检查**:
- API Key 是否有效
- 网络连接是否正常
- 尝试重启应用

---

## 下一步

### 了解更多
- 详细文档: [README.md](README.md)
- 使用示例: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- 部署指南: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### 调整应用
左侧面板可以调整：
- **温度**: 越低越专业，越高越创意
- **最大令牌数**: 控制回复长度
- **清空对话**: 删除所有历史记录

### 扩展功能
将来计划添加：
- 📄 文档上传和知识库
- 🔍 智能文档检索
- 💾 对话保存和导出
- 🌐 多用户支持

---

## 获取帮助

遇到问题？
1. 查看常见问题部分
2. 运行 `python test_setup.py` 检查环境
3. 查看应用日志（如果有错误会显示在控制台）
4. 阅读 [README.md](README.md) 的完整文档

---

## 停止应用

在终端按 `Ctrl + C` 停止应用。

---

祝你使用愉快！🎉
