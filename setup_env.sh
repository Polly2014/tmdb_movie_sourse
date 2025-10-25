#!/bin/bash

# 豆瓣电影项目 - 环境设置脚本

echo "🎬 豆瓣电影搜索系统 - 环境设置"
echo "================================"

# 检查是否在项目目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo "✅ 虚拟环境创建成功"
    else
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip -q

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 环境设置完成！"
    echo ""
    echo "📚 快速开始："
    echo "  cd lesson1"
    echo "  uvicorn step1_hello_fastapi:app --reload"
    echo ""
    echo "🌐 访问："
    echo "  http://127.0.0.1:8000/docs"
    echo ""
    echo "💡 退出虚拟环境："
    echo "  deactivate"
    echo ""
else
    echo "❌ 依赖安装失败，请检查 requirements.txt"
    exit 1
fi
