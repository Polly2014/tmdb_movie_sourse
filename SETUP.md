# 📝 配置和部署指南

## 🔐 环境变量配置

本项目使用环境变量来管理敏感信息（如 API Key）和配置参数。

### 配置步骤

1. **复制示例文件**
   ```bash
   cd lesson2
   cp .env.example .env
   ```

2. **编辑 .env 文件**
   ```bash
   nano .env  # 或使用你喜欢的编辑器
   ```

3. **填入你的 TMDB API Key**
   ```env
   TMDB_API_KEY=你的API密钥
   ```

### 获取 TMDB API Key

1. 访问 [TMDB 官网](https://www.themoviedb.org/)
2. 注册/登录账号
3. 进入 [API Settings](https://www.themoviedb.org/settings/api)
4. 申请 API Key（免费）
5. 复制 "API Read Access Token" 或 "API Key (v3 auth)"

## 📋 文件说明

### 不应上传到 Git 的文件

以下文件已在 `.gitignore` 中配置，**不会**被上传到 GitHub：

- `.env` - 包含你的 API Key（敏感信息）
- `venv/` - 虚拟环境目录
- `__pycache__/` - Python 缓存文件
- `*.pyc` - 编译后的 Python 文件
- `.DS_Store` - macOS 系统文件

### 应该上传到 Git 的文件

- `.env.example` - 环境变量示例（不包含真实 API Key）
- `.gitignore` - Git 忽略规则
- `config.py` - 配置管理代码
- `main.py` - 主应用代码
- `README.md` - 项目文档
- `requirements.txt` - 依赖列表

## 🚀 部署建议

### 本地开发

```bash
# 1. 克隆仓库
git clone <your-repo>
cd tmdb_movie_sourse

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cd lesson2
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 5. 启动服务
python main.py
```

### 生产环境

对于生产环境，建议：

1. **使用环境变量**（而非 .env 文件）
   ```bash
   export TMDB_API_KEY=your_key
   export HOST=0.0.0.0
   export PORT=8000
   ```

2. **使用 Gunicorn + Uvicorn Workers**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **使用 Docker**
   ```dockerfile
   FROM python:3.13-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY lesson2/ .
   ENV TMDB_API_KEY=${TMDB_API_KEY}
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. **使用反向代理**（如 Nginx）

## 🔒 安全注意事项

1. ✅ **永远不要**将 `.env` 文件提交到 Git
2. ✅ **永远不要**在代码中硬编码 API Key
3. ✅ 定期轮换 API Key
4. ✅ 使用 `.gitignore` 防止敏感文件上传
5. ✅ 在 GitHub 仓库设置中配置 Secrets（用于 CI/CD）

## 📦 依赖管理

### 更新依赖

```bash
# 查看已安装的包
pip list

# 导出依赖到 requirements.txt
pip freeze > requirements.txt

# 或只导出项目直接依赖
pip install pipreqs
pipreqs . --force
```

### 虚拟环境

建议为每个项目使用独立的虚拟环境：

```bash
# 创建
python3 -m venv venv

# 激活 (Linux/macOS)
source venv/bin/activate

# 激活 (Windows)
venv\Scripts\activate

# 停用
deactivate
```

## 🐛 常见问题

### 1. ValueError: 未找到 TMDB_API_KEY

**原因**: 未配置环境变量

**解决**: 
```bash
cd lesson2
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 2. 模块导入错误

**原因**: 未安装依赖或虚拟环境未激活

**解决**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. API 请求失败

**原因**: API Key 无效或网络问题

**解决**:
- 检查 API Key 是否正确
- 测试网络连接
- 或设置 `USE_MOCK_DATA=True` 使用模拟数据

## 📞 支持

如有问题，请提交 Issue 或联系维护者。
