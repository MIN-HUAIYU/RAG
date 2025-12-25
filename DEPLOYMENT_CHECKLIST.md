# 🚀 部署清单

按照这个清单来快速启动和部署 DeepSeek AI 对话系统。

---

## 第一阶段：本地开发部署

### 1. 环境准备

- [ ] Python 3.9+ 已安装
  ```bash
  python --version
  ```

- [ ] Git 已安装
  ```bash
  git --version
  ```

- [ ] 已进入项目目录
  ```bash
  cd RAG
  ```

### 2. 依赖安装

- [ ] 创建虚拟环境
  ```bash
  python -m venv venv
  ```

- [ ] 激活虚拟环境
  ```bash
  # Windows
  venv\Scripts\activate

  # macOS/Linux
  source venv/bin/activate
  ```

- [ ] 安装 Python 依赖
  ```bash
  pip install -r requirements.txt
  ```

- [ ] 验证依赖安装
  ```bash
  python test_setup.py
  ```

### 3. API 配置

- [ ] 拥有有效的 DeepSeek API Key
  - 访问 [DeepSeek 官网](https://www.deepseek.com/)
  - 申请 API 密钥

- [ ] 复制环境变量模板
  ```bash
  cp .env.example .env
  ```

- [ ] 编辑 `.env` 文件并填入 API Key
  ```env
  DEEPSEEK_API_KEY=your_actual_api_key_here
  ```

- [ ] 验证配置（运行测试）
  ```bash
  python test_setup.py
  ```

### 4. 启动应用

- [ ] 启动 Streamlit 应用
  ```bash
  python run.py
  ```

- [ ] 访问应用
  - 打开浏览器访问 `http://localhost:8501`

- [ ] 测试基本功能
  - [ ] 输入一条消息
  - [ ] 验证 AI 正常回复
  - [ ] 检查流式输出是否工作
  - [ ] 测试清空对话功能

### 5. 验证清单

运行验证脚本：

```bash
python test_setup.py
```

确保所有检查都通过：
- ✅ Python 版本 (3.9+)
- ✅ 依赖包完整
- ✅ .env 文件存在
- ✅ 项目结构正确
- ✅ API 配置有效
- ✅ API 连接成功

---

## 第二阶段：RAG 功能开发（预计）

### 向量模型部署

- [ ] 安装 RAG 相关依赖
  ```bash
  pip install sentence-transformers==2.2.2
  pip install chromadb==0.4.10
  pip install langchain==0.1.0
  ```

- [ ] 下载 BGE-Small-zh-v1.5 模型
  ```bash
  # 模型会在首次使用时自动下载
  # 或预先下载以加快启动
  python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
  ```

- [ ] 创建向量存储
  - [ ] 初始化 ChromaDB
  - [ ] 创建向量索引

- [ ] 集成文档处理
  - [ ] PDF 解析
  - [ ] 文本分块
  - [ ] 向量化

### 用户界面增强

- [ ] 文件上传组件
- [ ] 知识库管理界面
- [ ] 检索结果展示
- [ ] RAG 模式切换

---

## 第三阶段：生产部署（可选）

### Docker 容器化

- [ ] 创建 Dockerfile
- [ ] 创建 docker-compose.yml
- [ ] 构建镜像
- [ ] 测试容器运行

### 云平台部署

选择合适的部署平台：

#### Streamlit Cloud
- [ ] 项目上传到 GitHub
- [ ] 连接 Streamlit Cloud
- [ ] 配置环境变量
- [ ] 发布应用

#### Heroku（如果仍可用）
- [ ] 创建 Procfile
- [ ] 创建 runtime.txt
- [ ] 部署应用

#### 阿里云 / 腾讯云
- [ ] 配置云服务器
- [ ] 部署应用
- [ ] 配置域名和 SSL
- [ ] 监控和日志

### 性能优化

- [ ] 启用模型缓存
- [ ] 配置 CDN
- [ ] 优化数据库查询
- [ ] 添加请求缓存

### 安全加固

- [ ] 启用 HTTPS
- [ ] 配置 CORS
- [ ] 添加速率限制
- [ ] 实现用户认证
- [ ] 加密敏感数据

### 监控和维护

- [ ] 设置日志收集
- [ ] 配置告警
- [ ] 监控 API 使用量
- [ ] 定期备份

---

## 故障排查

### 问题 1: "DEEPSEEK_API_KEY 未设置"
**解决方案：**
1. 确认 `.env` 文件存在
2. 确认 API Key 已正确填入
3. 重启应用
4. 运行 `python test_setup.py` 验证

### 问题 2: 依赖安装失败
**解决方案：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip install --no-cache-dir -r requirements.txt

# 或指定 Python 版本
python -m pip install -r requirements.txt
```

### 问题 3: 模型下载失败
**解决方案：**
- 检查网络连接
- 尝试手动下载模型
- 配置 HuggingFace 镜像源

### 问题 4: API 返回错误
**解决方案：**
- 检查 API Key 是否有效
- 检查是否超过速率限制
- 查看完整错误日志

### 问题 5: 应用启动缓慢
**解决方案：**
- 首次运行会下载模型（如果使用 RAG）
- 可在后台让应用预热
- 增加服务器资源

---

## 性能优化建议

### 本地开发
- [ ] 使用虚拟环境
- [ ] 启用代码热重载（Streamlit 默认）
- [ ] 使用调试模式时的日志

### 部署优化
- [ ] 启用缓存
- [ ] 使用 CDN 加速
- [ ] 优化数据库查询
- [ ] 压缩资源文件
- [ ] 使用 Gunicorn 替代默认服务器

### 数据库优化（RAG 阶段）
- [ ] 创建适当的索引
- [ ] 定期清理过期数据
- [ ] 优化向量搜索参数
- [ ] 使用批处理操作

---

## 安全检查清单

### 代码安全
- [ ] 无硬编码密钥
- [ ] 输入验证完整
- [ ] SQL 注入防护
- [ ] XSS 防护

### 数据安全
- [ ] API Key 加密存储
- [ ] 敏感信息不记录
- [ ] 传输使用 HTTPS
- [ ] 定期备份

### 访问控制
- [ ] 仅授权用户访问
- [ ] API 速率限制
- [ ] 身份验证机制
- [ ] 审计日志记录

---

## 性能基准

目标性能指标：

| 指标 | 目标值 |
|------|--------|
| 首令牌响应 | < 1000ms |
| 完整响应 | < 30s |
| API 可用性 | 99.5% |
| 错误率 | < 0.1% |

---

## 发布前清单

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新完成
- [ ] README 和示例完整
- [ ] 变更日志更新
- [ ] 版本号更新
- [ ] Git 标签创建

---

## 后续支持

部署完成后：
1. 监控应用运行状态
2. 收集用户反馈
3. 定期更新依赖包
4. 优化性能和体验
5. 计划第二阶段 RAG 集成

---

最后更新: 2025-12-25
