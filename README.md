# 🎬 TMDB 电影搜索系统 - FastAPI 教学项目

## 📚 课程概述

本课程通过构建一个 TMDB 电影搜索系统，学习现代Python Web开发技术。

**课程时长：** 2节课（每节90分钟）  
**技术栈：** FastAPI + TMDB API + Python + HTML/JavaScript  
**目标学生：** 有Python基础的大学生

> 📖 **关于 TMDB**: [The Movie Database (TMDB)](https://www.themoviedb.org/) 是全球最受欢迎的开放电影数据库，提供免费的API访问，支持中文数据。相比豆瓣API，TMDB提供更稳定的服务和更丰富的电影信息。

---

## 🎯 学习目标

### 第一节课
- ✅ 理解Web API的基本概念
- ✅ 掌握FastAPI框架基础
- ✅ 学会调用第三方API
- ✅ 实现基本的电影搜索功能

### 第二节课
- ✅ 构建完整的Web界面
- ✅ 实现高级搜索和筛选功能
- ✅ 添加电影收藏功能
- ✅ 学习项目部署

---

## 📂 项目结构

```
tmdb_movie_sourse/
├── README.md                 # 项目说明
├── SETUP.md                  # 环境搭建指南
├── STUDENT_GUIDE.md          # 学生使用指南
├── requirements.txt          # 依赖包列表
├── .env.example              # 环境变量模板
├── lesson1/                  # 第一节课内容
│   ├── step1_hello_fastapi.py
│   ├── step2_basic_api.py
│   ├── step3_tmdb_api.py    # TMDB API调用示例
│   └── exercises.md
├── lesson2/                  # 第二节课内容
│   ├── main.py              # 完整应用（支持真实API和模拟数据）
│   ├── config.py            # 配置管理
│   ├── .env.example         # 环境变量模板
│   ├── templates/           # HTML模板
│   │   └── index.html
│   └── static/              # 静态资源
│       ├── style.css
│       └── script.js
├── solutions/               # 练习答案
│   └── ...
└── teaching_guide.md        # 教学指南
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

```bash
# 复制环境变量模板
cd lesson2
cp .env.example .env

# 编辑 .env 文件，添加你的 TMDB API Key
# 如果没有API Key，系统会自动使用模拟数据
```

> 💡 **获取 TMDB API Key**: 访问 [TMDB API](https://www.themoviedb.org/settings/api) 免费申请

### 3. 运行第一节课示例

```bash
cd lesson1
uvicorn step1_hello_fastapi:app --reload
```

访问：http://127.0.0.1:8000

### 4. 运行完整项目

```bash
cd lesson2
python main.py
# 或者
uvicorn main:app --reload
```

访问：http://127.0.0.1:8000

> ⚙️ **切换模式**: 
> - 真实API模式: 在 `.env` 中设置 `USE_MOCK_DATA=False`
> - 模拟数据模式: 在 `.env` 中设置 `USE_MOCK_DATA=True`

---

## 🎓 教学安排

### 第一节课（90分钟）

**时间分配：**
- 10分钟：课程介绍 + 环境准备
- 20分钟：FastAPI入门（step1）
- 20分钟：构建基本API（step2）
- 30分钟：集成TMDB API（step3）
- 10分钟：练习和答疑

**核心知识点：**
- HTTP请求方法（GET/POST）
- RESTful API设计
- 路径参数和查询参数
- 异步编程基础（async/await）
- 第三方API调用（TMDB API）
- API认证（API Key管理）
- 环境变量配置

### 第二节课（90分钟）

**时间分配：**
- 5分钟：回顾上节课
- 25分钟：前端界面开发
- 30分钟：功能完善（搜索、筛选、收藏）
- 20分钟：项目部署演示
- 10分钟：总结和扩展方向

**核心知识点：**
- Jinja2模板渲染
- 前后端交互（AJAX）
- 数据持久化（简单版）
- 错误处理和异常管理
- 配置管理（环境变量）
- 项目部署准备

---

## 🌟 项目特色

1. **渐进式教学**：从最简单的Hello World到完整应用
2. **双模式支持**：支持真实TMDB API和模拟数据，无需API Key也能学习
3. **实用性强**：使用真实的TMDB电影数据，支持中文
4. **现代技术**：FastAPI自动API文档、类型提示、异步编程
5. **安全第一**：环境变量管理API Key，代码不包含敏感信息
6. **可扩展**：提供多个扩展方向供学生探索

---

## 🔗 相关资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [TMDB API文档](https://developers.themoviedb.org/3)
- [TMDB官网](https://www.themoviedb.org/)
- [Python异步编程教程](https://docs.python.org/zh-cn/3/library/asyncio.html)
- [Pydantic文档](https://docs.pydantic.dev/)

---

## 📝 作业和扩展

### 基础作业
1. 添加电影详情页面
2. 实现评分筛选功能
3. 添加电影类型分类

### 进阶挑战
1. 添加用户登录功能
2. 实现电影评论功能
3. 数据库持久化（SQLite）
4. 部署到云服务器

---

## 👨‍🏫 教师备注

- ✅ 提前测试所有代码
- ✅ 无需API Key也能演示（自动使用模拟数据）
- ✅ 建议学生申请自己的TMDB API Key（免费）
- ✅ 使用GitHub分享代码
- ✅ 强调API Key安全性（不要提交到GitHub）
- ✅ 鼓励学生提问和尝试

## 🔒 安全提醒

**重要：** 
- ❌ 不要将 `.env` 文件提交到Git
- ❌ 不要在代码中硬编码API Key
- ✅ 使用 `.env.example` 作为模板
- ✅ 在 `.gitignore` 中排除 `.env` 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**祝教学顺利！🎉**
