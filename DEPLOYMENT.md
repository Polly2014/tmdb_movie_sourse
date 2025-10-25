# 🚀 项目部署指南

本指南将帮助你把豆瓣电影搜索系统部署到云平台。

---

## 方案一：Render 部署（推荐，免费）

### 优势
- ✅ 完全免费
- ✅ 自动从GitHub部署
- ✅ 支持自定义域名
- ✅ 自动HTTPS

### 步骤

#### 1. 准备代码

在项目根目录创建以下文件：

**render.yaml**
```yaml
services:
  - type: web
    name: douban-movie-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn lesson2.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

**runtime.txt**
```
python-3.9.16
```

#### 2. 推送到GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/douban-movie-app.git
git push -u origin main
```

#### 3. 在Render部署

1. 访问 https://render.com 并注册
2. 点击 "New +" → "Web Service"
3. 连接你的GitHub仓库
4. 配置：
   - **Name**: douban-movie-app
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn lesson2.main:app --host 0.0.0.0 --port $PORT`
5. 点击 "Create Web Service"
6. 等待部署完成（约3-5分钟）

#### 4. 访问你的网站

部署完成后，Render会提供一个URL：
```
https://douban-movie-app.onrender.com
```

---

## 方案二：Railway 部署

### 优势
- ✅ 500小时免费使用
- ✅ 部署简单
- ✅ 性能好

### 步骤

#### 1. 准备Procfile

创建 `Procfile` 文件：
```
web: uvicorn lesson2.main:app --host 0.0.0.0 --port $PORT
```

#### 2. 部署

1. 访问 https://railway.app
2. 使用GitHub登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway会自动检测Python项目并部署

#### 3. 配置环境变量（可选）

在Railway面板中添加：
```
PORT=8000
PYTHON_VERSION=3.9
```

---

## 方案三：使用Docker部署

### 创建Dockerfile

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "lesson2.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 创建 .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.git
.gitignore
README.md
*.md
```

### 构建和运行

```bash
# 构建镜像
docker build -t douban-movie-app .

# 运行容器
docker run -d -p 8000:8000 --name movie-app douban-movie-app

# 查看日志
docker logs -f movie-app
```

### 使用Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

---

## 方案四：腾讯云/阿里云部署

### 1. 购买云服务器

- 选择最低配置即可（1核2G）
- 系统选择Ubuntu 20.04

### 2. 配置服务器

SSH登录服务器后：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.9
sudo apt install python3.9 python3.9-venv python3-pip -y

# 安装Nginx
sudo apt install nginx -y
```

### 3. 部署应用

```bash
# 克隆代码
git clone https://github.com/你的用户名/douban-movie-app.git
cd douban-movie-app

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装进程管理工具
pip install gunicorn
```

### 4. 使用Gunicorn运行

创建 `gunicorn_conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
```

启动：
```bash
gunicorn lesson2.main:app -c gunicorn_conf.py
```

### 5. 配置Nginx反向代理

创建 `/etc/nginx/sites-available/douban-movie`:

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/douban-movie-app/lesson2/static;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/douban-movie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. 配置系统服务

创建 `/etc/systemd/system/douban-movie.service`:

```ini
[Unit]
Description=Douban Movie App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/douban-movie-app
Environment="PATH=/home/ubuntu/douban-movie-app/venv/bin"
ExecStart=/home/ubuntu/douban-movie-app/venv/bin/gunicorn lesson2.main:app -c gunicorn_conf.py

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start douban-movie
sudo systemctl enable douban-movie
sudo systemctl status douban-movie
```

---

## 性能优化建议

### 1. 使用Redis缓存

```bash
# 安装Redis
pip install redis

# 配置缓存
# 在main.py中添加
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

### 2. 启用GZIP压缩

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3. 静态文件CDN

将static文件夹上传到CDN：
- 阿里云OSS
- 腾讯云COS
- 七牛云

### 4. 数据库优化

如果使用数据库：
- 添加索引
- 使用连接池
- 查询优化

---

## 监控和日志

### 1. 应用监控

```python
# 添加健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2. 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. 错误追踪

使用Sentry：
```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="你的Sentry DSN",
    traces_sample_rate=1.0
)
```

---

## 安全建议

### 1. 使用HTTPS

免费SSL证书：Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 2. 环境变量

不要把敏感信息写在代码里：

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

### 3. CORS配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 常见问题

### Q: 部署后API请求失败？
A: 检查：
- 防火墙端口是否开放
- 环境变量是否正确
- 日志中的错误信息

### Q: 静态文件404？
A: 检查：
- static目录路径是否正确
- Nginx配置是否正确
- 文件权限是否正确

### Q: 性能不好？
A: 优化：
- 增加workers数量
- 使用缓存
- 优化数据库查询
- 使用CDN

---

## 部署检查清单

部署前确认：

- [ ] 代码已推送到GitHub
- [ ] requirements.txt完整
- [ ] 环境变量已配置
- [ ] 静态文件路径正确
- [ ] API端点测试通过
- [ ] 日志配置完成
- [ ] 错误处理完善
- [ ] 安全措施到位

部署后验证：

- [ ] 网站可以访问
- [ ] 搜索功能正常
- [ ] 收藏功能正常
- [ ] 响应速度acceptable
- [ ] 移动端显示正常
- [ ] 日志记录正常

---

**祝部署顺利！** 🚀

如有问题，欢迎提Issue或联系我。
