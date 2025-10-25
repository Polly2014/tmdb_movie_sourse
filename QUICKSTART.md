# 🎬 豆瓣电影搜索系统 - 快速开始

## 📦 安装依赖

```bash
# 进入项目目录
cd douban_movie_course

# 安装依赖
pip install -r requirements.txt
```

## 🚀 运行第一节课示例

### Step 1: FastAPI入门

```bash
cd lesson1
uvicorn step1_hello_fastapi:app --reload
```

访问：
- 主页：http://127.0.0.1:8000
- API文档：http://127.0.0.1:8000/docs

### Step 2: 基本的电影API

```bash
uvicorn step2_basic_api:app --reload
```

### Step 3: 豆瓣API集成

```bash
uvicorn step3_douban_api:app --reload
```

## 🌐 运行完整Web应用（第二节课）

```bash
cd lesson2
uvicorn main:app --reload
```

访问：http://127.0.0.1:8000

## 💡 常见问题

### Q: 导入错误 "No module named 'fastapi'"
A: 请先安装依赖：`pip install -r requirements.txt`

### Q: 豆瓣API请求失败
A: 检查网络连接，或等待一会儿重试

### Q: 端口被占用
A: 更改端口：`uvicorn main:app --port 8001`

## 📚 学习资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/zh/)
- [Python异步编程](https://docs.python.org/zh-cn/3/library/asyncio.html)
- [豆瓣API文档](https://douban-api-docs.zce.me/)

## 🎯 下一步

1. 完成 `lesson1/exercises.md` 中的练习
2. 自己实现一些新功能
3. 部署到云平台

**祝学习愉快！** 🎉
