"""检查 dist/ 中所有站内链接与资源（href/src/poster/srcset）是否存在：python3 scripts/check-links.py [BASE]"""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = os.environ.get("DIST") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")
BASE = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "/")).rstrip("/") + "/"
ATTRS = {"href", "src", "poster", "data-src", "data-poster"}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if v is None:
                continue
            if k == "id":
                self.ids.add(v)
            elif k in ATTRS:
                self.urls.append(v)
            elif k == "srcset":
                self.urls += [p.strip().split(" ")[0] for p in v.split(",") if p.strip()]


def resolve(url):
    u = urlparse(url)
    if u.scheme or url.startswith("//") or url.startswith(("mailto:", "#", "data:")):
        return None
    path = unquote(u.path)
    if not path.startswith(BASE):
        return ("outside-base", path)
    rel = path[len(BASE):]
    f = os.path.join(ROOT, rel)
    if os.path.isdir(f):
        f = os.path.join(f, "index.html")
    return (None, f) if os.path.exists(f) else ("missing", path)


bad, n, pages = [], 0, 0
for d, _, files in os.walk(ROOT):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        pages += 1
        p = P()
        p.feed(open(os.path.join(d, fn), encoding="utf-8").read())
        for url in p.urls:
            r = resolve(url)
            if r is None:
                continue
            n += 1
            if r[0]:
                bad.append((os.path.relpath(os.path.join(d, fn), ROOT), r[0], url))
print(f"pages={pages} internal_refs={n} broken={len(bad)}")
for b in bad[:50]:
    print(*b)
sys.exit(1 if bad else 0)
