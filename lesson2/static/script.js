// 全局状态
let currentPage = 0;
const pageSize = 20;

// ==================== 工具函数 ====================

// 显示加载动画
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

// 隐藏加载动画
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// 显示toast提示
function showToast(message, type = 'info') {
    // 简单的提示实现
    alert(message);
}

// ==================== 标签页切换 ====================

// 记录已加载的标签页，避免重复加载
const loadedTabs = new Set(['search']); // 搜索页默认已加载

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // 切换按钮状态
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // 切换内容
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`).classList.add('active');
        
        // 只在首次访问时加载内容，避免重复加载导致闪烁
        if (!loadedTabs.has(tab)) {
            loadedTabs.add(tab);
            if (tab === 'top250') loadTop250(0);
            else if (tab === 'theaters') loadTheaters();
            else if (tab === 'favorites') loadFavorites();
            else if (tab === 'stats') loadStats();
        }
    });
});

// ==================== 电影卡片渲染 ====================

function createMovieCard(movie, showFavoriteBtn = false) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    
    const rating = movie.rating > 0 ? `⭐ ${movie.rating}` : '暂无评分';
    const year = movie.year || '未知';
    
    card.innerHTML = `
        <img src="${movie.cover || '/static/default-movie.jpg'}" 
             alt="${movie.title}" 
             class="movie-cover"
             onerror="this.src='/static/default-movie.jpg'">
        <div class="movie-info">
            <div class="movie-title" title="${movie.title}">${movie.title}</div>
            <div class="movie-rating">${rating}</div>
            <div class="movie-year">${year}</div>
            <div class="movie-genres">
                ${movie.genres.slice(0, 3).map(g => `<span class="genre-tag">${g}</span>`).join('')}
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => showMovieDetail(movie.id));
    
    return card;
}

// ==================== 搜索功能 ====================

async function searchMovies(keyword) {
    if (!keyword.trim()) {
        showToast('请输入搜索关键词');
        return;
    }
    
    showLoading();
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '';
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(keyword)}&count=20`);
        
        // 检查响应状态
        if (!response.ok) {
            const errorData = await response.json();
            hideLoading();
            
            const errorMsg = errorData.detail?.message || errorData.detail || '搜索失败';
            resultsDiv.innerHTML = `
                <div class="empty-state">
                    <p>😢 ${errorMsg}</p>
                    <p style="font-size: 0.9rem; color: #999; margin-top: 1rem;">
                        可能原因：<br>
                        1. TMDB API 暂时不可用<br>
                        2. 网络连接问题<br>
                        3. 请稍后重试
                    </p>
                </div>
            `;
            return;
        }
        
        const data = await response.json();
        
        hideLoading();
        
        // 检查数据格式
        if (!data || !data.movies || !Array.isArray(data.movies)) {
            resultsDiv.innerHTML = '<div class="empty-state"><p>😢 数据格式错误</p></div>';
            return;
        }
        
        if (data.movies.length === 0) {
            resultsDiv.innerHTML = '<div class="empty-state"><p>😢 没有找到相关电影</p></div>';
            return;
        }
        
        data.movies.forEach(movie => {
            resultsDiv.appendChild(createMovieCard(movie));
        });
        
        document.getElementById('search-tips').textContent = 
            `找到 ${data.total} 个结果，显示前 ${data.movies.length} 个`;
            
    } catch (error) {
        hideLoading();
        console.error('搜索错误:', error);
        resultsDiv.innerHTML = `
            <div class="empty-state">
                <p>😢 搜索出错了</p>
                <p style="font-size: 0.9rem; color: #999;">错误信息: ${error.message}</p>
                <p style="font-size: 0.9rem; color: #999; margin-top: 1rem;">
                    提示：可以尝试切换到 "Top250" 或 "热映" 标签查看示例数据
                </p>
            </div>
        `;
    }
}

// 绑定搜索事件
document.getElementById('search-btn').addEventListener('click', () => {
    const keyword = document.getElementById('search-input').value;
    searchMovies(keyword);
});

document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const keyword = e.target.value;
        searchMovies(keyword);
    }
});

// ==================== Top250 ====================

// 防止重复加载
let isLoadingTop250 = false;

async function loadTop250(page = 0) {
    if (isLoadingTop250) return;
    isLoadingTop250 = true;
    
    showLoading();
    const resultsDiv = document.getElementById('top250-results');
    
    try {
        const start = page * pageSize;
        const response = await fetch(`/api/top250?start=${start}&count=${pageSize}`);
        const data = await response.json();
        
        // 使用 DocumentFragment 减少重绘
        const fragment = document.createDocumentFragment();
        data.movies.forEach(movie => {
            fragment.appendChild(createMovieCard(movie));
        });
        
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(fragment);
        
        hideLoading();
        
        // 更新分页
        currentPage = page;
        document.getElementById('top250-page-info').textContent = `第 ${page + 1} 页`;
        document.getElementById('top250-prev').disabled = page === 0;
        document.getElementById('top250-next').disabled = start + pageSize >= data.total;
        
    } catch (error) {
        hideLoading();
        showToast('加载失败: ' + error.message);
    } finally {
        isLoadingTop250 = false;
    }
}

// 分页按钮
document.getElementById('top250-prev').addEventListener('click', () => {
    if (currentPage > 0) loadTop250(currentPage - 1);
});

document.getElementById('top250-next').addEventListener('click', () => {
    loadTop250(currentPage + 1);
});

// ==================== 热映电影 ====================

// 防止重复加载
let isLoadingTheaters = false;

async function loadTheaters() {
    // 防止重复调用
    if (isLoadingTheaters) return;
    isLoadingTheaters = true;
    
    const city = document.getElementById('city-select').value;
    const theatersDiv = document.getElementById('theaters-results');
    const comingDiv = document.getElementById('coming-results');
    
    // 只在内容为空时显示加载动画，避免闪烁
    if (!theatersDiv.children.length) {
        theatersDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    if (!comingDiv.children.length) {
        comingDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    
    try {
        // 并行请求两个接口，减少等待时间
        const [theatersRes, comingRes] = await Promise.all([
            fetch(`/api/in_theaters?city=${encodeURIComponent(city)}`),
            fetch('/api/coming_soon')
        ]);
        
        const theatersData = await theatersRes.json();
        const comingData = await comingRes.json();
        
        // 使用 DocumentFragment 减少重绘次数
        const theatersFragment = document.createDocumentFragment();
        theatersData.movies.forEach(movie => {
            theatersFragment.appendChild(createMovieCard(movie));
        });
        theatersDiv.innerHTML = '';
        theatersDiv.appendChild(theatersFragment);
        
        const comingFragment = document.createDocumentFragment();
        comingData.movies.forEach(movie => {
            comingFragment.appendChild(createMovieCard(movie));
        });
        comingDiv.innerHTML = '';
        comingDiv.appendChild(comingFragment);
        
    } catch (error) {
        showToast('加载失败: ' + error.message);
        theatersDiv.innerHTML = '<div class="empty-state"><p>😢 加载失败</p></div>';
        comingDiv.innerHTML = '<div class="empty-state"><p>😢 加载失败</p></div>';
    } finally {
        isLoadingTheaters = false;
    }
}

// 添加防抖机制
let cityChangeTimer = null;
document.getElementById('city-select').addEventListener('change', () => {
    if (cityChangeTimer) clearTimeout(cityChangeTimer);
    cityChangeTimer = setTimeout(() => {
        loadTheaters();
    }, 300); // 300ms 防抖延迟
});

// ==================== 收藏功能 ====================

// 防止重复加载
let isLoadingFavorites = false;

async function loadFavorites() {
    if (isLoadingFavorites) return;
    isLoadingFavorites = true;
    
    const sortBy = document.getElementById('favorites-sort').value;
    const resultsDiv = document.getElementById('favorites-results');
    const emptyDiv = document.getElementById('empty-favorites');
    
    // 只在首次加载时显示加载动画
    if (!resultsDiv.children.length && emptyDiv.style.display === 'none') {
        resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    
    try {
        const response = await fetch(`/api/favorites?sort_by=${sortBy}`);
        const data = await response.json();
        
        if (data.favorites.length === 0) {
            resultsDiv.innerHTML = '';
            emptyDiv.style.display = 'block';
            return;
        }
        
        emptyDiv.style.display = 'none';
        
        // 使用 DocumentFragment 减少重绘
        const fragment = document.createDocumentFragment();
        data.favorites.forEach(fav => {
            fragment.appendChild(createMovieCard(fav.movie, true));
        });
        
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(fragment);
        
    } catch (error) {
        showToast('加载失败: ' + error.message);
    } finally {
        isLoadingFavorites = false;
    }
}

// 添加防抖机制
let favoriteSortTimer = null;
document.getElementById('favorites-sort').addEventListener('change', () => {
    if (favoriteSortTimer) clearTimeout(favoriteSortTimer);
    favoriteSortTimer = setTimeout(() => {
        loadFavorites();
    }, 200);
});

async function addToFavorites(movieId) {
    try {
        const response = await fetch(`/api/favorites/${movieId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('✅ 收藏成功！');
            return true;
        }
    } catch (error) {
        showToast('收藏失败: ' + error.message);
        return false;
    }
}

async function removeFromFavorites(movieId) {
    try {
        const response = await fetch(`/api/favorites/${movieId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('已取消收藏');
            return true;
        }
    } catch (error) {
        showToast('取消失败: ' + error.message);
        return false;
    }
}

// ==================== 电影详情 ====================

async function showMovieDetail(movieId) {
    const modal = document.getElementById('movie-modal');
    const detailDiv = document.getElementById('movie-detail');
    
    detailDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    modal.style.display = 'block';
    
    try {
        const response = await fetch(`/api/movie/${movieId}`);
        const data = await response.json();
        const movie = data.movie;
        const extra = data.extra;
        
        const favoriteBtn = data.is_favorite
            ? `<button class="btn btn-danger" onclick="handleRemoveFavorite('${movieId}')">💔 取消收藏</button>`
            : `<button class="btn btn-primary" onclick="handleAddFavorite('${movieId}')">❤️ 加入收藏</button>`;
        
        detailDiv.innerHTML = `
            <div class="movie-detail-content">
                <div>
                    <img src="${movie.cover}" alt="${movie.title}" class="detail-cover">
                    <div class="detail-actions">
                        ${favoriteBtn}
                        <a href="${extra.douban_url}" target="_blank" class="btn btn-primary">
                            🔗 TMDB 链接
                        </a>
                    </div>
                </div>
                <div class="detail-info">
                    <h2>${movie.title}</h2>
                    <p><strong>原名：</strong>${movie.original_title || movie.title}</p>
                    <p><strong>评分：</strong>⭐ ${movie.rating} (${movie.rating_count} 人评价)</p>
                    <p><strong>年份：</strong>${movie.year}</p>
                    <p><strong>导演：</strong>${movie.directors.join(', ')}</p>
                    <p><strong>主演：</strong>${movie.actors.join(', ')}</p>
                    <p><strong>类型：</strong>${movie.genres.join(' / ')}</p>
                    <p><strong>制片国家/地区：</strong>${extra.countries.join(' / ')}</p>
                    <p><strong>语言：</strong>${extra.languages.join(' / ')}</p>
                    <p><strong>片长：</strong>${extra.duration}</p>
                    <p><strong>简介：</strong></p>
                    <p>${movie.summary || '暂无简介'}</p>
                </div>
            </div>
        `;
        
    } catch (error) {
        detailDiv.innerHTML = `<p>加载失败: ${error.message}</p>`;
    }
}

// 处理收藏按钮点击
async function handleAddFavorite(movieId) {
    const success = await addToFavorites(movieId);
    if (success) {
        showMovieDetail(movieId); // 刷新详情
    }
}

async function handleRemoveFavorite(movieId) {
    const success = await removeFromFavorites(movieId);
    if (success) {
        showMovieDetail(movieId); // 刷新详情
        loadFavorites(); // 刷新收藏列表
    }
}

// 关闭模态框
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('movie-modal').style.display = 'none';
});

window.addEventListener('click', (e) => {
    const modal = document.getElementById('movie-modal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// ==================== 统计功能 ====================

// 防止重复加载
let isLoadingStats = false;

async function loadStats() {
    if (isLoadingStats) return;
    isLoadingStats = true;
    
    const statsDiv = document.getElementById('stats-content');
    
    // 只在内容为空时显示加载动画
    if (!statsDiv.children.length) {
        statsDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.total_favorites === 0) {
            statsDiv.innerHTML = '<div class="empty-state"><p>暂无统计数据</p></div>';
            return;
        }
        
        // 类型分布
        const genresHtml = Object.entries(data.genres_distribution)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([genre, count]) => `<li>${genre}: ${count} 部</li>`)
            .join('');
        
        // 最近搜索
        const searchesHtml = data.recent_searches
            .map(s => `<li>${s.keyword} (${s.results_count} 个结果)</li>`)
            .join('');
        
        statsDiv.innerHTML = `
            <div class="stat-card">
                <h3>📊 收藏统计</h3>
                <div class="stat-value">${data.total_favorites}</div>
                <p>部电影</p>
            </div>
            
            <div class="stat-card">
                <h3>⭐ 平均评分</h3>
                <div class="stat-value">${data.average_rating}</div>
                <p>你的品味不错！</p>
            </div>
            
            <div class="stat-card">
                <h3>🔍 搜索次数</h3>
                <div class="stat-value">${data.total_searches}</div>
                <p>次搜索</p>
            </div>
            
            <div class="stat-card">
                <h3>🎭 类型分布</h3>
                <ul class="stat-list">
                    ${genresHtml}
                </ul>
            </div>
            
            <div class="stat-card">
                <h3>📜 最近搜索</h3>
                <ul class="stat-list">
                    ${searchesHtml || '<li>暂无搜索记录</li>'}
                </ul>
            </div>
        `;
        
    } catch (error) {
        statsDiv.innerHTML = `<p>加载失败: ${error.message}</p>`;
    } finally {
        isLoadingStats = false;
    }
}

// ==================== 页面初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎬 TMDB 电影搜索系统已加载');
});
