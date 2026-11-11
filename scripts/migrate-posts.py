#!/usr/bin/env python3
"""
将 Jekyll (Chirpy) 博客的 _posts 迁移到 Astro 内容集合 src/content/blog。

用法：
  python3 scripts/migrate-posts.py [JEKYLL_REPO_DIR]
  默认 JEKYLL_REPO_DIR = ../../../../work/ghio 或环境变量 JEKYLL_DIR

做的事情：
  - 文件名中的日期 -> date；文件名 slug 化（空格 -> 连字符，小写）
  - 保留 title / tags，去掉 layout / header-style / catalog / author 等 Jekyll 专用字段
  - 修复空标签 / 异常标签；按标题与标签归类 series
  - 只复制文章引用到的图片，>300KB 的转换为 webp 并压缩
  - 图片改为相对路径（由 Astro 资源管线处理，自动适配 base 路径）
  - /assets/*.mp4 视频链接改为 <video>，指向原仓库固定 commit 的 jsDelivr CDN
  - 标题层级整体下降一级（页面已有 h1），并去掉与文章标题重复的首个 h1
"""
import os, re, sys, shutil, subprocess, hashlib, urllib.parse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("JEKYLL_DIR", "/workspace/work/ghio"))
POSTS = SRC / "_posts"
OUT = ROOT / "src" / "content" / "blog"
IMG_OUT = OUT / "images"
MEDIA_BASE = os.environ.get(
    "MEDIA_BASE",
    "https://cdn.jsdelivr.net/gh/zhouzhengjeff/zhouzhengjeff.github.io@cca264d5f188c0f9d9b538c1c7d78dbff7114933",
)
MAX_BYTES = 300_000

TAG_FIX = {"锻炼身体KKK": "锻炼身体", "潮流月刊": "潮流周刊"}
SLUG_FIX = {
    "2024-11-21-My-Daily": "2024-10-my-daily",
    "2025-01-08-11-My-Daily": "2024-11-my-daily",
    "2025-01-09-01-My-Daily": "2024-01-my-daily",
    "2024-11-05-2023-Sumarry": "2023-summary",
    "2025-02-07-2024-Life": "2024-life-beyond-work",
    "2025-01-23-My-Tools": "2024-my-tools",
}
DEFAULT_TAGS = {"2024-11-21-My-Daily.md": ["个人日常", "我的日常", "生活记录"]}


def slugify(stem: str) -> str:
    if stem in SLUG_FIX:
        return SLUG_FIX[stem]
    s = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    s = s.replace("Beyond Walking", "Beyond Working")  # 原文件名笔误
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s


def series_of(title: str, tags):
    t = title + " " + " ".join(tags)
    if "代码之外" in t or "Beyond Code" in t:
        return "beyond-code"
    if "Beyond Working" in title or "工作之外系列" in tags:
        return "beyond-working"
    if re.search(r"年总结|年度|^\d{4}年，", title):
        return "annual"
    return "daily"


def compress(src: Path, dst_noext: Path) -> Path:
    size = src.stat().st_size
    ext = src.suffix.lower()
    if ext == ".gif" or (size <= MAX_BYTES and ext in (".png", ".jpg", ".jpeg", ".webp")):
        dst = dst_noext.with_suffix(".jpg" if ext == ".jpeg" else ext)
        shutil.copyfile(src, dst)
        return dst
    dst = dst_noext.with_suffix(".webp")
    for dim, q in ((1600, 78), (1600, 66), (1400, 60), (1200, 55), (1000, 50)):
        subprocess.run(
            ["magick", str(src) + "[0]", "-auto-orient", "-strip", "-resize", f"{dim}x{dim}>",
             "-quality", str(q), str(dst)], check=True)
        if dst.stat().st_size <= MAX_BYTES:
            break
    return dst


def first_paragraph(body: str) -> str:
    in_code = False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s or s.startswith(("#", "!", "<", "|", "-", "*", "[", "```")):
            continue
        s = re.sub(r"^>\s*", "", s)
        s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"[*_`]", "", s)
        s = re.sub(r"^[\s\u200d\uFE0F\U00010000-\U0010FFFF\u2600-\u27BF]+", "", s).strip()
        if len(s) < 12:
            continue
        return (s[:110] + "…") if len(s) > 110 else s
    return ""


def yaml_str(v: str) -> str:
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def migrate():
    if OUT.exists():
        shutil.rmtree(OUT)
    IMG_OUT.mkdir(parents=True)
    count = 0
    img_total = 0
    for f in sorted(POSTS.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
        fm = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
        date = re.match(r"(\d{4}-\d{2}-\d{2})", f.name).group(1)
        slug = slugify(f.stem)
        title = str(fm.get("title", slug)).strip()
        tags = [str(t).strip() for t in (fm.get("tags") or []) if t and str(t).strip()]
        tags = [TAG_FIX.get(t, t) for t in tags]
        if not tags:
            tags = DEFAULT_TAGS.get(f.name, ["个人日常"])
        tags = list(dict.fromkeys(tags))
        series = series_of(title, tags)

        # --- 图片 ---
        (IMG_OUT / slug).mkdir(exist_ok=True)
        mapping = {}
        cover = None

        def img_repl(mm):
            nonlocal cover, img_total
            alt, target = mm.group(1), mm.group(2).strip()
            path = target.split(" ")[0]
            if not path.startswith("/images/"):
                return mm.group(0)
            if path not in mapping:
                srcp = SRC / urllib.parse.unquote(path.lstrip("/"))
                h = hashlib.md5(path.encode()).hexdigest()[:6]
                dst = compress(srcp, IMG_OUT / slug / f"img-{len(mapping) + 1:02d}-{h}")
                mapping[path] = f"./images/{slug}/{dst.name}"
                img_total += 1
                if cover is None:
                    cover = mapping[path]
            alt = re.sub(r"\.(png|jpe?g|gif|webp)$", "", alt, flags=re.I)
            return f"![{alt}]({mapping[path]})"

        body = re.sub(r"!\[([^\]]*)\]\(([^)]*\.(?:png|jpe?g|gif|webp)[^)]*)\)", img_repl, body, flags=re.I)

        # --- 视频 ---
        def vid_url(p):
            return MEDIA_BASE + urllib.parse.quote(p)

        def vid_line(mm):
            label, p = mm.group(2), mm.group(3)
            label = re.sub(r"\.mp4$", "", label)
            return (f'{mm.group(1)}<figure class="video"><video controls preload="none" playsinline '
                    f'src="{vid_url(p)}"></video><figcaption>{label}</figcaption></figure>')

        body = re.sub(r"(?m)^([ \t]*)\[([^\]]*)\]\((/assets/\S+?\.mp4)\)[ \t]*$", vid_line, body)
        body = re.sub(r"\[([^\]]*)\]\((/assets/\S+?\.mp4)\)",
                      lambda mm: f"[▶ {mm.group(1)}]({vid_url(mm.group(2))})", body)

        # --- 标题 ---
        lines, out, in_code, dropped = body.splitlines(), [], False, False
        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
            if not in_code and re.match(r"^#{1,5}\s", line):
                if not dropped and line.startswith("# ") and not any(l.strip() for l in out):
                    dropped = True
                    continue
                line = "#" + line
            out.append(line)
        body = "\n".join(out).strip() + "\n"

        desc = first_paragraph(body) or f"{title}。"
        front = ["---", f"title: {yaml_str(title)}", f"date: {date}",
                 f"description: {yaml_str(desc)}", f"series: {series}", "tags:"]
        front += [f"  - {yaml_str(t)}" for t in tags]
        if cover:
            front.append(f"cover: {yaml_str(cover)}")
        front.append(f"sourceFile: {yaml_str(f.name)}")
        front.append("---")
        (OUT / f"{slug}.md").write_text("\n".join(front) + "\n\n" + body, encoding="utf-8")
        count += 1
    print(f"migrated {count} posts, {img_total} images")


def migrate_about():
    raw = (SRC / "_tabs" / "about.md").read_text(encoding="utf-8")
    body = re.sub(r"^---.*?---\s*", "", raw, flags=re.S)
    lines = [re.sub(r"^>\s?", "", l).strip() for l in body.splitlines()]
    lines = [l for l in lines if l]
    data = ROOT / "src" / "data"
    data.mkdir(parents=True, exist_ok=True)
    out = ["// 由 scripts/migrate-posts.py 从 _tabs/about.md 生成，可直接编辑", "export const ABOUT: string[] = ["]
    out += ["  " + yaml_str(l) + "," for l in lines]
    out.append("];")
    (data / "about.ts").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"about: {len(lines)} paragraphs")


if __name__ == "__main__":
    migrate()
    migrate_about()
