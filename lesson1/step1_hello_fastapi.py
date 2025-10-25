"""
第一节课 - Step 1: FastAPI 入门
学习目标：
1. 了解 FastAPI 的基本结构
2. 创建第一个 API 端点
3. 理解自动生成的 API 文档
"""

from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI(
    title="我的第一个FastAPI应用",
    description="学习FastAPI的入门示例",
    version="1.0.0"
)


# 1. 最简单的GET请求
@app.get("/")
async def root():
    """
    根路径 - 返回欢迎信息
    """
    return {"message": "欢迎来到FastAPI世界！"}


# 2. 带路径参数的请求
@app.get("/hello/{name}")
async def say_hello(name: str):
    """
    路径参数示例
    访问: http://127.0.0.1:8000/hello/张三
    """
    return {"message": f"你好，{name}！"}


# 3. 带查询参数的请求
@app.get("/greet")
async def greet(name: str = "朋友", age: int = 0):
    """
    查询参数示例
    访问: http://127.0.0.1:8000/greet?name=李四&age=20
    """
    if age > 0:
        return {"message": f"你好，{age}岁的{name}！"}
    return {"message": f"你好，{name}！"}


# 4. 返回更复杂的数据
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    """
    返回用户信息（模拟数据）
    """
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user{user_id}@example.com",
        "is_active": True
    }


# 5. POST 请求示例
from pydantic import BaseModel

class Item(BaseModel):
    """数据模型"""
    name: str
    price: float
    description: str = None

@app.post("/items/")
async def create_item(item: Item):
    """
    创建物品（POST请求）
    测试方法：访问 http://127.0.0.1:8000/docs 使用交互式文档
    """
    return {
        "message": "物品创建成功",
        "item": item.dict()
    }


"""
🎯 运行说明：
1. 在终端运行：uvicorn step1_hello_fastapi:app --reload
2. 访问 http://127.0.0.1:8000 查看根路径
3. 访问 http://127.0.0.1:8000/docs 查看自动生成的API文档（重要！）
4. 访问 http://127.0.0.1:8000/redoc 查看另一种风格的文档

💡 课堂练习：
1. 创建一个 /about 端点，返回你的个人信息
2. 创建一个 /calculate 端点，接收两个数字参数，返回它们的和
3. 尝试修改代码，观察自动文档的变化
"""

if __name__ == "__main__":
    import uvicorn
    print("🚀 正在启动 FastAPI 服务器...")
    print("📖 API文档: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
