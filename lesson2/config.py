"""
配置管理模块
从环境变量或 .env 文件加载配置
"""
import os
from pathlib import Path
from typing import Optional


class Settings:
    """应用配置类"""
    
    def __init__(self):
        # 尝试加载 .env 文件
        self._load_dotenv()
        
        # TMDB API 配置
        self.TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
        self.TMDB_API_BASE: str = os.getenv("TMDB_API_BASE", "https://api.themoviedb.org/3")
        self.TMDB_IMAGE_BASE: str = os.getenv("TMDB_IMAGE_BASE", "https://image.tmdb.org/t/p/w500")
        
        # 服务器配置
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        
        # 应用配置
        self.USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
        self.TIMEOUT: float = float(os.getenv("TIMEOUT", "10.0"))
        
        # 验证必需配置
        self._validate()
    
    def _load_dotenv(self):
        """加载 .env 文件"""
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 只设置尚未设置的环境变量
                        if key and not os.getenv(key):
                            os.environ[key] = value
    
    def _validate(self):
        """验证必需的配置"""
        if not self.TMDB_API_KEY and not self.USE_MOCK_DATA:
            raise ValueError(
                "⚠️  未找到 TMDB_API_KEY！\n"
                "请执行以下步骤：\n"
                "1. 复制 .env.example 为 .env\n"
                "2. 在 https://www.themoviedb.org/settings/api 获取 API Key\n"
                "3. 将 API Key 填入 .env 文件的 TMDB_API_KEY\n"
                "或者设置 USE_MOCK_DATA=True 使用模拟数据"
            )
    
    def get_api_url(self, endpoint: str) -> str:
        """构建完整的 API URL"""
        return f"{self.TMDB_API_BASE}/{endpoint}"
    
    def get_image_url(self, path: Optional[str]) -> str:
        """构建完整的图片 URL"""
        if not path:
            return "/static/default-movie.jpg"
        return f"{self.TMDB_IMAGE_BASE}{path}"


# 创建全局配置实例
settings = Settings()


# 导出配置（方便使用）
__all__ = ['settings', 'Settings']
