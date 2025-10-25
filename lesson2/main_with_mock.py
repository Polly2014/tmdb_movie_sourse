"""
第二节课 - 完整的豆瓣电影Web应用（带模拟数据版本）
适用于豆瓣API不可用的情况
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

app = FastAPI(
    title="豆瓣电影搜索系统",
    description="完整的豆瓣电影搜索和收藏Web应用（带模拟数据）",
    version="4.0.0"
)

# ========== 配置静态文件和模板 ==========

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 豆瓣API配置
DOUBAN_API_BASE = "https://douban-api-docs.zce.me"
TIMEOUT = 5.0
USE_MOCK_DATA = True  # 设置为True使用模拟数据，False使用真实API

# ========== 内存存储 ==========
favorites: Dict[str, dict] = {}
search_history: List[dict] = []

# ========== 模拟数据 ==========

MOCK_MOVIES = [
    {
        "id": "1292052",
        "title": "肖申克的救赎",
        "original_title": "The Shawshank Redemption",
        "year": "1994",
        "rating": {"average": 9.7, "numRaters": 2800000},
        "genres": ["剧情", "犯罪"],
        "directors": [{"name": "弗兰克·德拉邦特"}],
        "casts": [
            {"name": "蒂姆·罗宾斯"},
            {"name": "摩根·弗里曼"},
            {"name": "鲍勃·冈顿"}
        ],
        "images": {"large": "https://img2.doubanio.com/view/photo/s_ratio_poster/public/p480747492.jpg"},
        "summary": "20世纪40年代末，小有成就的青年银行家安迪因涉嫌杀害妻子及她的情人而锒铛入狱。在这座名为肖申克的监狱内，希望似乎虚无缥缈，终身监禁的惩罚无疑注定了安迪接下来灰暗绝望的人生...",
        "alt": "https://movie.douban.com/subject/1292052/",
        "countries": ["美国"],
        "languages": ["英语"],
        "durations": ["142分钟"],
        "aka": ["月黑高飞", "刺激1995"]
    },
    {
        "id": "1291546",
        "title": "霸王别姬",
        "original_title": "霸王别姬",
        "year": "1993",
        "rating": {"average": 9.6, "numRaters": 2000000},
        "genres": ["剧情", "爱情"],
        "directors": [{"name": "陈凯歌"}],
        "casts": [
            {"name": "张国荣"},
            {"name": "张丰毅"},
            {"name": "巩俐"}
        ],
        "images": {"large": "https://img2.doubanio.com/view/photo/s_ratio_poster/public/p2561716440.jpg"},
        "summary": "段小楼（张丰毅）与程蝶衣（张国荣）是一对打小一起长大的师兄弟，两人一个演生，一个饰旦，一向配合天衣无缝，尤其一出《霸王别姬》，更是誉满京城...",
        "alt": "https://movie.douban.com/subject/1291546/",
        "countries": ["中国大陆", "香港"],
        "languages": ["汉语普通话"],
        "durations": ["171分钟"],
        "aka": ["Farewell My Concubine"]
    },
    {
        "id": "1292720",
        "title": "阿甘正传",
        "original_title": "Forrest Gump",
        "year": "1994",
        "rating": {"average": 9.5, "numRaters": 2200000},
        "genres": ["剧情", "爱情"],
        "directors": [{"name": "罗伯特·泽米吉斯"}],
        "casts": [
            {"name": "汤姆·汉克斯"},
            {"name": "罗宾·怀特"},
            {"name": "加里·西尼斯"}
        ],
        "images": {"large": "https://img2.doubanio.com/view/photo/s_ratio_poster/public/p2372307693.jpg"},
        "summary": "阿甘是个智商只有75的低能儿。在学校里为了躲避别的孩子的欺侮，听从一个朋友珍妮的话而开始"跑"。他跑着躲避别人的捉弄。在中学时，他为了躲避别人而跑进了一所学校的橄榄球场...",
        "alt": "https://movie.douban.com/subject/1292720/",
        "countries": ["美国"],
        "languages": ["英语"],
        "durations": ["142分钟"],
        "aka": ["福雷斯特·冈普"]
    },
    {
        "id": "1295644",
        "title": "这个杀手不太冷",
        "original_title": "Léon",
        "year": "1994",
        "rating": {"average": 9.4, "numRaters": 2100000},
        "genres": ["剧情", "动作", "犯罪"],
        "directors": [{"name": "吕克·贝松"}],
        "casts": [
            {"name": "让·雷诺"},
            {"name": "娜塔莉·波特曼"},
            {"name": "加里·奥德曼"}
        ],
        "images": {"large": "https://img2.doubanio.com/view/photo/s_ratio_poster/public/p511118051.jpg"},
        "summary": "里昂（让·雷诺）是名孤独的职业杀手，受人雇佣。一天，邻居家小姑娘马蒂尔达（娜塔丽·波特曼）敲开他的房门，要求在他那里暂时躲避一下...",
        "alt": "https://movie.douban.com/subject/1295644/",
        "countries": ["法国"],
        "languages": ["英语", "法语"],
        "durations": ["133分钟"],
        "aka": ["杀手莱昂", "Leon"]
    },
    {
        "id": "1292063",
        "title": "泰坦尼克号",
        "original_title": "Titanic",
        "year": "1997",
        "rating": {"average": 9.4, "numRaters": 1800000},
        "genres": ["剧情", "爱情", "灾难"],
        "directors": [{"name": "詹姆斯·卡梅隆"}],
        "casts": [
            {"name": "莱昂纳多·迪卡普里奥"},
            {"name": "凯特·温斯莱特"},
            {"name": "比利·赞恩"}
        ],
        "images": {"large": "https://img2.doubanio.com/view/photo/s_ratio_poster/public/p2896124000.jpg"},
        "summary": "1912年4月10日，号称"世界工业史上的奇迹"的豪华客轮泰坦尼克号开始了自己的处女航，从英国的南安普敦出发驶往美国纽约...",
        "alt": "https://movie.douban.com/subject/1292063/",
        "countries": ["美国"],
        "languages": ["英语"],
        "durations": ["194分钟"],
        "aka": []
    }
]

# 扩展更多电影
for i in range(20):
    MOCK_MOVIES.extend([
        {
            "id": f"mock_{i}_1",
            "title": f"经典电影 {i+1}",
            "original_title": f"Classic Movie {i+1}",
            "year": str(1990 + i % 30),
            "rating": {"average": round(7.5 + (i % 25) * 0.1, 1), "numRaters": 100000 + i * 10000},
            "genres": ["剧情", "动作"][i % 2:],
            "directors": [{"name": f"导演{i+1}"}],
            "casts": [{"name": f"演员{j}"} for j in range(1, 4)],
            "images": {"large": f"https://via.placeholder.com/300x450?text=Movie+{i+1}"},
            "summary": f"这是第 {i+1} 部精彩的电影...",
            "alt": f"https://movie.douban.com/subject/mock_{i}_1/",
            "countries": ["美国", "中国"][i % 2:i % 2 + 1],
            "languages": ["英语", "汉语"][i % 2:i % 2 + 1],
            "durations": ["120分钟"],
            "aka": []
        }
    ])

# ========== 数据模型 ==========

class MovieInfo(BaseModel):
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

# ========== 辅助函数 ==========

def parse_movie_data(data: dict) -> MovieInfo:
    """解析电影数据"""
    try:
        return MovieInfo(
            id=str(data.get('id', '')),
            title=data.get('title', ''),
            original_title=data.get('original_title', ''),
            year=data.get('year', ''),
            directors=[d.get('name', '') for d in data.get('directors', [])],
            actors=[a.get('name', '') for a in data.get('casts', [])[:5]],
            genres=data.get('genres', []),
            rating=float(data.get('rating', {}).get('average', 0)),
            rating_count=int(data.get('rating', {}).get('numRaters', 0)),
            cover=data.get('images', {}).get('large', ''),
            summary=data.get('summary', '')[:200] + '...' if data.get('summary', '') else ''
        )
    except Exception as e:
        print(f"解析电影数据出错: {e}")
        raise

async def fetch_from_douban(endpoint: str, params: dict = None) -> dict:
    """从豆瓣API获取数据，失败时使用模拟数据"""
    if USE_MOCK_DATA:
        # 使用模拟数据
        return get_mock_data(endpoint, params)
    
    url = f"{DOUBAN_API_BASE}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ API调用失败，使用模拟数据: {str(e)}")
        # API失败时降级使用模拟数据
        return get_mock_data(endpoint, params)

def get_mock_data(endpoint: str, params: dict = None) -> dict:
    """获取模拟数据"""
    params = params or {}
    
    if "search" in endpoint:
        # 搜索
        keyword = params.get('q', '').lower()
        results = [m for m in MOCK_MOVIES if keyword in m['title'].lower() or keyword in m.get('original_title', '').lower()]
        start = params.get('start', 0)
        count = params.get('count', 20)
        return {
            'subjects': results[start:start + count],
            'start': start,
            'count': len(results[start:start + count]),
            'total': len(results)
        }
    elif "top250" in endpoint:
        # Top250
        start = params.get('start', 0)
        count = params.get('count', 20)
        sorted_movies = sorted(MOCK_MOVIES[:50], key=lambda x: x['rating']['average'], reverse=True)
        return {
            'subjects': sorted_movies[start:start + count],
            'start': start,
            'count': len(sorted_movies[start:start + count]),
            'total': len(sorted_movies)
        }
    elif "in_theaters" in endpoint:
        # 正在热映
        count = params.get('count', 10)
        return {
            'subjects': MOCK_MOVIES[:count],
            'count': count,
            'total': count
        }
    elif "coming_soon" in endpoint:
        # 即将上映
        count = params.get('count', 10)
        return {
            'subjects': MOCK_MOVIES[5:5 + count],
            'count': count,
            'total': count
        }
    elif "subject" in endpoint:
        # 电影详情
        movie_id = endpoint.split('/')[-1]
        for movie in MOCK_MOVIES:
            if str(movie['id']) == str(movie_id):
                return movie
        return MOCK_MOVIES[0]  # 默认返回第一个
    
    return {'subjects': [], 'count': 0, 'total': 0}

# ========== 网页路由 ==========

@app.get("/", response_class=HTMLResponse, tags=["页面"])
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "豆瓣电影搜索系统",
            "current_year": datetime.now().year
        }
    )

# ========== API路由 ==========

@app.get("/api/search", tags=["API"])
async def search_movies(
    q: str = Query(..., min_length=1),
    start: int = Query(0, ge=0),
    count: int = Query(20, ge=1, le=50)
):
    """搜索电影"""
    params = {"q": q, "start": start, "count": count}
    data = await fetch_from_douban("v2/movie/search", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    # 记录搜索历史
    search_history.insert(0, {
        "keyword": q,
        "timestamp": datetime.now().isoformat(),
        "results_count": len(movies)
    })
    
    if len(search_history) > 50:
        search_history.pop()
    
    return {
        "count": len(movies),
        "start": data.get('start', 0),
        "total": data.get('total', 0),
        "movies": [m.dict() for m in movies]
    }

@app.get("/api/movie/{movie_id}", tags=["API"])
async def get_movie_detail(movie_id: str):
    """获取电影详情"""
    data = await fetch_from_douban(f"v2/movie/subject/{movie_id}", {})
    movie = parse_movie_data(data)
    
    is_favorite = movie_id in favorites
    
    return {
        "movie": movie.dict(),
        "is_favorite": is_favorite,
        "extra": {
            "countries": data.get('countries', []),
            "languages": data.get('languages', []),
            "duration": data.get('durations', [''])[0] if data.get('durations') else '',
            "aka": data.get('aka', []),
            "douban_url": data.get('alt', '')
        }
    }

@app.get("/api/top250", tags=["API"])
async def get_top250(
    start: int = Query(0, ge=0, le=225),
    count: int = Query(20, ge=1, le=100)
):
    """Top250"""
    params = {"start": start, "count": count}
    data = await fetch_from_douban("v2/movie/top250", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return {
        "count": len(movies),
        "start": data.get('start', 0),
        "total": data.get('total', 0),
        "movies": [m.dict() for m in movies]
    }

@app.get("/api/in_theaters", tags=["API"])
async def get_in_theaters(
    city: str = Query("北京"),
    count: int = Query(20, ge=1, le=50)
):
    """正在热映"""
    params = {"city": city, "count": count}
    data = await fetch_from_douban("v2/movie/in_theaters", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return {
        "count": len(movies),
        "movies": [m.dict() for m in movies]
    }

@app.get("/api/coming_soon", tags=["API"])
async def get_coming_soon(count: int = Query(20, ge=1, le=50)):
    """即将上映"""
    params = {"count": count}
    data = await fetch_from_douban("v2/movie/coming_soon", params)
    
    movies = [parse_movie_data(item) for item in data.get('subjects', [])]
    
    return {
        "count": len(movies),
        "movies": [m.dict() for m in movies]
    }

# ========== 收藏功能 ==========

@app.post("/api/favorites/{movie_id}", tags=["收藏"])
async def add_favorite(movie_id: str, note: str = ""):
    """添加收藏"""
    data = await fetch_from_douban(f"v2/movie/subject/{movie_id}", {})
    movie = parse_movie_data(data)
    
    favorites[movie_id] = {
        "movie": movie.dict(),
        "added_at": datetime.now().isoformat(),
        "note": note
    }
    
    return {
        "success": True,
        "message": "收藏成功",
        "movie": movie.dict()
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
    """统计信息"""
    if not favorites:
        return {
            "total_favorites": 0,
            "message": "暂无收藏数据"
        }
    
    fav_movies = [f["movie"] for f in favorites.values()]
    
    genres_count = {}
    for movie in fav_movies:
        for genre in movie["genres"]:
            genres_count[genre] = genres_count.get(genre, 0) + 1
    
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
    """搜索历史"""
    return {
        "total": len(search_history),
        "history": search_history[:limit]
    }

if __name__ == "__main__":
    import uvicorn
    print("🎬 豆瓣电影搜索系统启动中...")
    print(f"📊 使用{'模拟数据' if USE_MOCK_DATA else '真实API'}")
    print("🌐 访问: http://127.0.0.1:8000")
    print("📖 API文档: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
