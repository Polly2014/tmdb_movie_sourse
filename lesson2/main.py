"""
第二节课 - 完整的 TMDB 电影Web应用
完整功能: 搜索、详情、热门电影、正在上映、即将上映、收藏系统、统计分析
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
from pathlib import Path
import json
from datetime import datetime
from config import settings  # 导入配置

app = FastAPI(
    title="TMDB 电影搜索系统",
    description="完整的 TMDB 电影搜索和收藏Web应用",
    version="2.0"
)

# ========== 配置静态文件和模板 ==========

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 配置模板目录
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 配置静态文件目录
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ========== 模拟数据 ==========
MOCK_TOP_MOVIES = [
    {"id": "1292052", "title": "肖申克的救赎", "year": "1994", "rating": 9.7, "genres": ["剧情", "犯罪"]},
    {"id": "1291546", "title": "霸王别姬", "year": "1993", "rating": 9.6, "genres": ["剧情", "爱情"]},
    {"id": "1292720", "title": "阿甘正传", "year": "1994", "rating": 9.5, "genres": ["剧情", "爱情"]},
    {"id": "1295644", "title": "这个杀手不太冷", "year": "1994", "rating": 9.4, "genres": ["剧情", "动作"]},
    {"id": "1292063", "title": "泰坦尼克号", "year": "1997", "rating": 9.4, "genres": ["剧情", "爱情"]},
    {"id": "1291561", "title": "千与千寻", "year": "2001", "rating": 9.4, "genres": ["动画", "奇幻"]},
    {"id": "1295038", "title": "辛德勒的名单", "year": "1993", "rating": 9.6, "genres": ["剧情", "历史"]},
    {"id": "1293350", "title": "盗梦空间", "year": "2010", "rating": 9.4, "genres": ["剧情", "科幻"]},
    {"id": "1291843", "title": "三傻大闹宝莱坞", "year": "2009", "rating": 9.2, "genres": ["剧情", "喜剧"]},
    {"id": "1307914", "title": "星际穿越", "year": "2014", "rating": 9.4, "genres": ["剧情", "科幻"]},
]

# 扩展更多电影用于搜索
for i in range(20):
    MOCK_TOP_MOVIES.append({
        "id": f"mock_{i}",
        "title": f"精彩电影 {i+1}",
        "year": str(2000 + i),
        "rating": round(7.5 + (i % 15) * 0.1, 1),
        "genres": ["剧情", "动作", "喜剧"][i % 3: i % 3 + 1]
    })

# ========== 简单的内存存储 ==========

# 用户收藏的电影（简单版，使用内存存储）
favorites: Dict[str, dict] = {}

# 搜索历史
search_history: List[dict] = []


# ========== 数据模型 ==========

class MovieInfo(BaseModel):
    """电影信息模型"""
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


class FavoriteMovie(BaseModel):
    """收藏的电影"""
    movie: MovieInfo
    added_at: str
    note: str = ""


# ========== 辅助函数 ==========

def parse_movie_data(data: dict) -> MovieInfo:
    """解析 TMDB API 返回的电影数据（已废弃，保留用于参考）"""
    try:
        return MovieInfo(
            id=str(data.get('id', '')),
            title=data.get('title', ''),
            original_title=data.get('original_title', data.get('title', '')),
            year=data.get('year', ''),
            directors=[d.get('name', '') if isinstance(d, dict) else str(d) for d in data.get('directors', [])],
            actors=[a.get('name', '') if isinstance(a, dict) else str(a) for a in data.get('casts', data.get('actors', []))[:5]],
            genres=data.get('genres', []),
            rating=float(data.get('rating', {}).get('average', 0) if isinstance(data.get('rating'), dict) else data.get('rating', 0)),
            rating_count=int(data.get('rating', {}).get('numRaters', 0) if isinstance(data.get('rating'), dict) else 100000),
            cover=data.get('images', {}).get('large', '') if isinstance(data.get('images'), dict) else '',
            summary=data.get('summary', '')[:200] + '...' if data.get('summary', '') else ''
        )
    except Exception as e:
        print(f"解析电影数据出错: {e}")
        raise

def get_mock_data(endpoint: str, params: dict = None) -> dict:
    """生成模拟数据 - 返回 TMDB API 格式"""
    params = params or {}
    
    # 将模拟数据转换为TMDB格式
    def convert_to_tmdb_format(mock_movie: dict) -> dict:
        """将模拟数据转换为TMDB API格式"""
        return {
            "id": int(mock_movie["id"]) if mock_movie["id"].isdigit() else 1,
            "title": mock_movie["title"],
            "original_title": mock_movie["title"],
            "release_date": f"{mock_movie['year']}-01-01",
            "vote_average": mock_movie["rating"],
            "vote_count": 10000,
            "poster_path": "/mock_poster.jpg",
            "overview": f"这是{mock_movie['title']}的精彩剧情介绍...",
            "genre_ids": [18, 80] if "剧情" in mock_movie.get("genres", []) else [28, 12],
            "genres": [{"id": i, "name": g} for i, g in enumerate(mock_movie.get("genres", []))],
        }
    
    if "search" in endpoint:
        # 搜索电影: /search/movie
        keyword = params.get('query', '').lower()
        results = [m for m in MOCK_TOP_MOVIES if keyword in m['title'].lower()]
        return {
            'results': [convert_to_tmdb_format(m) for m in results[:20]],
            'page': params.get('page', 1),
            'total_results': len(results),
            'total_pages': (len(results) + 19) // 20
        }
    elif "popular" in endpoint or "top" in endpoint:
        # 热门电影: /movie/popular
        page = params.get('page', 1)
        start = (page - 1) * 20
        count = min(20, len(MOCK_TOP_MOVIES) - start)
        return {
            'results': [convert_to_tmdb_format(m) for m in MOCK_TOP_MOVIES[start:start + count]],
            'page': page,
            'total_results': len(MOCK_TOP_MOVIES),
            'total_pages': (len(MOCK_TOP_MOVIES) + 19) // 20
        }
    elif "now_playing" in endpoint or "upcoming" in endpoint:
        # 正在上映/即将上映: /movie/now_playing, /movie/upcoming
        return {
            'results': [convert_to_tmdb_format(m) for m in MOCK_TOP_MOVIES[:20]],
            'page': 1,
            'total_results': 20,
            'total_pages': 1
        }
    elif "movie/" in endpoint and endpoint.split('/')[-1].isdigit():
        # 电影详情: /movie/{id}
        movie_id = endpoint.split('/')[-1]
        for movie in MOCK_TOP_MOVIES:
            if str(movie['id']) == str(movie_id):
                tmdb_movie = convert_to_tmdb_format(movie)
                # 添加详情页需要的额外信息
                tmdb_movie.update({
                    "runtime": 120,
                    "production_countries": [{"name": "美国"}],
                    "spoken_languages": [{"english_name": "English"}],
                    "credits": {
                        "cast": [{"name": f"演员{i}"} for i in range(1, 6)],
                        "crew": [{"name": "导演张三", "job": "Director"}]
                    }
                })
                return tmdb_movie
        # 默认返回第一个电影
        default = convert_to_tmdb_format(MOCK_TOP_MOVIES[0])
        default.update({
            "runtime": 120,
            "production_countries": [{"name": "美国"}],
            "spoken_languages": [{"english_name": "English"}],
            "credits": {
                "cast": [{"name": f"演员{i}"} for i in range(1, 6)],
                "crew": [{"name": "导演张三", "job": "Director"}]
            }
        })
        return default
    
    return {'results': [], 'page': 1, 'total_results': 0, 'total_pages': 0}


async def fetch_from_tmdb(endpoint: str, params: dict = None) -> dict:
    """从 TMDB API 获取数据"""
    # 如果使用模拟数据，直接返回
    if settings.USE_MOCK_DATA:
        print(f"📊 使用模拟数据: {endpoint}")
        return get_mock_data(endpoint, params)
    
    url = settings.get_api_url(endpoint)
    
    # 添加 API Key 和中文语言参数
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    params['language'] = 'zh-CN'  # 获取中文数据
    
    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.TimeoutException:
        print(f"❌ 请求超时: {url}")
        raise HTTPException(
            status_code=504, 
            detail={"error": "请求超时", "message": "TMDB API响应超时，请稍后重试"}
        )
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP错误: {e.response.status_code} - {url}")
        raise HTTPException(
            status_code=502, 
            detail={"error": "API请求失败", "message": f"TMDB API返回错误: {e.response.status_code}"}
        )
    except httpx.RequestError as e:
        print(f"❌ 请求错误: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail={"error": "网络错误", "message": "无法连接到TMDB API，请检查网络连接"}
        )
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": "服务器错误", "message": f"处理请求时发生错误: {str(e)}"}
        )


def convert_tmdb_to_douban_format(tmdb_movie: dict, is_detail: bool = False) -> dict:
    """将 TMDB 格式转换为前端兼容格式"""
    # 基础数据
    movie = {
        "id": str(tmdb_movie.get("id", "")),
        "title": tmdb_movie.get("title", ""),
        "original_title": tmdb_movie.get("original_title", ""),
        "year": tmdb_movie.get("release_date", "")[:4] if tmdb_movie.get("release_date") else "",
        "rating": round(tmdb_movie.get("vote_average", 0), 1),
        "rating_count": tmdb_movie.get("vote_count", 0),
        "cover": settings.get_image_url(tmdb_movie.get('poster_path')),
        "summary": tmdb_movie.get("overview", ""),
        "genres": [g.get("name", "") for g in tmdb_movie.get("genres", [])] if is_detail else [],
    }
    
    # 详情页需要更多信息
    if is_detail:
        credits = tmdb_movie.get("credits", {})
        movie.update({
            "directors": [p["name"] for p in credits.get("crew", []) if p.get("job") == "Director"][:5],
            "actors": [p["name"] for p in credits.get("cast", [])][:10],
            "countries": [c.get("name", "") for c in tmdb_movie.get("production_countries", [])],
            "languages": [l.get("english_name", "") for l in tmdb_movie.get("spoken_languages", [])],
            "duration": f"{tmdb_movie.get('runtime', 0)} 分钟" if tmdb_movie.get("runtime") else "",
            "douban_url": f"https://www.themoviedb.org/movie/{tmdb_movie.get('id')}",
        })
    else:
        # 列表页从 genre_ids 获取类型（需要预定义映射）
        genre_map = {
            28: "动作", 12: "冒险", 16: "动画", 35: "喜剧", 80: "犯罪",
            99: "纪录", 18: "剧情", 10751: "家庭", 14: "奇幻", 36: "历史",
            27: "恐怖", 10402: "音乐", 9648: "悬疑", 10749: "爱情", 878: "科幻",
            10770: "电视电影", 53: "惊悚", 10752: "战争", 37: "西部"
        }
        genre_ids = tmdb_movie.get("genre_ids", [])
        movie["genres"] = [genre_map.get(gid, "其他") for gid in genre_ids[:3]]
    
    return movie


# ========== 网页路由 ==========

@app.get("/", response_class=HTMLResponse, tags=["页面"])
async def index(request: Request):
    """主页 - 电影搜索界面"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "TMDB 电影搜索系统",
            "current_year": datetime.now().year
        }
    )


# ========== API路由 ==========

@app.get("/api/search", tags=["API"])
async def search_movies(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    start: int = Query(0, ge=0),
    count: int = Query(20, ge=1, le=50)
):
    """搜索电影API - 使用 TMDB"""
    # TMDB 搜索API：/search/movie
    params = {"query": q, "page": (start // count) + 1}
    data = await fetch_from_tmdb("search/movie", params)
    
    # 转换 TMDB 数据为前端格式
    movies = [convert_tmdb_to_douban_format(item) for item in data.get('results', [])]
    
    # 记录搜索历史
    search_history.insert(0, {
        "keyword": q,
        "timestamp": datetime.now().isoformat(),
        "results_count": len(movies)
    })
    
    # 只保留最近50条搜索记录
    if len(search_history) > 50:
        search_history.pop()
    
    return {
        "count": len(movies),
        "start": start,
        "total": data.get('total_results', 0),
        "movies": movies
    }


@app.get("/api/movie/{movie_id}", tags=["API"])
async def get_movie_detail(movie_id: str):
    """获取电影详情 - 使用 TMDB"""
    # TMDB 详情API：/movie/{id}，追加演员信息
    params = {"append_to_response": "credits"}
    data = await fetch_from_tmdb(f"movie/{movie_id}", params)
    movie = convert_tmdb_to_douban_format(data, is_detail=True)
    
    # 检查是否已收藏
    is_favorite = movie_id in favorites
    
    return {
        "movie": movie,
        "is_favorite": is_favorite,
        "extra": {
            "countries": data.get('production_countries', []),
            "languages": [l.get('english_name', '') for l in data.get('spoken_languages', [])],
            "duration": f"{data.get('runtime', 0)} 分钟" if data.get('runtime') else '',
            "aka": [],
            "douban_url": f"https://www.themoviedb.org/movie/{movie_id}"
        }
    }


@app.get("/api/top250", tags=["API"])
async def get_top250(
    start: int = Query(0, ge=0, le=225),
    count: int = Query(20, ge=1, le=100)
):
    """获取Top250 - 使用 TMDB 热门电影"""
    # TMDB 热门电影API：/movie/popular
    page = (start // count) + 1
    params = {"page": page}
    data = await fetch_from_tmdb("movie/popular", params)
    
    movies = [convert_tmdb_to_douban_format(item) for item in data.get('results', [])]
    
    return {
        "count": len(movies),
        "start": start,
        "total": min(data.get('total_results', 0), 500),  # TMDB 限制最多500页
        "movies": movies
    }


@app.get("/api/in_theaters", tags=["API"])
async def get_in_theaters(
    city: str = Query("北京"),
    count: int = Query(20, ge=1, le=50)
):
    """正在热映 - 使用 TMDB 正在上映"""
    # TMDB 正在上映API：/movie/now_playing (中国地区)
    params = {"region": "CN", "page": 1}
    data = await fetch_from_tmdb("movie/now_playing", params)
    
    # 转换为字典格式，限制数量
    movies = [convert_tmdb_to_douban_format(item) for item in data.get('results', [])[:count]]
    
    return {
        "count": len(movies),
        "movies": movies
    }


@app.get("/api/coming_soon", tags=["API"])
async def get_coming_soon(count: int = Query(20, ge=1, le=50)):
    """即将上映 - 使用 TMDB 即将上映"""
    # TMDB 即将上映API：/movie/upcoming (中国地区)
    params = {"region": "CN", "page": 1}
    data = await fetch_from_tmdb("movie/upcoming", params)
    
    # 转换为字典格式，限制数量
    movies = [convert_tmdb_to_douban_format(item) for item in data.get('results', [])[:count]]
    
    return {
        "count": len(movies),
        "movies": movies
    }


# ========== 收藏功能 ==========

@app.post("/api/favorites/{movie_id}", tags=["收藏"])
async def add_favorite(movie_id: str, note: str = ""):
    """添加到收藏"""
    # 获取电影信息 - 使用 TMDB
    params = {"append_to_response": "credits"}
    data = await fetch_from_tmdb(f"movie/{movie_id}", params)
    movie = convert_tmdb_to_douban_format(data, is_detail=True)
    
    # 添加到收藏
    favorites[movie_id] = {
        "movie": movie,
        "added_at": datetime.now().isoformat(),
        "note": note
    }
    
    return {
        "success": True,
        "message": "收藏成功",
        "movie": movie
    }


@app.delete("/api/favorites/{movie_id}", tags=["收藏"])
async def remove_favorite(movie_id: str):
    """取消收藏"""
    if movie_id in favorites:
        removed = favorites.pop(movie_id)
        return {
            "success": True,
            "message": "已取消收藏",
            "movie": removed["movie"]
        }
    else:
        raise HTTPException(status_code=404, detail="未找到该收藏")


@app.get("/api/favorites", tags=["收藏"])
async def get_favorites(
    sort_by: str = Query("added_at", regex="^(added_at|rating|year)$")
):
    """获取收藏列表"""
    fav_list = list(favorites.values())
    
    # 排序
    if sort_by == "added_at":
        fav_list.sort(key=lambda x: x["added_at"], reverse=True)
    elif sort_by == "rating":
        fav_list.sort(key=lambda x: x["movie"]["rating"], reverse=True)
    elif sort_by == "year":
        fav_list.sort(key=lambda x: x["movie"]["year"], reverse=True)
    
    return {
        "count": len(fav_list),
        "favorites": fav_list
    }


# ========== 统计功能 ==========

@app.get("/api/stats", tags=["统计"])
async def get_stats():
    """获取统计信息"""
    if not favorites:
        return {
            "total_favorites": 0,
            "message": "暂无收藏数据"
        }
    
    fav_movies = [f["movie"] for f in favorites.values()]
    
    # 统计类型分布
    genres_count = {}
    for movie in fav_movies:
        for genre in movie["genres"]:
            genres_count[genre] = genres_count.get(genre, 0) + 1
    
    # 统计年份分布
    years = [m["year"] for m in fav_movies if m["year"]]
    
    # 平均评分
    ratings = [m["rating"] for m in fav_movies if m["rating"] > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_favorites": len(favorites),
        "average_rating": round(avg_rating, 2),
        "genres_distribution": genres_count,
        "total_searches": len(search_history),
        "recent_searches": search_history[:10]
    }


@app.get("/api/search_history", tags=["统计"])
async def get_search_history(limit: int = Query(20, ge=1, le=100)):
    """获取搜索历史"""
    return {
        "total": len(search_history),
        "history": search_history[:limit]
    }


"""
🎯 运行说明：
1. 确保已创建 templates 和 static 目录
2. 运行：uvicorn main:app --reload
3. 访问 http://127.0.0.1:8000

📁 目录结构：
lesson2/
├── main.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js

🌟 功能特色：
1. ✅ 电影搜索（实时搜索）
2. ✅ Top250榜单
3. ✅ 正在热映/即将上映
4. ✅ 电影收藏功能
5. ✅ 搜索历史记录
6. ✅ 统计信息展示
7. ✅ 响应式界面设计

💡 课堂演示重点：
1. 前后端如何交互
2. API设计的RESTful风格
3. 数据持久化的思考（内存 vs 数据库）
4. 用户体验优化
"""

if __name__ == "__main__":
    import uvicorn
    print("🎬 TMDB 电影搜索系统启动中...")
    print(f"🌐 访问: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔑 API Key: {'已配置' if settings.TMDB_API_KEY else '未配置（使用模拟数据）'}")
    print(f"📊 模拟数据模式: {'开启' if settings.USE_MOCK_DATA else '关闭'}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)
