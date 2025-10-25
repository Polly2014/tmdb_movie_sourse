"""
第一节课 - Step 3: 集成TMDB电影API
学习目标：
1. 学会调用第三方API
2. 处理异步HTTP请求
3. 数据转换和错误处理
4. API认证和配置管理
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
from datetime import datetime
import os
from pathlib import Path

app = FastAPI(
    title="TMDB电影搜索API",
    description="集成TMDB API的电影搜索服务",
    version="3.0.0"
)

# ========== 配置 ==========

# TMDB API配置
TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# API Key（从环境变量读取）
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

# 超时设置
TIMEOUT = 10.0

# 是否使用模拟数据（当没有API Key时）
USE_MOCK_DATA = not TMDB_API_KEY


# ========== 模拟数据 ==========
MOCK_MOVIES = [
    {
        "id": 278, "title": "肖申克的救赎", "original_title": "The Shawshank Redemption",
        "vote_average": 8.7, "vote_count": 25000, "release_date": "1994-09-23",
        "poster_path": "/mock1.jpg", "overview": "一部关于希望和自由的经典电影...",
        "genre_ids": [18, 80]
    },
    {
        "id": 238, "title": "教父", "original_title": "The Godfather",
        "vote_average": 8.7, "vote_count": 18000, "release_date": "1972-03-24",
        "poster_path": "/mock2.jpg", "overview": "黑帮家族的史诗传奇...",
        "genre_ids": [18, 80]
    },
    {
        "id": 240, "title": "教父2", "original_title": "The Godfather Part II",
        "vote_average": 8.6, "vote_count": 12000, "release_date": "1974-12-20",
        "poster_path": "/mock3.jpg", "overview": "延续第一部的精彩...",
        "genre_ids": [18, 80]
    },
]


# ========== 数据模型 ==========

class MovieInfo(BaseModel):
    """电影基本信息"""
    id: int
    title: str
    original_title: str = ""
    year: str = ""
    rating: float = Field(0.0, ge=0, le=10)
    rating_count: int = 0
    cover: str = ""
    summary: str = ""
    genres: List[str] = []


class MovieDetail(MovieInfo):
    """电影详细信息"""
    countries: List[str] = []
    languages: List[str] = []
    duration: str = ""
    tmdb_url: str = ""


class SearchResult(BaseModel):
    """搜索结果"""
    count: int
    start: int
    total: int
    movies: List[MovieInfo]


# ========== 辅助函数 ==========

def get_image_url(path: Optional[str]) -> str:
    """获取完整的图片URL"""
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return f"{TMDB_IMAGE_BASE}{path}"


def parse_movie_data(data: dict, is_detail: bool = False) -> dict:
    """解析TMDB API返回的电影数据"""
    try:
        # 类型映射（简化版）
        genre_map = {
            28: "动作", 12: "冒险", 16: "动画", 35: "喜剧", 80: "犯罪",
            99: "纪录", 18: "剧情", 10751: "家庭", 14: "奇幻", 36: "历史",
            27: "恐怖", 10402: "音乐", 9648: "悬疑", 10749: "爱情", 878: "科幻",
            53: "惊悚", 10752: "战争", 37: "西部"
        }
        
        movie_data = {
            "id": data.get('id', 0),
            "title": data.get('title', ''),
            "original_title": data.get('original_title', ''),
            "year": data.get('release_date', '')[:4] if data.get('release_date') else '',
            "rating": round(data.get('vote_average', 0), 1),
            "rating_count": data.get('vote_count', 0),
            "cover": get_image_url(data.get('poster_path')),
            "summary": data.get('overview', '')[:200] + '...' if data.get('overview') else '',
        }
        
        # 处理类型
        if is_detail and 'genres' in data:
            movie_data["genres"] = [g.get("name", "") for g in data.get("genres", [])]
        else:
            genre_ids = data.get("genre_ids", [])
            movie_data["genres"] = [genre_map.get(gid, "其他") for gid in genre_ids[:3]]
        
        return movie_data
    except Exception as e:
        print(f"解析电影数据出错: {e}")
        raise


def get_mock_data(endpoint: str, params: dict = None) -> dict:
    """获取模拟数据"""
    params = params or {}
    
    if "search" in endpoint:
        keyword = params.get('query', '').lower()
        results = [m for m in MOCK_MOVIES if keyword in m['title'].lower() or keyword in m['original_title'].lower()]
        return {'results': results, 'total_results': len(results), 'page': 1}
    elif "popular" in endpoint or "top_rated" in endpoint:
        return {'results': MOCK_MOVIES, 'total_results': len(MOCK_MOVIES), 'page': 1}
    elif "movie/" in endpoint:
        # 电影详情
        movie_id = int(endpoint.split('/')[-1])
        for movie in MOCK_MOVIES:
            if movie['id'] == movie_id:
                # 添加详情信息
                detail = movie.copy()
                detail['genres'] = [{"id": gid, "name": ["动作", "冒险", "动画"][i % 3]} 
                                  for i, gid in enumerate(movie.get('genre_ids', []))]
                detail['production_countries'] = [{"name": "美国"}]
                detail['spoken_languages'] = [{"english_name": "英语"}]
                detail['runtime'] = 142
                return detail
        return MOCK_MOVIES[0]
    
    return {'results': [], 'total_results': 0, 'page': 1}


async def fetch_from_tmdb(endpoint: str, params: dict = None) -> dict:
    """
    从TMDB API获取数据
    使用异步HTTP客户端
    """
    # 如果使用模拟数据
    if USE_MOCK_DATA:
        print(f"📊 使用模拟数据: {endpoint}")
        return get_mock_data(endpoint, params)
    
    url = f"{TMDB_API_BASE}/{endpoint}"
    
    # 添加API Key和语言参数
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY
    params['language'] = 'zh-CN'
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时，请稍后重试")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"TMDB API请求失败: {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"网络错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# ========== API端点 ==========

@app.get("/", tags=["首页"])
async def root():
    """API首页"""
    return {
        "message": "欢迎使用TMDB电影搜索API",
        "version": "3.0.0",
        "mode": "模拟数据模式" if USE_MOCK_DATA else "真实API模式",
        "endpoints": {
            "搜索电影": "/search?q=关键词",
            "热门电影": "/popular",
            "电影详情": "/movie/{movie_id}",
            "推荐电影": "/recommendations"
        },
        "docs": "/docs",
        "api_configured": bool(TMDB_API_KEY)
    }


@app.get("/search", response_model=SearchResult, tags=["搜索"])
async def search_movies(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, le=500, description="页码")
):
    """
    搜索电影
    
    示例：
    - /search?q=肖申克
    - /search?q=Inception&page=1
    """
    params = {"query": q, "page": page}
    data = await fetch_from_tmdb("search/movie", params)
    
    # 解析电影列表
    movies_data = [parse_movie_data(item) for item in data.get('results', [])]
    movies = [MovieInfo(**m) for m in movies_data]
    
    return SearchResult(
        count=len(movies),
        start=(page - 1) * 20,
        total=min(data.get('total_results', 0), 10000),
        movies=movies
    )


@app.get("/movie/{movie_id}", response_model=MovieDetail, tags=["电影详情"])
async def get_movie_detail(movie_id: int):
    """
    获取电影详细信息
    
    示例：
    - /movie/278 (肖申克的救赎)
    - /movie/238 (教父)
    """
    data = await fetch_from_tmdb(f"movie/{movie_id}", {"append_to_response": "credits"})
    
    # 解析基本信息
    movie_data = parse_movie_data(data, is_detail=True)
    
    # 添加详情信息
    return MovieDetail(
        **movie_data,
        countries=[c.get('name', '') for c in data.get('production_countries', [])],
        languages=[l.get('english_name', '') for l in data.get('spoken_languages', [])],
        duration=f"{data.get('runtime', 0)} 分钟" if data.get('runtime') else '',
        tmdb_url=f"https://www.themoviedb.org/movie/{movie_id}"
    )


@app.get("/popular", response_model=SearchResult, tags=["榜单"])
async def get_popular(
    page: int = Query(1, ge=1, le=500, description="页码")
):
    """
    获取热门电影
    
    示例：
    - /popular
    - /popular?page=2
    """
    params = {"page": page}
    data = await fetch_from_tmdb("movie/popular", params)
    
    movies_data = [parse_movie_data(item) for item in data.get('results', [])]
    movies = [MovieInfo(**m) for m in movies_data]
    
    return SearchResult(
        count=len(movies),
        start=(page - 1) * 20,
        total=min(data.get('total_results', 0), 10000),
        movies=movies
    )


@app.get("/top_rated", response_model=SearchResult, tags=["榜单"])
async def get_top_rated(
    page: int = Query(1, ge=1, le=500, description="页码")
):
    """
    获取高分电影
    
    示例：
    - /top_rated
    - /top_rated?page=2
    """
    params = {"page": page}
    data = await fetch_from_tmdb("movie/top_rated", params)
    
    movies_data = [parse_movie_data(item) for item in data.get('results', [])]
    movies = [MovieInfo(**m) for m in movies_data]
    
    return SearchResult(
        count=len(movies),
        start=(page - 1) * 20,
        total=min(data.get('total_results', 0), 10000),
        movies=movies
    )


@app.get("/recommendations", tags=["推荐"])
async def get_recommendations(
    min_rating: float = Query(7.0, ge=0, le=10, description="最低评分")
):
    """
    获取推荐电影（基于热门电影筛选）
    
    示例：
    - /recommendations?min_rating=8.0
    - /recommendations?min_rating=7.5
    """
    # 获取热门电影
    data = await fetch_from_tmdb("movie/popular", {"page": 1})
    
    movies_data = [parse_movie_data(item) for item in data.get('results', [])]
    
    # 筛选高分电影
    filtered_movies = [
        MovieInfo(**m) for m in movies_data 
        if m['rating'] >= min_rating
    ]
    
    return SearchResult(
        count=len(filtered_movies),
        start=0,
        total=len(filtered_movies),
        movies=filtered_movies[:20]
    )


"""
🎯 运行说明：
1. 运行：uvicorn step3_tmdb_api:app --reload
2. 访问 http://127.0.0.1:8000/docs

💡 测试建议：
1. 搜索你喜欢的电影
2. 查看热门电影榜单
3. 获取某部电影的详细信息（从搜索结果中获取ID）
4. 尝试不同的筛选条件

🌟 知识点总结：
1. async/await 异步编程
2. httpx 异步HTTP客户端
3. 错误处理和超时控制
4. 数据解析和转换
5. API认证（API Key）
6. 环境变量配置
7. 模拟数据策略

🎓 扩展思考：
1. 如果TMDB API不可用，怎么办？（降级策略、缓存）
2. 如何提高API响应速度？（数据缓存、CDN）
3. 如何处理大量并发请求？（限流、队列）
4. 如何保护API Key？（环境变量、密钥管理）

📝 配置说明：
- 无API Key: 自动使用模拟数据
- 有API Key: 设置环境变量 export TMDB_API_KEY=your_key_here
"""

if __name__ == "__main__":
    import uvicorn
    print("🎬 TMDB电影API服务启动中...")
    print(f"🔑 API Key: {'已配置' if TMDB_API_KEY else '未配置（使用模拟数据）'}")
    print(f"📊 模式: {'模拟数据模式' if USE_MOCK_DATA else '真实API模式'}")
    print("📖 API文档: http://127.0.0.1:8000/docs")
    print("🔍 试试搜索: http://127.0.0.1:8000/search?q=肖申克")
    uvicorn.run(app, host="127.0.0.1", port=8000)
