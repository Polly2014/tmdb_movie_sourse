# 第一节课 - 课堂练习

## 📝 练习一：FastAPI基础（15分钟）

### 题目
基于 `step1_hello_fastapi.py`，完成以下任务：

1. **个人信息API**
   - 创建 `/about` 端点
   - 返回你的姓名、专业、爱好等信息
   - 使用字典格式返回

2. **计算器API**
   - 创建 `/calculate` 端点
   - 接收两个数字参数：`a` 和 `b`
   - 接收一个操作符参数：`op`（可选值：add, subtract, multiply, divide）
   - 返回计算结果

3. **学生查询API**
   - 创建一个 `Student` 数据模型（包含：id, name, age, major）
   - 创建 `/students/{student_id}` 端点
   - 返回对应学生的信息（可以使用模拟数据）

### 提示
```python
# 计算器示例
@app.get("/calculate")
async def calculate(
    a: float,
    b: float,
    op: str = Query(..., regex="^(add|subtract|multiply|divide)$")
):
    # 你的代码
    pass
```

---

## 📝 练习二：数据模型和CRUD（20分钟）

### 题目
基于 `step2_basic_api.py`，扩展以下功能：

1. **高级搜索**
   - 创建 `/movies/advanced-search` 端点
   - 支持同时按年份范围和评分范围筛选
   - 参数：`year_from`, `year_to`, `min_rating`, `max_rating`

2. **导演统计**
   - 创建 `/directors` 端点
   - 返回所有导演及其作品数量
   - 按作品数量降序排列

3. **批量操作**
   - 创建 `/movies/batch` 端点（POST）
   - 支持一次性添加多部电影
   - 返回添加成功的电影列表

### 提示
```python
# 高级搜索示例
@app.get("/movies/advanced-search")
async def advanced_search(
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None
):
    results = movies_db
    
    if year_from:
        results = [m for m in results if m.year >= year_from]
    
    # 继续筛选...
    
    return results
```

---

## 📝 练习三：豆瓣API集成（20分钟）

### 题目
基于 `step3_douban_api.py`，实现以下功能：

1. **按导演搜索**
   - 创建 `/search/director` 端点
   - 输入导演名字，返回该导演的所有电影
   - 按评分降序排列

2. **电影对比**
   - 创建 `/compare` 端点
   - 接收两个电影ID
   - 返回两部电影的对比信息（评分、年份、类型等）

3. **个性化推荐**
   - 创建 `/recommend/similar` 端点
   - 输入一个电影ID
   - 返回相似类型且评分接近的电影
   - 提示：可以基于类型和评分进行匹配

### 提示
```python
# 电影对比示例
@app.get("/compare")
async def compare_movies(
    movie1_id: str = Query(..., description="第一部电影ID"),
    movie2_id: str = Query(..., description="第二部电影ID")
):
    # 获取两部电影的详细信息
    movie1 = await fetch_from_douban(f"v2/movie/subject/{movie1_id}")
    movie2 = await fetch_from_douban(f"v2/movie/subject/{movie2_id}")
    
    # 构建对比结果
    comparison = {
        "movie1": parse_movie_data(movie1),
        "movie2": parse_movie_data(movie2),
        "comparison": {
            "rating_diff": abs(movie1_rating - movie2_rating),
            # 更多对比...
        }
    }
    
    return comparison
```

---

## 🎯 挑战题（课后作业）

### 难度：⭐⭐⭐

1. **缓存机制**
   - 实现一个简单的内存缓存
   - 缓存豆瓣API的搜索结果
   - 5分钟内相同的搜索直接返回缓存结果

```python
from datetime import datetime, timedelta

cache = {}

def get_cache(key):
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(minutes=5):
            return data
    return None

def set_cache(key, data):
    cache[key] = (data, datetime.now())
```

2. **错误重试**
   - 当豆瓣API请求失败时，自动重试3次
   - 使用指数退避策略（第1次等1秒，第2次等2秒，第3次等4秒）

3. **API限流**
   - 实现一个简单的限流器
   - 每个IP每分钟最多请求10次
   - 超过限制返回429状态码

---

## ✅ 自我检查清单

完成练习后，确保你能够：

- [ ] 创建基本的GET/POST端点
- [ ] 使用路径参数和查询参数
- [ ] 定义和使用Pydantic数据模型
- [ ] 实现CRUD操作
- [ ] 调用第三方API
- [ ] 处理异步HTTP请求
- [ ] 进行基本的错误处理
- [ ] 使用FastAPI的自动文档

---

## 💡 提示和技巧

1. **调试技巧**
   - 使用 `print()` 或 `logging` 输出中间结果
   - 在 `/docs` 页面测试API
   - 使用浏览器开发者工具查看网络请求

2. **常见错误**
   - 忘记 `async`/`await` 关键字
   - 参数类型不匹配
   - 路径冲突（如 `/movies/search` 和 `/movies/{movie_id}`）

3. **最佳实践**
   - 给每个端点添加清晰的文档字符串
   - 使用有意义的变量名
   - 合理设置参数的默认值和验证规则

---

**祝你练习顺利！有问题随时举手提问！🎉**
