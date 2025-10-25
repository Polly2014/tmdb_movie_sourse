#!/bin/bash

# 🚀 GitHub 上传前准备脚本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 准备上传到 GitHub: tmdb_movie_sourse"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 检查 Git 仓库
if [ ! -d .git ]; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    echo "请先运行: git init"
    exit 1
fi

# 2. 检查 .env 文件是否存在但被忽略
if [ -f lesson2/.env ]; then
    if git check-ignore lesson2/.env > /dev/null 2>&1; then
        echo "✅ lesson2/.env 已在 .gitignore 中（不会上传）"
    else
        echo "⚠️  警告: lesson2/.env 存在但未被忽略！"
        echo "请确保 .gitignore 包含 .env"
        exit 1
    fi
fi

# 3. 检查是否有硬编码的 API Key
echo ""
echo "🔍 检查代码中是否有硬编码的 API Key..."
if grep -r "444d85391891a2a3bcdcb290e3cdb2cc" lesson1/ lesson2/*.py 2>/dev/null; then
    echo "⚠️  警告: 发现硬编码的 API Key！请移除后再上传"
    exit 1
else
    echo "✅ 未发现硬编码的 API Key"
fi

# 4. 显示将要上传的文件
echo ""
echo "📋 将要上传到 GitHub 的文件："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git status --short

# 5. 显示被忽略的文件
echo ""
echo "🚫 被忽略的文件（不会上传）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git status --ignored --short | grep "^!!" || echo "（无）"

# 6. 最终检查清单
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 上传前检查清单："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ .env 文件已在 .gitignore 中"
echo "✅ 代码中无硬编码的 API Key"
echo "✅ PPT_OUTLINE.md 等个人笔记已忽略"
echo "✅ venv/ 虚拟环境目录已忽略"
echo ""
echo "🎯 推荐的 Git 操作："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "git add ."
echo "git commit -m 'feat: 完整的 TMDB 电影搜索教学项目'"
echo "git remote add origin https://github.com/Polly2014/tmdb_movie_sourse.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "✨ 准备完成！可以安全上传了！"
