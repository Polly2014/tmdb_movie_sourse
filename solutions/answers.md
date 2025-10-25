# 练习题答案参考

## 练习一：FastAPI基础

### 1. 个人信息API

```python
@app.get("/about")
async def about():
    """返回个人信息"""
    return {
        "name": "张三",
        "major": "计算机科学与技术",
        "grade": "大三",
        "hobbies": ["编程", "看电影", "打篮球"],
        "skills": ["Python", "Java", "Web开发"]
    }
```

### 2. 计算器API

```python
from fastapi import Query

@app.get("/calculate")
async def calculate(
    a: float = Query(..., description="第一个数字"),
    b: float = Query(..., description="第二个数字"),
    op: str = Query(..., regex="^(add|subtract|multiply|divide)$", description="操作符")
):
    """计算器API"""
    result = 0
    
    if op == "add":
        result = a + b
        operation = f"{a} + {b}"
    elif op == "subtract":
        result = a - b
        operation = f"{a} - {b}"
    elif op == "multiply":
        result = a * b
        operation = f"{a} × {b}"
    elif op == "divide":
        if b == 0:
            raise HTTPException(status_code=400, detail="除数不能为0")
        result = a / b
        operation = f"{a} ÷ {b}"
    
    return {
        "operation": operation,
        "result": result
    }
```

### 3. 学生查询API

```python
from pydantic import BaseModel

class Student(BaseModel):
    """学生数据模型"""
    id: int
    name: str
    age: int
    major: str
    gpa: float = 0.0

# 模拟学生数据库
students_db = {
    1: Student(id=1, name="张三", age=20, major="计算机科学", gpa=3.8),
    2: Student(id=2, name="李四", age=21, major="软件工程", gpa=3.6),
    3: Student(id=3, name="王五", age=19, major="数据科学", gpa=3.9)
}

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    """获取学生信息"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail=f"学生ID {student_id} 不存在")
    
    return students_db[student_id]

@app.get("/students", response_model=List[Student])
async def get_all_students():
    """获取所有学生"""
    return list(students_db.values())
```

---

## 练习二：数据模型和CRUD

### 1. 高级搜索

```python
@app.get("/movies/advanced-search", response_model=List[Movie])
async def advanced_search(
    year_from: Optional[int] = Query(None, ge=1900, description="起始年份"),
    year_to: Optional[int] = Query(None, le=2030, description="结束年份"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="最低评分"),
    max_rating: Optional[float] = Query(None, ge=0, le=10, description="最高评分"),
    genre: Optional[str] = Query(None, description="电影类型")
):
    """
    高级搜索功能
    支持多个条件组合筛选
    """
    results = movies_db.copy()
    
    # 按年份筛选
    if year_from:
        results = [m for m in results if m.year >= year_from]
    if year_to:
        results = [m for m in results if m.year <= year_to]
    
    # 按评分筛选
    if min_rating:
        results = [m for m in results if m.rating >= min_rating]
    if max_rating:
        results = [m for m in results if m.rating <= max_rating]
    
    # 按类型筛选
    if genre:
        results = [m for m in results if genre in m.genres]
    
    # 按评分降序排列
    results.sort(key=lambda x: x.rating, reverse=True)
    
    return results
```

### 2. 导演统计

```python
@app.get("/directors", tags=["统计"])
async def get_directors_stats():
    """
    获取导演统计信息
    返回所有导演及其作品数量
    """
    directors_count = {}
    directors_movies = {}
    
    # 统计每个导演的电影
    for movie in movies_db:
        if directors_count.get(movie.director):
            directors_count[movie.director] += 1
            directors_movies[movie.director].append(movie.title)
        else:
            directors_count[movie.director] = 1
            directors_movies[movie.director] = [movie.title]
    
    # 转换为列表并排序
    directors_list = [
        {
            "director": director,
            "movie_count": count,
            "movies": directors_movies[director]
        }
        for director, count in directors_count.items()
    ]
    
    # 按作品数量降序排列
    directors_list.sort(key=lambda x: x["movie_count"], reverse=True)
    
    return {
        "total_directors": len(directors_list),
        "directors": directors_list
    }
```

### 3. 批量操作

```python
class BatchMovieCreate(BaseModel):
    """批量创建电影的数据模型"""
    movies: List[MovieCreate]

@app.post("/movies/batch", response_model=List[Movie], tags=["电影"])
async def batch_create_movies(batch: BatchMovieCreate):
    """
    批量创建电影
    """
    global next_id
    
    created_movies = []
    
    for movie_data in batch.movies:
        # 创建新电影
        new_movie = Movie(
            id=next_id,
            **movie_data.dict()
        )
        
        # 添加到数据库
        movies_db.append(new_movie)
        created_movies.append(new_movie)
        next_id += 1
    
    return created_movies

# 使用示例：
"""
POST /movies/batch
{
  "movies": [
    {
      "title": "电影1",
      "director": "导演1",
      "year": 2020,
      "rating": 8.0,
      "genres": ["剧情"]
    },
    {
      "title": "电影2",
      "director": "导演2",
      "year": 2021,
      "rating": 8.5,
      "genres": ["喜剧"]
    }
  ]
}
"""
```

---

## 练习三：豆瓣API集成

### 1. 按导演搜索

```python
@app.get("/search/director", tags=["搜索"])
async def search_by_director(
    director: str = Query(..., min_length=1, description="导演姓名"),
    count: int = Query(20, ge=1, le=50, description="返回数量")
):
    """
    按导演搜索电影
    返回该导演的所有电影，按评分降序排列
    """
    # 使用豆瓣搜索API
    params = {
        "q": director,
        "count": 100  # 多获取一些，便于筛选
    }
    
    data = await fetch_from_douban("v2/movie/search", params)
    
    # 解析并筛选
    all_movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    # 筛选出该导演的电影
    director_movies = [
        movie for movie in all_movies 
        if director in ' '.join(movie.directors)
    ]
    
    # 按评分降序排列
    director_movies.sort(key=lambda x: x.rating, reverse=True)
    
    return {
        "director": director,
        "count": len(director_movies),
        "movies": director_movies[:count]
    }
```

### 2. 电影对比

```python
@app.get("/compare", tags=["对比"])
async def compare_movies(
    movie1_id: str = Query(..., description="第一部电影ID"),
    movie2_id: str = Query(..., description="第二部电影ID")
):
    """
    对比两部电影
    """
    # 获取两部电影的详细信息
    data1 = await fetch_from_douban(f"v2/movie/subject/{movie1_id}")
    data2 = await fetch_from_douban(f"v2/movie/subject/{movie2_id}")
    
    movie1 = parse_movie_data(data1)
    movie2 = parse_movie_data(data2)
    
    # 计算相似度
    common_genres = set(movie1.genres) & set(movie2.genres)
    
    # 构建对比结果
    comparison = {
        "movie1": {
            "title": movie1.title,
            "rating": movie1.rating,
            "year": movie1.year,
            "genres": movie1.genres,
            "directors": movie1.directors
        },
        "movie2": {
            "title": movie2.title,
            "rating": movie2.rating,
            "year": movie2.year,
            "genres": movie2.genres,
            "directors": movie2.directors
        },
        "comparison": {
            "rating_diff": abs(movie1.rating - movie2.rating),
            "year_diff": abs(int(movie1.year) - int(movie2.year)) if movie1.year and movie2.year else None,
            "common_genres": list(common_genres),
            "genre_similarity": len(common_genres) / max(len(movie1.genres), len(movie2.genres)) if movie1.genres or movie2.genres else 0,
            "better_rating": movie1.title if movie1.rating > movie2.rating else movie2.title,
            "conclusion": f"{movie1.title} 和 {movie2.title} 的评分相差 {abs(movie1.rating - movie2.rating):.1f} 分"
        }
    }
    
    return comparison
```

### 3. 个性化推荐

```python
@app.get("/recommend/similar", tags=["推荐"])
async def recommend_similar(
    movie_id: str = Query(..., description="电影ID"),
    count: int = Query(10, ge=1, le=20, description="推荐数量")
):
    """
    基于电影推荐相似电影
    根据类型和评分进行匹配
    """
    # 获取基准电影信息
    base_data = await fetch_from_douban(f"v2/movie/subject/{movie_id}")
    base_movie = parse_movie_data(base_data)
    
    # 获取Top250作为推荐池
    top_data = await fetch_from_douban("v2/movie/top250", {"count": 100})
    all_movies = [parse_movie_data(item) for item in top_data.get('subjects', [])]
    
    # 排除基准电影自己
    all_movies = [m for m in all_movies if m.id != movie_id]
    
    # 计算相似度
    recommendations = []
    for movie in all_movies:
        # 计算类型相似度
        common_genres = set(base_movie.genres) & set(movie.genres)
        genre_similarity = len(common_genres) / max(len(base_movie.genres), len(movie.genres), 1)
        
        # 计算评分相似度（差距越小越相似）
        rating_similarity = 1 - abs(base_movie.rating - movie.rating) / 10
        
        # 综合相似度（类型权重0.6，评分权重0.4）
        total_similarity = genre_similarity * 0.6 + rating_similarity * 0.4
        
        recommendations.append({
            "movie": movie,
            "similarity": total_similarity,
            "common_genres": list(common_genres)
        })
    
    # 按相似度排序
    recommendations.sort(key=lambda x: x["similarity"], reverse=True)
    
    return {
        "base_movie": {
            "title": base_movie.title,
            "genres": base_movie.genres,
            "rating": base_movie.rating
        },
        "recommendations": [
            {
                "movie": r["movie"].dict(),
                "similarity_score": round(r["similarity"], 2),
                "match_reason": f"共同类型: {', '.join(r['common_genres'])}" if r['common_genres'] else "评分接近"
            }
            for r in recommendations[:count]
        ]
    }
```

---

## 挑战题答案

### 1. 缓存机制

```python
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any

# 缓存存储
cache: Dict[str, Tuple[Any, datetime]] = {}

def get_cache(key: str, ttl_minutes: int = 5) -> Any:
    """
    从缓存获取数据
    Args:
        key: 缓存键
        ttl_minutes: 过期时间（分钟）
    """
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
            return data
    return None

def set_cache(key: str, data: Any):
    """设置缓存"""
    cache[key] = (data, datetime.now())

# 在搜索API中使用
@app.get("/search")
async def search_movies_with_cache(q: str, count: int = 20):
    """带缓存的搜索"""
    cache_key = f"search:{q}:{count}"
    
    # 尝试从缓存获取
    cached_result = get_cache(cache_key)
    if cached_result:
        return {**cached_result, "from_cache": True}
    
    # 缓存未命中，调用API
    params = {"q": q, "count": count}
    data = await fetch_from_douban("v2/movie/search", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    result = {
        "count": len(movies),
        "movies": [m.dict() for m in movies],
        "from_cache": False
    }
    
    # 存入缓存
    set_cache(cache_key, result)
    
    return result
```

### 2. 错误重试

```python
import asyncio
from typing import Callable

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0
):
    """
    带指数退避的重试机制
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                # 最后一次重试失败，抛出异常
                raise
            
            # 计算延迟时间（指数退避）
            delay = initial_delay * (2 ** attempt)
            print(f"请求失败，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)

# 使用示例
async def fetch_from_douban_with_retry(endpoint: str, params: dict = None):
    """带重试的豆瓣API请求"""
    
    async def make_request():
        url = f"{DOUBAN_API_BASE}/{endpoint}"
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    return await retry_with_backoff(make_request, max_retries=3)
```

### 3. API限流

```python
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request

# 存储每个IP的请求记录
request_records: Dict[str, list] = defaultdict(list)

def check_rate_limit(ip: str, max_requests: int = 10, window_minutes: int = 1) -> bool:
    """
    检查是否超过限流
    Args:
        ip: 客户端IP
        max_requests: 最大请求数
        window_minutes: 时间窗口（分钟）
    Returns:
        True: 未超限，False: 超限
    """
    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    
    # 获取该IP的请求记录
    records = request_records[ip]
    
    # 移除过期记录
    records[:] = [t for t in records if t > cutoff]
    
    # 检查是否超限
    if len(records) >= max_requests:
        return False
    
    # 记录本次请求
    records.append(now)
    return True

# 创建限流依赖
from fastapi import HTTPException

async def rate_limit_dependency(request: Request):
    """限流中间件"""
    client_ip = request.client.host
    
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试"
        )

# 在API中使用
from fastapi import Depends

@app.get("/search", dependencies=[Depends(rate_limit_dependency)])
async def search_with_rate_limit(q: str):
    """带限流的搜索API"""
    # ... 原有逻辑
    pass
```

---

## 完整示例：综合所有改进

```python
"""
综合示例：缓存 + 重试 + 限流
"""

from fastapi import FastAPI, Depends, HTTPException, Request, Query
import httpx
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any, Tuple, Callable

app = FastAPI(title="改进版豆瓣电影API")

# ========== 缓存系统 ==========
cache: Dict[str, Tuple[Any, datetime]] = {}

def get_cache(key: str, ttl_minutes: int = 5):
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
            return data
    return None

def set_cache(key: str, data: Any):
    cache[key] = (data, datetime.now())

# ========== 重试机制 ==========
async def retry_with_backoff(func: Callable, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt
            await asyncio.sleep(delay)

# ========== 限流系统 ==========
request_records: Dict[str, list] = defaultdict(list)

async def rate_limit(request: Request, max_requests: int = 10):
    ip = request.client.host
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)
    
    records = request_records[ip]
    records[:] = [t for t in records if t > cutoff]
    
    if len(records) >= max_requests:
        raise HTTPException(status_code=429, detail="请求过于频繁")
    
    records.append(now)

# ========== API端点 ==========
@app.get("/search", dependencies=[Depends(rate_limit)])
async def search_with_all_improvements(q: str, count: int = 20):
    """
    综合改进的搜索API
    - 缓存
    - 重试
    - 限流
    """
    cache_key = f"search:{q}:{count}"
    
    # 尝试缓存
    cached = get_cache(cache_key)
    if cached:
        return {**cached, "from_cache": True}
    
    # 带重试的API调用
    async def fetch():
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{DOUBAN_API_BASE}/v2/movie/search",
                params={"q": q, "count": count}
            )
            response.raise_for_status()
            return response.json()
    
    data = await retry_with_backoff(fetch)
    
    result = {
        "count": len(data.get('subjects', [])),
        "movies": data.get('subjects', []),
        "from_cache": False
    }
    
    # 存入缓存
    set_cache(cache_key, result)
    
    return result
```

---

**这些答案仅供参考，鼓励学生自己思考和实现！** 💪
