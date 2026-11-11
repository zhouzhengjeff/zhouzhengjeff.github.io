"""本地截图校验：python3 scripts/screenshots.py [BASE_URL]"""
import sys, json, threading, functools, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if len(sys.argv) > 1:
    BASE = sys.argv[1]
else:
    # 未指定地址时，内置静态服务器托管 dist/
    handler = functools.partial(SimpleHTTPRequestHandler, directory=os.path.join(ROOT, "dist"))
    handler.log_message = lambda *a, **k: None
    srv = ThreadingHTTPServer(("127.0.0.1", 4329), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    BASE = "http://127.0.0.1:4329"
os.chdir(ROOT)
SHOTS = [
    ("home-desktop-1440.png", "/", 1440, 900, True),
    ("home-hero-desktop-1440.png", "/", 1440, 900, False),
    ("home-mobile-390.png", "/", 390, 844, True),
    ("post-desktop-1440.png", "/blog/beyond-working-serials-efficient-life-and-work/", 1440, 900, False),
    ("post-mobile-390.png", "/blog/2023-summary/", 390, 844, False),
    ("blog-desktop-1440.png", "/blog/", 1440, 900, False),
    ("videos-desktop-1440.png", "/videos/", 1440, 900, True),
    ("videos-mobile-390.png", "/videos/", 390, 844, True),
    ("home-videos-desktop-1440.png", "/", 1440, 900, "#videos"),
    ("home-videos-mobile-390.png", "/", 390, 844, "#videos"),
    ("videos-modal-desktop-1440.png", "/videos/", 1440, 900, "modal"),
    ("videos-modal-mobile-390.png", "/videos/", 390, 844, "modal"),
]
report = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, path, w, h, full in SHOTS:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(BASE + path, wait_until="networkidle")
        pg.add_style_tag(content="html{scroll-behavior:auto !important}")
        # 触发所有 reveal 动画，便于整页截图
        pg.evaluate("""async () => {
          document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible'));
          document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; });
          await Promise.all([...document.images].map(i => i.decode().catch(() => null)));
          for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
          window.scrollTo(0, 0);
        }""")
        pg.wait_for_timeout(1800)
        info = pg.evaluate("""() => {
          const de = document.documentElement;
          const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.loading !== 'lazy').map(i => i.src);
          const wide = [...document.querySelectorAll('body *')].filter(el => { const r = el.getBoundingClientRect(); return r.right > de.clientWidth + 1 && getComputedStyle(el).position !== 'fixed'; }).slice(0, 8).map(el => el.tagName + '.' + el.className);
          return { scrollW: de.scrollWidth, clientW: de.clientWidth, height: de.scrollHeight, broken, wide };
        }""")
        info["errors"] = errors
        report[name] = info
        if name.startswith("post-mobile"):
            pg.evaluate("() => { const m = document.querySelector('.prose img, .prose figure'); if (m) { m.scrollIntoView({block: 'center'}); } }")
            pg.wait_for_timeout(600)
            pg.screenshot(path="screenshots/post-mobile-390-media.png")
            pg.evaluate("() => window.scrollTo(0, 0)")
            pg.wait_for_timeout(400)
        if full == "modal":
            # 打开播放器（不自动播放，避免下载视频），检查 Esc 能关闭
            pg.evaluate("() => { HTMLMediaElement.prototype.play = function () { return Promise.resolve(); }; }")
            pg.click("[data-video-open] >> nth=1")
            pg.wait_for_timeout(700)
            pg.screenshot(path=f"screenshots/{name}")
            info["modal_open"] = pg.evaluate("() => document.getElementById('video-dialog').open")
            info["modal_src"] = pg.evaluate("() => document.getElementById('vp-video').getAttribute('src')")
            pg.keyboard.press("ArrowRight")
            info["after_next"] = pg.evaluate("() => document.getElementById('vp-count').textContent")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(300)
            info["closed_by_esc"] = not pg.evaluate("() => document.getElementById('video-dialog').open")
        elif isinstance(full, str):
            # 元素截图时让固定页头/回到顶部按钮不遮挡内容
            pg.add_style_tag(content=".site-header{position:absolute !important} .to-top,#to-top,.back-to-top{display:none !important}")
            pg.locator(full).screenshot(path=f"screenshots/{name}")
        else:
            pg.screenshot(path=f"screenshots/{name}", full_page=full)
        pg.close()
    b.close()
print(json.dumps(report, ensure_ascii=False, indent=1))
