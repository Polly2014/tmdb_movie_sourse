"""
第一节课 - Step 3: 集成豆瓣电影API
学习目标：
1. 学会调用第三方API
2. 处理异步HTTP请求
3. 数据转换和错误处理
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import httpx
from datetime import datetime

app = FastAPI(
    title="豆瓣电影搜索API",
    description="集成豆瓣API的电影搜索服务",
    version="3.0.0"
)

# ========== 配置 ==========

# 豆瓣API基础URL（使用第三方代理服务）
DOUBAN_API_BASE = "https://douban-api-docs.zce.me"

# 超时设置
TIMEOUT = 10.0


# ========== 数据模型 ==========

class MovieInfo(BaseModel):
    """电影基本信息"""
    id: str
    title: str
    original_title: str = ""
    year: str = ""
    directors: List[str] = []
    actors: List[str] = []
    genres: List[str] = []
    rating: float = 0.0
    rating_count: int = 0
    cover: str = ""
    summary: str = ""


class MovieDetail(MovieInfo):
    """电影详细信息"""
    countries: List[str] = []
    languages: List[str] = []
    duration: str = ""
    aka: List[str] = []
    douban_url: str = ""


class SearchResult(BaseModel):
    """搜索结果"""
    count: int
    start: int
    total: int
    movies: List[MovieInfo]


# ========== 辅助函数 ==========

def parse_movie_data(data: dict) -> MovieInfo:
    """解析豆瓣API返回的电影数据"""
    try:
        return MovieInfo(
            id=data.get('id', ''),
            title=data.get('title', ''),
            original_title=data.get('original_title', ''),
            year=data.get('year', ''),
            directors=[d.get('name', '') for d in data.get('directors', [])],
            actors=[a.get('name', '') for a in data.get('casts', [])[:5]],  # 只取前5个
            genres=data.get('genres', []),
            rating=float(data.get('rating', {}).get('average', 0)),
            rating_count=int(data.get('rating', {}).get('numRaters', 0)),
            cover=data.get('images', {}).get('large', ''),
            summary=data.get('summary', '')
        )
    except Exception as e:
        print(f"解析电影数据出错: {e}")
        raise


async def fetch_from_douban(endpoint: str, params: dict = None) -> dict:
    """
    从豆瓣API获取数据
    使用异步HTTP客户端
    """
    url = f"{DOUBAN_API_BASE}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时，请稍后重试")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"豆瓣API请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# ========== API端点 ==========

@app.get("/", tags=["首页"])
async def root():
    """API首页"""
    return {
        "message": "欢迎使用豆瓣电影搜索API",
        "version": "3.0.0",
        "endpoints": {
            "搜索电影": "/search?q=关键词",
            "Top250": "/top250",
            "电影详情": "/movie/{movie_id}",
            "正在热映": "/in_theaters",
            "即将上映": "/coming_soon"
        },
        "docs": "/docs"
    }


@app.get("/search", response_model=SearchResult, tags=["搜索"])
async def search_movies(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    start: int = Query(0, ge=0, description="起始位置"),
    count: int = Query(10, ge=1, le=50, description="返回数量")
):
    """
    搜索电影
    
    示例：
    - /search?q=肖申克
    - /search?q=周星驰&count=20
    """
    params = {
        "q": q,
        "start": start,
        "count": count
    }
    
    data = await fetch_from_douban("v2/movie/search", params)
    
    # 解析电影列表
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return SearchResult(
        count=len(movies),
        start=data.get('start', 0),
        total=data.get('total', 0),
        movies=movies
    )


@app.get("/movie/{movie_id}", response_model=MovieDetail, tags=["电影详情"])
async def get_movie_detail(movie_id: str):
    """
    获取电影详细信息
    
    示例：
    - /movie/1292052 (肖申克的救赎)
    - /movie/1291546 (霸王别姬)
    """
    data = await fetch_from_douban(f"v2/movie/subject/{movie_id}")
    
    # 解析详细信息
    movie = parse_movie_data(data)
    
    return MovieDetail(
        **movie.dict(),
        countries=data.get('countries', []),
        languages=data.get('languages', []),
        duration=data.get('durations', [''])[0] if data.get('durations') else '',
        aka=data.get('aka', []),
        douban_url=data.get('alt', '')
    )


@app.get("/top250", response_model=SearchResult, tags=["榜单"])
async def get_top250(
    start: int = Query(0, ge=0, le=225, description="起始位置"),
    count: int = Query(25, ge=1, le=100, description="返回数量")
):
    """
    获取豆瓣Top250电影
    
    示例：
    - /top250 (前25部)
    - /top250?start=25&count=25 (第26-50部)
    """
    params = {
        "start": start,
        "count": count
    }
    
    data = await fetch_from_douban("v2/movie/top250", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return SearchResult(
        count=len(movies),
        start=data.get('start', 0),
        total=data.get('total', 0),
        movies=movies
    )


@app.get("/in_theaters", response_model=SearchResult, tags=["榜单"])
async def get_in_theaters(
    city: str = Query("北京", description="城市"),
    start: int = Query(0, ge=0, description="起始位置"),
    count: int = Query(10, ge=1, le=50, description="返回数量")
):
    """
    获取正在热映的电影
    
    示例：
    - /in_theaters
    - /in_theaters?city=上海
    """
    params = {
        "city": city,
        "start": start,
        "count": count
    }
    
    data = await fetch_from_douban("v2/movie/in_theaters", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return SearchResult(
        count=len(movies),
        start=data.get('start', 0),
        total=data.get('total', 0),
        movies=movies
    )


@app.get("/coming_soon", response_model=SearchResult, tags=["榜单"])
async def get_coming_soon(
    start: int = Query(0, ge=0, description="起始位置"),
    count: int = Query(10, ge=1, le=50, description="返回数量")
):
    """
    获取即将上映的电影
    """
    params = {
        "start": start,
        "count": count
    }
    
    data = await fetch_from_douban("v2/movie/coming_soon", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return SearchResult(
        count=len(movies),
        start=data.get('start', 0),
        total=data.get('total', 0),
        movies=movies
    )


@app.get("/recommendations", tags=["推荐"])
async def get_recommendations(
    genre: str = Query(None, description="类型：剧情、喜剧、动作等"),
    min_rating: float = Query(8.0, ge=0, le=10, description="最低评分")
):
    """
    获取推荐电影（基于Top250筛选）
    
    示例：
    - /recommendations?genre=剧情&min_rating=9.0
    - /recommendations?genre=喜剧&min_rating=8.5
    """
    # 获取Top250
    data = await fetch_from_douban("v2/movie/top250", {"start": 0, "count": 100})
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    # 筛选
    filtered_movies = []
    for movie in movies:
        # 评分筛选
        if movie.rating < min_rating:
            continue
        
        # 类型筛选
        if genre and genre not in movie.genres:
            continue
        
        filtered_movies.append(movie)
    
    return SearchResult(
        count=len(filtered_movies),
        start=0,
        total=len(filtered_movies),
        movies=filtered_movies[:20]  # 最多返回20部
    )


"""
🎯 运行说明：
1. 运行：uvicorn step3_douban_api:app --reload
2. 访问 http://127.0.0.1:8000/docs

💡 测试建议：
1. 搜索你喜欢的电影
2. 查看Top250榜单
3. 获取某部电影的详细信息（从搜索结果中获取ID）
4. 尝试不同的筛选条件

🌟 知识点总结：
1. async/await 异步编程
2. httpx 异步HTTP客户端
3. 错误处理和超时控制
4. 数据解析和转换
5. API设计最佳实践

🎓 扩展思考：
1. 如果豆瓣API不可用，怎么办？（缓存策略）
2. 如何提高API响应速度？（数据缓存）
3. 如何处理大量并发请求？（限流）
"""

if __name__ == "__main__":
    import uvicorn
    print("🎬 豆瓣电影API服务启动中...")
    print("📖 API文档: http://127.0.0.1:8000/docs")
    print("🔍 试试搜索: http://127.0.0.1:8000/search?q=肖申克")
    uvicorn.run(app, host="127.0.0.1", port=8000)
