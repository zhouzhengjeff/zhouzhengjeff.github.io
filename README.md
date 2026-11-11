# 周正 · Zheng Zhou — 个人网站

## 简介

这是周正（Jeff Chou / 正哥 / 爪哇爹）的个人网站与博客：程序员、Java & AI Agent 讲师、创作者。

- **技术栈**：Astro 7（纯静态输出）+ TypeScript + 原生 CSS，无 UI 框架依赖
- **设计**：深海蓝紫科技风，中文优先；首页粒子网络画布、打字机角色切换、滚动渐显、卡片 3D 倾斜与鼠标高光；正文区保持纯净背景，长文阅读舒适（行高约 1.85，最大宽度约 72ch）
- **功能**：视频号「爪哇爹」AI 讲解短视频页 `/videos`（分类筛选、竖版卡片、弹窗播放器）、博客列表（标签筛选）、文章页（Shiki 代码高亮、阅读时长、目录 TOC、上一篇 / 下一篇）、标签页、归档时间线、关于页、404、RSS、Sitemap、robots.txt、SEO / Open Graph / JSON-LD
- **体验**：移动端适配、`prefers-reduced-motion` 时关闭动画、图片由 Astro 自动转 webp 并懒加载
- **内容来源**：全部来自原 Jekyll（Chirpy）博客仓库 `zhouzhengjeff/zhouzhengjeff.github.io` 的 `_posts`、`_tabs/about.md` 和 `images`

## 快速开始

需要 **Node.js ≥ 22.23.4**（Astro 7 的要求）和 npm。

```bash
npm ci            # 安装依赖（使用 package-lock.json 锁定版本）
npm run dev       # 本地开发：http://localhost:4321
npm run build     # 构建到 dist/
npm run preview   # 预览构建结果
npm run check     # 类型检查（astro check）
```

可选脚本（需要 Python 3）：

```bash
npm run migrate       # 重新从 Jekyll 仓库迁移文章（见下文）
npm run screenshots   # 用 Playwright 对 dist/ 截图，输出到 screenshots/
npm run check:links   # 检查 dist/ 中所有站内链接与资源是否存在
```

## 目录结构

```text
.
├── .github/workflows/deploy.yml   # GitHub Pages 自动部署
├── astro.config.mjs               # 站点配置（SITE / BASE 环境变量）
├── public/                        # 原样拷贝的静态文件（favicon、og.jpg、videos/*.mp4、posters/*.webp）
├── scripts/
│   ├── migrate-posts.py           # Jekyll → Astro 迁移脚本
│   └── screenshots.py             # 本地截图校验
├── screenshots/                   # 截图结果
└── src/
    ├── assets/                    # 头像、签名字体（经 Vite 处理，自动适配 base）
    ├── components/                # Header / Footer / Hero / PostCard / Toc / Icon
    ├── content/blog/              # 文章（Markdown）与文章图片 images/<slug>/
    ├── content.config.ts          # 内容集合 schema
    ├── consts.ts                  # 站点信息、导航、系列、技能
    ├── data/about.ts              # 关于我（由 about.md 生成）
    ├── data/videos.json           # 视频号视频清单（最新在前）
    ├── data/videos.ts             # 视频清单类型、频道数据、分类与路径工具
    ├── layouts/BaseLayout.astro   # SEO、页头页脚、全局交互脚本
    ├── pages/                     # 路由：/、/blog、/blog/[slug]、/tags、/tags/[tag]、/videos、/archive、/about、404、rss.xml、robots.txt、posts/[old]（旧地址跳转）
    ├── styles/global.css          # 设计变量与全局样式
    └── utils/index.ts             # base 路径、日期、阅读时长、标签工具
```

### 写新文章

在 `src/content/blog/` 新建 `my-post.md`（文件名即 URL：`/blog/my-post/`）：

```markdown
---
title: "文章标题"
date: 2026-01-01
description: "一句话摘要（用于卡片与 SEO）"
series: beyond-working   # 可选：beyond-working | daily | annual | beyond-code
tags:
  - Java
  - AI Agent
cover: "./images/my-post/cover.webp"   # 可选：封面图
---

正文从二级标题（##）开始，目录会自动生成。
```

图片放在 `src/content/blog/images/my-post/`，正文用相对路径 `![说明](./images/my-post/xxx.webp)` 引用，构建时会自动压缩并加上 base 前缀。

### 添加视频号视频

1. 把竖版视频（建议 540×960、≤ 6MB 的 H.264 mp4）放到 `public/videos/<slug>.mp4`，封面放到 `public/posters/<slug>.webp`。
2. 在 `src/data/videos.json` 顶部追加一条：

```json
{ "slug": "2026-11-12-xxx", "title": "标题", "date": "2026-11-12", "duration_sec": 300, "width": 540, "height": 960,
  "poster": "posters/2026-11-12-xxx.webp", "src": "videos/2026-11-12-xxx.mp4", "size_mb": 4.2,
  "category": "AI Agent", "description": "一句话简介" }
```

分类配色与顺序在 `src/data/videos.ts` 的 `CATEGORY_META`，频道数据（关注、获赞等）在 `CHANNEL`。首页自动展示最新 8 个，`/videos` 展示全部；路径会自动加上 `BASE` 前缀，视频只在点击播放时才加载（`preload="none"`）。

### 从 Jekyll 重新迁移

```bash
JEKYLL_DIR=/path/to/zhouzhengjeff.github.io npm run migrate
```

迁移脚本会：从文件名取日期并生成 slug；只保留 `title / tags`，丢弃 `layout / header-style / catalog / author`；修复空标签和异常标签；按标题与标签归入四个系列；只复制被引用的图片，> 300KB 的转为 webp 压缩；标题层级整体下降一级；把 `/assets/*.mp4` 视频链接转为 `<video>` 播放器。

> 原仓库的视频合计约 650MB，不适合放进本站仓库，因此视频通过 jsDelivr 从原仓库的**固定 commit** 加载（`MEDIA_BASE` 环境变量可改）。如果将来删除原仓库或改写其历史，需要把视频迁到其它存储并重新运行迁移。

## 部署到 GitHub Pages

1. 在 GitHub 新建仓库并推送本项目（用户主页仓库 `zhouzhengjeff.github.io` 或任意项目仓库均可）。
2. 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
3. 推送到 `main` 分支后，`.github/workflows/deploy.yml` 会自动执行：Node 22 → `npm ci` → `npm run build` → `actions/upload-pages-artifact` → `actions/deploy-pages`。

站点地址与子路径由环境变量控制（`deploy.yml` 中已写明用户主页仓库的 `SITE=https://zhouzhengjeff.github.io`、`BASE=/`；如部署到项目仓库，请把 `BASE` 改为 `/<仓库名>/`）：

| 变量   | 默认值                            | 说明                                                 |
| ------ | --------------------------------- | ---------------------------------------------------- |
| `SITE` | `https://zhouzhengjeff.github.io` | 站点根地址，用于 canonical、RSS、Sitemap、OG         |
| `BASE` | `/`                               | 子路径。项目仓库部署时为 `/<仓库名>/`                |

本地模拟项目仓库部署：

```bash
SITE=https://zhouzhengjeff.github.io BASE=/my-site/ npm run build
```

> 新文章地址统一为 `/blog/<slug>/`。为了不让旧链接失效，构建时会为每篇文章生成旧 Jekyll 地址 `/posts/<原文件名>/` 的静态跳转页（noindex，不进入 Sitemap）。

## 许可

- 文章与图片版权归周正所有。
- 签名字体子集来自 [Great Vibes](https://github.com/googlefonts/great-vibes)（SIL Open Font License，见 `src/assets/fonts/GreatVibes-OFL.txt`）。
