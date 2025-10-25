#!/bin/bash
# 上传到 GitHub 前的准备脚本

echo "🔍 开始检查项目..."

# 进入项目目录
cd "$(dirname "$0")"

echo ""
echo "📋 第一步：检查敏感文件"
echo "================================"

# 检查 .env 是否会被忽略
if git check-ignore lesson2/.env > /dev/null 2>&1; then
    echo "✅ .env 文件会被正确忽略"
else
    echo "❌ 警告：.env 文件可能会被上传！"
    echo "   请检查 .gitignore 配置"
    exit 1
fi

# 检查 venv 是否会被忽略
if git check-ignore venv/ > /dev/null 2>&1; then
    echo "✅ venv/ 目录会被正确忽略"
else
    echo "⚠️  注意：venv/ 目录未被忽略（如果存在）"
fi

echo ""
echo "📋 第二步：检查必需文件"
echo "================================"

required_files=(
    "README.md"
    "STUDENT_GUIDE.md"
    "SETUP.md"
    "requirements.txt"
    ".gitignore"
    "lesson2/.env.example"
    "lesson2/config.py"
    "lesson2/main.py"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ 缺少: $file"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo ""
    echo "❌ 有文件缺失，请检查！"
    exit 1
fi

echo ""
echo "📋 第三步：检查 .env.example"
echo "================================"

if grep -q "your_api_key_here" lesson2/.env.example; then
    echo "✅ .env.example 使用示例 API Key"
elif grep -q "444d85391891a2a3bcdcb290e3cdb2cc" lesson2/.env.example; then
    echo "❌ 警告：.env.example 包含真实 API Key！"
    echo "   请替换为 'your_api_key_here'"
    exit 1
else
    echo "⚠️  .env.example 格式可能不正确"
fi

echo ""
echo "📋 第四步：检查代码中是否有硬编码密钥"
echo "================================"

if grep -r "444d85391891a2a3bcdcb290e3cdb2cc" lesson2/*.py 2>/dev/null | grep -v ".env"; then
    echo "❌ 警告：代码中发现硬编码的 API Key！"
    exit 1
else
    echo "✅ 代码中没有硬编码的 API Key"
fi

echo ""
echo "📋 第五步：测试配置文件"
echo "================================"

cd lesson2
if python3 -c "from config import settings; print(f'✅ config.py 可以正常加载')" 2>/dev/null; then
    echo "✅ config.py 加载成功"
else
    echo "❌ config.py 加载失败，请检查语法"
    exit 1
fi
cd ..

echo ""
echo "📋 第六步：Git 状态检查"
echo "================================"

git status --short

echo ""
echo "🎉 所有检查通过！"
echo ""
echo "📝 下一步操作："
echo "1. 查看将要提交的文件: git status"
echo "2. 添加文件: git add ."
echo "3. 提交: git commit -m \"feat: 初始提交 - TMDB电影搜索教学项目\""
echo "4. 推送: git push -u origin main"
echo ""
echo "⚠️  推送前最后确认："
echo "   - 运行: git ls-files | grep -E '\\.env$|venv/'"
echo "   - 应该没有任何输出"
echo ""
