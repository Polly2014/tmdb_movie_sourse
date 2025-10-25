# ✅ GitHub 上传前检查清单

在将项目推送到 GitHub 之前，请确认以下事项：

## 🔐 安全检查

- [ ] `.env` 文件已在 `.gitignore` 中
- [ ] `venv/` 目录已在 `.gitignore` 中
- [ ] 代码中没有硬编码的 API Key
- [ ] `.env.example` 中的示例 Key 是假的
- [ ] 个人笔记文件已在 `.gitignore` 中

## 📁 文件检查

### 应该包含的文件
- [ ] `README.md` - 项目介绍
- [ ] `STUDENT_GUIDE.md` - 学生使用指南
- [ ] `SETUP.md` - 配置指南
- [ ] `requirements.txt` - 依赖列表
- [ ] `.gitignore` - Git 忽略规则
- [ ] `.env.example` - 环境变量示例
- [ ] `lesson1/` - 第一课代码
- [ ] `lesson2/` - 第二课代码
- [ ] `lesson2/config.py` - 配置管理
- [ ] `lesson2/templates/` - HTML 模板
- [ ] `lesson2/static/` - 静态资源

### 不应该包含的文件
- [ ] `.env` - 环境变量（包含真实 API Key）
- [ ] `venv/` - 虚拟环境
- [ ] `__pycache__/` - Python 缓存
- [ ] `.DS_Store` - macOS 系统文件
- [ ] `PPT_OUTLINE.md` - 个人笔记
- [ ] `BUGFIX_*.md` - 开发笔记

## 🧪 功能测试

- [ ] lesson1 可以正常运行
- [ ] lesson2 使用模拟数据可以运行
- [ ] lesson2 使用真实 API 可以运行
- [ ] 所有链接正确（README 等）
- [ ] API 文档可以访问
- [ ] 前端页面可以正常显示

## 📝 文档检查

- [ ] README.md 完整且清晰
- [ ] STUDENT_GUIDE.md 包含所有必要信息
- [ ] 代码注释充分
- [ ] API 端点有文档字符串
- [ ] 配置说明清楚

## 🚀 执行检查

### 1. 检查将要提交的文件

```bash
cd /Users/polly/Downloads/Sublime_Workspace/GitHub_Workspace/PlayGround_Python/tmdb_movie_sourse
git status
```

### 2. 查看 .gitignore 是否生效

```bash
git status --ignored
```

### 3. 确认敏感文件不在列表中

```bash
# 应该看不到这些文件
git ls-files | grep -E "\.env$|venv/|PPT_OUTLINE"
```

如果看到敏感文件，执行：
```bash
git rm --cached .env
git rm --cached -r venv/
```

### 4. 添加所有文件

```bash
git add .
```

### 5. 再次确认

```bash
git status
```

### 6. 提交

```bash
git commit -m "feat: 完整的 TMDB 电影搜索教学项目

- 添加 lesson1 基础教程
- 添加 lesson2 完整应用
- 配置管理和环境变量分离
- 完善文档和学生指南
- 保护 API Key 安全"
```

### 7. 推送到 GitHub

```bash
git remote add origin https://github.com/Polly2014/tmdb_movie_sourse.git
git branch -M main
git push -u origin main
```

## 🔍 上传后验证

在 GitHub 上检查：

- [ ] 在线预览 README.md 正常
- [ ] 代码高亮正常
- [ ] 文件结构清晰
- [ ] 没有 .env 文件
- [ ] 没有 venv/ 目录
- [ ] Issues 和 Discussions 已启用（可选）

## 📊 GitHub 仓库设置建议

### About 部分
- **Description**: FastAPI 电影搜索系统 - Python Web 开发教学项目
- **Website**: (如果有部署的演示)
- **Topics**: `fastapi`, `python`, `教学`, `tmdb-api`, `web开发`

### Settings
- [ ] Issues 开启（学生可以提问）
- [ ] Discussions 开启（讨论区）
- [ ] Wiki 开启（可选）
- [ ] 设置 License (MIT)

### README.md Badges（可选）
```markdown
![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
```

## ✨ 完成！

所有检查通过后，你的项目就可以安全地分享给学生了！

---

**记住**: 
- 🔒 永远不要上传 `.env` 文件
- 📚 保持文档更新
- 🐛 及时响应学生的 Issues
- 🎯 持续改进代码质量
