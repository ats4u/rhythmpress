#!/usr/bin/env python3
import os, datetime, urllib.parse, yaml
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, quote

QUARTO_YML = "_quarto.yml"
NOW = datetime.date.today().isoformat()

# ---- Config you can tweak ----
EXCLUDE_FILES = {"404.html", "search.html"}
EXCLUDE_PATTERNS = ("master-", )  # skip files whose basename starts with any of these
HEAD_READ_BYTES = 131072          # ~128KB to cover <head>
# --------------------------------

# --- Load project.output-dir (env > YAML > default) ---
def load_output_dir():
    env_out = os.getenv("QUARTO_PROJECT_OUTPUT_DIR")
    if env_out:
        return env_out
    with open(QUARTO_YML, "r", encoding="utf-8") as f:
        conf = yaml.safe_load(f) or {}
    return (conf.get("project", {}) or {}).get("output-dir", "_site")

# --- Load website.site-url (env > YAML > default) ---
def load_site_url():
    env = os.getenv("SITE_URL")
    if env:
        return env.rstrip("/") + "/"
    with open(QUARTO_YML, "r", encoding="utf-8") as f:
        conf = yaml.safe_load(f) or {}
    url = (conf.get("website", {}) or {}).get("site-url", "https://example.com/")
    return url.rstrip("/") + "/"

SITE_DIR = load_output_dir()
BASE_URL = load_site_url()

# --- HTML <head> parser for robots + canonical ---
class HeadScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.noindex = False
        self.canonical = None
        self.in_head = False
    def handle_starttag(self, tag, attrs):
        a = {k.lower(): v for k, v in attrs}
        t = tag.lower()
        if t == "head":
            self.in_head = True
        if not self.in_head:
            return
        if t == "meta" and (a.get("name","").lower() == "robots"):
            content = (a.get("content") or "").lower()
            if "noindex" in content or content.strip() == "none":
                self.noindex = True
        # rel may be space-separated; handle common forms
        if t == "link" and "rel" in a and "canonical" in a.get("rel","").lower():
            self.canonical = a.get("href")
    def handle_endtag(self, tag):
        if tag.lower() == "head":
            self.in_head = False

def scan_head(fullpath):
    with open(fullpath, "r", encoding="utf-8", errors="ignore") as f:
        head = f.read(HEAD_READ_BYTES)
    p = HeadScanner(); p.feed(head); return p

def pretty_url(rel):
    rel = rel.replace(os.sep, "/")
    if rel.endswith("index.html"):
        rel = rel[:-10]  # .../index.html -> .../
    return urllib.parse.urljoin(BASE_URL, rel)

def encode_url(u: str) -> str:
    parts = urlsplit(u)
    path  = quote(parts.path,  safe="/-._~")
    query = quote(parts.query, safe="=&?/:;-._~")
    frag  = quote(parts.fragment, safe="-._~")
    return urlunsplit((parts.scheme, parts.netloc, path, query, frag))

def should_skip_file(name: str) -> bool:
    base = os.path.basename(name)
    if base in EXCLUDE_FILES:
        return True
    return any(base.startswith(pfx) for pfx in EXCLUDE_PATTERNS)

# --- Sanity: ensure output dir exists ---
if not os.path.isdir(SITE_DIR):
    raise SystemExit(f"[sitemap] Output dir not found: {SITE_DIR}\n"
                     f"          Run `quarto render` first or set QUARTO_PROJECT_OUTPUT_DIR.")

# --- Gather (url, lastmod) from rendered HTML ---
entries = []  # list of tuples (encoded_url, yyy-mm-dd)
for root, _, files in os.walk(SITE_DIR):
    for name in files:
        if not name.endswith(".html"):
            continue
        if should_skip_file(name):
            continue

        full = os.path.join(root, name)
        rel  = os.path.relpath(full, SITE_DIR)

        info = scan_head(full)
        if info.noindex:
            continue

        # URL choice: canonical (if present) else pretty path
        raw_url = urllib.parse.urljoin(BASE_URL, info.canonical) if info.canonical else pretty_url(rel)
        url = encode_url(raw_url)

        # Per-file lastmod from mtime; fallback to today if anything odd
        try:
            lastmod = datetime.date.fromtimestamp(os.path.getmtime(full)).isoformat()
        except Exception:
            lastmod = NOW

        entries.append((url, lastmod))

# --- Write sitemap.xml ---
sitemap_path = os.path.join(SITE_DIR, "sitemap.xml")
os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)

with open(sitemap_path, "w", encoding="utf-8") as out:
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u, lm in sorted(entries, key=lambda x: x[0]):
        out.write("  <url>\n")
        out.write(f"    <loc>{u}</loc>\n")
        out.write(f"    <lastmod>{lm}</lastmod>\n")
        out.write("  </url>\n")
    out.write("</urlset>\n")

print(f"[sitemap] {len(entries)} URLs → {sitemap_path} (base {BASE_URL}, out {SITE_DIR})")

