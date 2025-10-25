# 🎓 学生使用指南

欢迎！本指南将帮助你快速开始 TMDB 电影搜索系统项目。

## 📋 前置要求

- ✅ Python 3.10+ 已安装
- ✅ 基本的 Python 编程知识
- ✅ 对 Web 开发有基本了解

## 🚀 快速开始

### 步骤 1: 克隆项目

```bash
git clone https://github.com/Polly2014/tmdb_movie_sourse.git
cd tmdb_movie_sourse
```

### 步骤 2: 创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤 3: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 4: 获取 TMDB API Key

1. 访问 [TMDB 官网](https://www.themoviedb.org/)
2. 注册账号（免费）
3. 进入 [API 设置页面](https://www.themoviedb.org/settings/api)
4. 申请 API Key
5. 复制你的 API Key

### 步骤 5: 配置 API Key

```bash
cd lesson2
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：
```env
TMDB_API_KEY=你的API密钥
```

### 步骤 6: 启动项目

```bash
cd lesson2
python main.py
```

打开浏览器访问: http://127.0.0.1:8000

## 📖 课程内容

### 第一节课 - FastAPI 基础

**目录:** `lesson1/`

1. **step1_hello_fastapi.py** - FastAPI 入门
   ```bash
   cd lesson1
   uvicorn step1_hello_fastapi:app --reload
   ```

2. **step2_basic_api.py** - 基础 API 开发
   ```bash
   uvicorn step2_basic_api:app --reload
   ```

3. **step3_douban_api.py** - TMDB API 集成
   ```bash
   uvicorn step3_douban_api:app --reload
   ```

### 第二节课 - 完整 Web 应用

**目录:** `lesson2/`

完整的电影搜索系统，包含：
- 🔍 电影搜索
- 🌟 热门电影
- 🎭 正在热映/即将上映
- ❤️ 收藏功能
- 📊 统计分析

## 🔧 常见问题

### Q1: 没有 API Key 怎么办？

**方案 1:** 使用模拟数据
```env
USE_MOCK_DATA=True
```

**方案 2:** 申请免费 API Key（推荐）
- 访问 TMDB 官网注册
- 完全免费
- 5分钟完成申请

### Q2: `pip install` 失败

尝试使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 端口 8000 被占用

修改 `.env` 文件：
```env
PORT=8080
```

或在启动时指定：
```bash
python main.py  # 会读取 .env 中的配置
```

### Q4: 虚拟环境激活失败（Windows）

如果遇到 PowerShell 执行策略问题：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 学习资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/)
- [TMDB API 文档](https://developers.themoviedb.org/3)
- [Python 异步编程](https://docs.python.org/zh-cn/3/library/asyncio.html)

## 💡 练习建议

1. **第一课后练习:**
   - 修改搜索功能，添加分页
   - 实现按评分筛选
   - 添加错误处理

2. **第二课后练习:**
   - 美化界面（修改 CSS）
   - 添加电影评论功能
   - 实现用户登录（进阶）

3. **项目扩展:**
   - 添加电影详情页面
   - 实现个人推荐算法
   - 部署到云服务器

## 🆘 获取帮助

- 📧 邮件: [教师邮箱]
- 💬 讨论区: [课程讨论区链接]
- 🐛 问题反馈: [GitHub Issues](https://github.com/Polly2014/tmdb_movie_sourse/issues)

## 🎉 完成课程后

恭喜完成课程！你已经学会了：

✅ FastAPI 框架开发  
✅ RESTful API 设计  
✅ 异步编程  
✅ 第三方 API 集成  
✅ 前后端交互  

**下一步学习方向:**
- 数据库集成（SQLAlchemy）
- 用户认证（JWT）
- 项目部署（Docker, Nginx）
- 前端框架（Vue.js, React）

---

**祝学习愉快！🚀**
