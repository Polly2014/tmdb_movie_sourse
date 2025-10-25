"""
第一节课 - Step 2: 构建基本的电影API
学习目标：
1. 设计RESTful API结构
2. 使用Pydantic进行数据验证
3. 实现增删改查（CRUD）操作
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="电影信息API",
    description="学习构建RESTful API",
    version="2.0.0"
)

# ========== 数据模型定义 ==========

class Movie(BaseModel):
    """电影数据模型"""
    id: int
    title: str = Field(..., description="电影名称")
    director: str = Field(..., description="导演")
    year: int = Field(..., ge=1900, le=2030, description="上映年份")
    rating: float = Field(..., ge=0, le=10, description="评分")
    genres: List[str] = Field(default=[], description="类型")
    description: Optional[str] = Field(None, description="简介")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "肖申克的救赎",
                "director": "弗兰克·德拉邦特",
                "year": 1994,
                "rating": 9.7,
                "genres": ["剧情", "犯罪"],
                "description": "一部经典的励志电影"
            }
        }


class MovieCreate(BaseModel):
    """创建电影时的数据模型（不包含id）"""
    title: str
    director: str
    year: int = Field(..., ge=1900, le=2030)
    rating: float = Field(..., ge=0, le=10)
    genres: List[str] = []
    description: Optional[str] = None


# ========== 模拟数据库 ==========

# 使用列表模拟数据库存储
movies_db: List[Movie] = [
    Movie(
        id=1,
        title="肖申克的救赎",
        director="弗兰克·德拉邦特",
        year=1994,
        rating=9.7,
        genres=["剧情", "犯罪"],
        description="两个被监禁的男人多年后建立了深厚的友谊"
    ),
    Movie(
        id=2,
        title="霸王别姬",
        director="陈凯歌",
        year=1993,
        rating=9.6,
        genres=["剧情", "爱情"],
        description="两位京剧伶人半个世纪的悲欢离合"
    ),
    Movie(
        id=3,
        title="阿甘正传",
        director="罗伯特·泽米吉斯",
        year=1994,
        rating=9.5,
        genres=["剧情", "爱情"],
        description="阿甘的传奇人生"
    ),
    Movie(
        id=4,
        title="泰坦尼克号",
        director="詹姆斯·卡梅隆",
        year=1997,
        rating=9.4,
        genres=["剧情", "爱情", "灾难"],
        description="在泰坦尼克号上发生的爱情故事"
    ),
    Movie(
        id=5,
        title="千与千寻",
        director="宫崎骏",
        year=2001,
        rating=9.4,
        genres=["动画", "奇幻"],
        description="少女千寻在神灵世界的冒险"
    )
]

# 用于生成新ID
next_id = 6


# ========== API端点 ==========

@app.get("/", tags=["首页"])
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用电影信息API",
        "docs": "/docs",
        "total_movies": len(movies_db)
    }


@app.get("/movies", response_model=List[Movie], tags=["电影"])
async def get_movies(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    genre: Optional[str] = Query(None, description="按类型筛选")
):
    """
    获取电影列表
    - 支持分页
    - 支持按类型筛选
    """
    movies = movies_db
    
    # 按类型筛选
    if genre:
        movies = [m for m in movies if genre in m.genres]
    
    # 分页
    return movies[skip: skip + limit]


@app.get("/movies/{movie_id}", response_model=Movie, tags=["电影"])
async def get_movie(movie_id: int):
    """
    获取单个电影信息
    """
    for movie in movies_db:
        if movie.id == movie_id:
            return movie
    
    # 如果没找到，返回404错误
    raise HTTPException(status_code=404, detail=f"电影ID {movie_id} 不存在")


@app.post("/movies", response_model=Movie, status_code=201, tags=["电影"])
async def create_movie(movie: MovieCreate):
    """
    创建新电影
    """
    global next_id
    
    # 创建新电影对象
    new_movie = Movie(
        id=next_id,
        **movie.dict()
    )
    
    # 添加到数据库
    movies_db.append(new_movie)
    next_id += 1
    
    return new_movie


@app.put("/movies/{movie_id}", response_model=Movie, tags=["电影"])
async def update_movie(movie_id: int, movie: MovieCreate):
    """
    更新电影信息
    """
    for i, existing_movie in enumerate(movies_db):
        if existing_movie.id == movie_id:
            updated_movie = Movie(id=movie_id, **movie.dict())
            movies_db[i] = updated_movie
            return updated_movie
    
    raise HTTPException(status_code=404, detail=f"电影ID {movie_id} 不存在")


@app.delete("/movies/{movie_id}", tags=["电影"])
async def delete_movie(movie_id: int):
    """
    删除电影
    """
    for i, movie in enumerate(movies_db):
        if movie.id == movie_id:
            deleted_movie = movies_db.pop(i)
            return {"message": "删除成功", "movie": deleted_movie}
    
    raise HTTPException(status_code=404, detail=f"电影ID {movie_id} 不存在")


@app.get("/movies/search/", response_model=List[Movie], tags=["搜索"])
async def search_movies(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    search_in: str = Query("title", regex="^(title|director)$", description="搜索字段")
):
    """
    搜索电影
    - 可以按标题或导演搜索
    """
    results = []
    q_lower = q.lower()
    
    for movie in movies_db:
        if search_in == "title" and q_lower in movie.title.lower():
            results.append(movie)
        elif search_in == "director" and q_lower in movie.director.lower():
            results.append(movie)
    
    return results


@app.get("/stats", tags=["统计"])
async def get_stats():
    """
    获取统计信息
    """
    if not movies_db:
        return {"message": "暂无电影数据"}
    
    total = len(movies_db)
    avg_rating = sum(m.rating for m in movies_db) / total
    
    # 统计类型
    genres_count = {}
    for movie in movies_db:
        for genre in movie.genres:
            genres_count[genre] = genres_count.get(genre, 0) + 1
    
    return {
        "total_movies": total,
        "average_rating": round(avg_rating, 2),
        "genres_distribution": genres_count,
        "year_range": {
            "earliest": min(m.year for m in movies_db),
            "latest": max(m.year for m in movies_db)
        }
    }


"""
🎯 运行说明：
1. 运行：uvicorn step2_basic_api:app --reload
2. 访问 http://127.0.0.1:8000/docs 测试所有API

💡 课堂练习：
1. 使用API文档添加一部新电影
2. 搜索包含"千寻"的电影
3. 获取评分大于9.5的电影（需要自己实现筛选端点）
4. 查看统计信息

🔍 思考问题：
1. 为什么创建电影使用POST，而不是GET？
2. PUT和DELETE的区别是什么？
3. 这个"数据库"有什么问题？（提示：重启服务器会怎样？）
"""

if __name__ == "__main__":
    import uvicorn
    print("🎬 电影API服务器启动中...")
    print("📖 API文档: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
