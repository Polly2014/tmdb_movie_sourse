# 快速启动脚本 - Windows 版本

Write-Host "🎬 豆瓣电影搜索系统 - 环境设置" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 检查是否在项目目录
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ 错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查虚拟环境是否存在
if (-not (Test-Path "venv")) {
    Write-Host "📦 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
}

# 激活虚拟环境
Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 升级 pip
Write-Host "⬆️  升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q

# 安装依赖
Write-Host "📥 安装依赖包..." -ForegroundColor Yellow
pip install -r requirements.txt -q

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 环境设置完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 快速开始：" -ForegroundColor Cyan
    Write-Host "  cd lesson1"
    Write-Host "  uvicorn step1_hello_fastapi:app --reload"
    Write-Host ""
    Write-Host "🌐 访问：" -ForegroundColor Cyan
    Write-Host "  http://127.0.0.1:8000/docs"
    Write-Host ""
    Write-Host "💡 退出虚拟环境：" -ForegroundColor Cyan
    Write-Host "  deactivate"
    Write-Host ""
} else {
    Write-Host "❌ 依赖安装失败，请检查 requirements.txt" -ForegroundColor Red
    exit 1
}
