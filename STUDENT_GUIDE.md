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

### 步骤 4: 获取 TMDB API Key（详细步骤）

#### 4.1 注册 TMDB 账号

1. 访问 [TMDB 官网](https://www.themoviedb.org/)
2. 点击右上角 "Join TMDB"（加入）
3. 填写注册信息：
   - Username（用户名）
   - Password（密码）
   - Email（邮箱）
4. 验证邮箱（检查收件箱，点击验证链接）

#### 4.2 申请 API Key

1. 登录后，进入 [API 设置页面](https://www.themoviedb.org/settings/api)
2. 点击 "Request an API Key"（申请 API Key）
3. 选择 **"Developer"**（开发者）类型
4. 接受服务条款

#### 4.3 填写申请表单

**必填字段说明：**

| 字段名称 | 英文名 | 如何填写 | 示例 |
|---------|--------|---------|------|
| 应用类型 | Application Type | 选择 "Website" | Website |
| 应用名称 | Application Name | 你的项目名称 | TMDB Movie Search |
| 应用简介 | Application Summary | 简单描述项目用途 | A learning project for FastAPI course |
| 应用URL | Application URL | 可以填 localhost 或 GitHub | http://localhost:8000 |
| 个人信息 | Personal Information | 按实际填写 | - |

**推荐填写内容：**

```
Application Name（应用名称）:
TMDB Movie Learning Project

Application Summary（应用简介）:
This is a student learning project for a FastAPI web development course. 
The application uses TMDB API to search movies and display movie information.

Application URL（应用网址）:
http://localhost:8000
或
https://github.com/[你的用户名]/tmdb_movie_sourse
```

#### 4.4 获取 API Key

1. 提交表单后，会立即生成 API Key
2. 找到 **"API Key (v3 auth)"** 部分
3. 复制这个32位的密钥（类似：`a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`）
4. **保密！** 不要分享给他人或提交到 GitHub

> 💡 **提示：** 整个申请过程约 2-5 分钟，完全免费！

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
   访问: http://127.0.0.1:8000/docs

2. **step2_basic_api.py** - 基础 API 开发（CRUD操作）
   ```bash
   uvicorn step2_basic_api:app --reload
   ```
   访问: http://127.0.0.1:8000/docs

3. **step3_tmdb_api.py** - TMDB API 集成（真实数据）
   
   **方式1：使用模拟数据（无需 API Key）**
   ```bash
   python step3_tmdb_api.py
   ```
   
   **方式2：使用真实 API（需要 API Key）**
   ```bash
   # 先创建 .env 文件
   cp .env.example .env
   # 编辑 .env，填入 API Key
   # 然后运行
   python step3_tmdb_api.py
   ```
   访问: http://127.0.0.1:8000/docs

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

### Q5: 如何保护 API Key？

**重要安全提示：**

❌ **不要做：**
- 不要将 API Key 直接写在代码中
- 不要将 `.env` 文件提交到 GitHub
- 不要在公开场合分享你的 API Key
- 不要截图包含 API Key 的内容

✅ **应该做：**
- 使用 `.env` 文件存储 API Key
- 确保 `.env` 在 `.gitignore` 中
- 使用 `.env.example` 作为模板（不包含真实 Key）
- 如果泄露，立即在 TMDB 网站重新生成新的 Key

**检查是否安全：**
```bash
# 查看 .gitignore 是否包含 .env
cat .gitignore | grep .env

# 确保 .env 没有被 Git 追踪
git status  # 不应该看到 .env 文件
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
