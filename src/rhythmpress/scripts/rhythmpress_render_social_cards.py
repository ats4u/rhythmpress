#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import urljoin, urlparse

from rhythmpress.scripts.rhythmpress_post_render_patch import resolve_output_dir

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    yaml = None


CARD_WIDTH = 1200
CARD_HEIGHT = 630
CARD_INNER_HEIGHT = 630 - 52 - 56
SOCIAL_MARKER_BEGIN = "<!-- rhythmpress social cards begin -->"
SOCIAL_MARKER_END = "<!-- rhythmpress social cards end -->"
DEFAULT_BROWSER_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)
SKIP_DIR_NAMES = {"site_libs"}
SKIP_FILE_NAMES = {"404.html"}
BLOCK_LIMIT = 6
CHAR_BUDGET = 720
DESCRIPTION_LIMIT = 220

_SOCIAL_BLOCK_RE = re.compile(
    rf"{re.escape(SOCIAL_MARKER_BEGIN)}.*?{re.escape(SOCIAL_MARKER_END)}\n?",
    flags=re.IGNORECASE | re.DOTALL,
)
_HEAD_CLOSE_RE = re.compile(r"</head>", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")
_INDEX_HTML = PurePosixPath("index.html")

_EXTRACT_CARD_PAYLOAD_JS = f"""
() => {{
  const root =
    document.querySelector("main#quarto-document-content") ||
    document.querySelector("main.content") ||
    document.body;
  const titleEl =
    document.querySelector("#title-block-header .title") ||
    root.querySelector("h1.title") ||
    document.querySelector("title");
  const title = (titleEl?.innerText || document.title || "").replace(/\\s+/g, " ").trim();
  const lang = (document.documentElement.getAttribute("lang") || "").trim();
  const blocks = [];
  const seen = new Set();
  let charCount = 0;

  const candidates = Array.from(root.querySelectorAll("h2, h3, h4, p, li, blockquote, pre"));
  for (const el of candidates) {{
    if (el.closest("#title-block-header")) continue;
    if (el.closest("nav, .sidebar, #TOC, .toc-actions, .page-navigation, .quarto-listing")) continue;

    let text = (el.innerText || "").replace(/\\s+/g, " ").trim();
    if (!text) continue;
    if (title && text === title) continue;
    if (seen.has(text)) continue;

    const tag = el.tagName.toLowerCase();
    const perBlockLimit =
      tag === "p" ? 260 :
      tag === "li" ? 170 :
      tag === "blockquote" ? 190 :
      140;

    if (text.length > perBlockLimit) {{
      text = text.slice(0, perBlockLimit - 1).trimEnd() + "…";
    }}
    if (!text) continue;

    blocks.push({{ tag, text }});
    seen.add(text);
    charCount += text.length;

    if (blocks.length >= {BLOCK_LIMIT} || charCount >= {CHAR_BUDGET}) {{
      break;
    }}
  }}

  const description = blocks
    .map((block) => block.text)
    .join(" ")
    .replace(/\\s+/g, " ")
    .trim()
    .slice(0, {DESCRIPTION_LIMIT});

  return {{
    title,
    lang,
    description,
    blocks
  }};
}}
"""

_FIT_CARD_JS = f"""
() => {{
  const card = document.querySelector(".card");
  const title = document.querySelector(".title");
  const excerpt = document.querySelector(".excerpt");
  if (!card || !title || !excerpt) {{
    return {{ ok: false, reason: "missing elements" }};
  }}

  const minTitle = 30;
  const minBody = 19;
  let titleSize = parseFloat(getComputedStyle(title).fontSize);
  let bodySize = parseFloat(getComputedStyle(excerpt).fontSize);

  const fits = () => card.scrollHeight <= {CARD_INNER_HEIGHT};

  let guard = 0;
  while (!fits() && guard < 24) {{
    guard += 1;
    let changed = false;

    if (titleSize > minTitle) {{
      titleSize = Math.max(minTitle, titleSize - 2);
      title.style.fontSize = `${{titleSize}}px`;
      changed = true;
    }}

    if (!fits() && bodySize > minBody) {{
      bodySize = Math.max(minBody, bodySize - 1);
      excerpt.style.fontSize = `${{bodySize}}px`;
      changed = true;
    }}

    if (!changed) {{
      break;
    }}
  }}

  return {{
    ok: true,
    titleSize,
    bodySize,
    scrollHeight: card.scrollHeight
  }};
}}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_render_social_cards",
        description=(
            "Render social-card PNGs from rendered Quarto HTML and inject "
            "Open Graph / Twitter meta tags into each page."
        ),
    )
    p.add_argument(
        "--output-dir",
        default="",
        help=(
            "Rendered site directory. "
            "Default: QUARTO_PROJECT_OUTPUT_DIR env, else _quarto.yml project.output-dir, else _site."
        ),
    )
    p.add_argument(
        "--site-url",
        default="",
        help="Absolute deployed site URL. Default: website.site-url from _quarto.yml.",
    )
    p.add_argument(
        "--browser-executable",
        default="",
        help=(
            "Browser executable path. Default: RHYTHMPRESS_SOCIAL_BROWSER env, "
            "else a known system Chrome/Chromium path."
        ),
    )
    p.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Process at most N pages (debug helper; 0 means all pages).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without writing files.",
    )
    p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress non-error logs.",
    )
    return p.parse_args(argv)


def _load_quarto_config() -> dict:
    q = Path("_quarto.yml")
    if not q.is_file() or yaml is None:
        return {}
    try:
        data = yaml.safe_load(q.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_site_url(cli_site_url: str) -> str:
    if cli_site_url.strip():
        return _normalize_site_url(cli_site_url.strip())
    env_site_url = os.getenv("RHYTHMPRESS_SITE_URL", "").strip()
    if env_site_url:
        return _normalize_site_url(env_site_url)

    config = _load_quarto_config()
    site_url = ((config.get("website") or {}).get("site-url") or "").strip()
    if not site_url:
        raise RuntimeError(
            "cannot determine site URL. Use --site-url or set website.site-url in _quarto.yml."
        )
    return _normalize_site_url(site_url)


def _normalize_site_url(site_url: str) -> str:
    normalized = site_url.strip()
    if not normalized:
        return normalized
    if not normalized.endswith("/"):
        normalized += "/"
    return normalized


def resolve_browser_executable(cli_path: str) -> str:
    if cli_path.strip():
        candidate = Path(cli_path.strip())
        if candidate.is_file():
            return str(candidate)
        raise RuntimeError(f"browser executable not found: {candidate}")

    env_path = os.getenv("RHYTHMPRESS_SOCIAL_BROWSER", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_file():
            return str(candidate)
        raise RuntimeError(f"browser executable not found: {candidate}")

    for raw in DEFAULT_BROWSER_CANDIDATES:
        candidate = Path(raw)
        if candidate.is_file():
            return str(candidate)

    raise RuntimeError(
        "no supported browser executable found. Use --browser-executable or "
        "set RHYTHMPRESS_SOCIAL_BROWSER."
    )


def iter_html_files(root: Path) -> Iterable[Path]:
    for html_path in sorted(root.rglob("*.html")):
        rel = html_path.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        if rel.name in SKIP_FILE_NAMES:
            continue
        yield html_path


def rel_html_path(output_dir: Path, html_path: Path) -> PurePosixPath:
    return PurePosixPath(html_path.relative_to(output_dir).as_posix())


def social_image_rel_path(rel_html: PurePosixPath) -> PurePosixPath:
    image_name = Path(rel_html.name).with_suffix(".png").name
    return PurePosixPath("attachments", "social", *rel_html.parts[:-1], image_name)


def page_url(site_url: str, rel_html: PurePosixPath) -> str:
    if rel_html == _INDEX_HTML:
        return site_url
    if rel_html.name == "index.html":
        return urljoin(site_url, "/".join(rel_html.parts[:-1]) + "/")
    return urljoin(site_url, rel_html.as_posix())


def image_url(site_url: str, image_rel: PurePosixPath) -> str:
    return urljoin(site_url, image_rel.as_posix())


def _clean_text(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", (value or "").strip())


def _truncate_text(value: str, limit: int) -> str:
    cleaned = _clean_text(value)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def build_card_html(*, title: str, blocks: list[dict[str, str]], rel_html: PurePosixPath, site_label: str, lang: str) -> str:
    safe_title = html.escape(_truncate_text(title or rel_html.as_posix(), 120))
    safe_site_label = html.escape(_clean_text(site_label or "Rhythmpress"))
    safe_path = html.escape("/" + rel_html.as_posix())
    safe_lang = html.escape(lang or "en")

    block_markup: list[str] = []
    for block in blocks:
        tag = block.get("tag", "p")
        text = _truncate_text(block.get("text", ""), 280 if tag == "p" else 180)
        if not text:
            continue
        if tag in {"h2", "h3", "h4"}:
            klass = "block block-heading"
        elif tag == "li":
            klass = "block block-list"
            text = "• " + text
        elif tag == "blockquote":
            klass = "block block-quote"
        else:
            klass = "block block-body"
        block_markup.append(f'<div class="{klass}">{html.escape(text)}</div>')

    if not block_markup:
        block_markup.append('<div class="block block-body">(No excerpt found)</div>')

    return f"""<!doctype html>
<html lang="{safe_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      color-scheme: light;
      --paper: #f7f0e3;
      --paper-deep: #eadac0;
      --ink: #1e1d1a;
      --muted: #6d665d;
      --accent: #955124;
      --border: rgba(30, 29, 26, 0.12);
    }}

    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      width: {CARD_WIDTH}px;
      height: {CARD_HEIGHT}px;
      overflow: hidden;
      background:
        radial-gradient(circle at top right, rgba(149, 81, 36, 0.16), transparent 36%),
        linear-gradient(135deg, var(--paper), var(--paper-deep));
      color: var(--ink);
    }}

    body {{
      font-family: "Avenir Next", "Hiragino Sans", "Yu Gothic", "Helvetica Neue", sans-serif;
    }}

    .card {{
      width: 100%;
      height: 100%;
      padding: 56px 64px 52px;
      display: flex;
      flex-direction: column;
      gap: 22px;
      position: relative;
      overflow: hidden;
    }}

    .card::before {{
      content: "";
      position: absolute;
      inset: 18px;
      border: 1px solid var(--border);
      border-radius: 28px;
      pointer-events: none;
    }}

    .eyebrow {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
    }}

    .title {{
      margin: 0;
      font-size: 3em;
      line-height: 1.25;
      font-weight: 700;
      max-width: 1020px;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 3;
      overflow: hidden;
    }}

    .excerpt {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 980px;
      overflow: hidden;
      font-size: 2em;
      line-height: 1.5;
    }}

    .block {{
      display: -webkit-box;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .block-heading {{
      font-size: 1em;
      line-height: 1.18;
      font-weight: 700;
      color: var(--accent);
      -webkit-line-clamp: 2;
    }}

    .block-body,
    .block-list,
    .block-quote {{
      font-size: 1.5em;
      line-height: 1.25;
      padding:0em;
      -webkit-line-clamp: 3;
    }}

    .block-quote {{
      padding-left: 18px;
      border-left: 4px solid rgba(149, 81, 36, 0.30);
    }}

    .footer {{
      margin-top: auto;
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.2;
    }}

    .site-label {{
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">Rendered opening excerpt</div>
    <h1 class="title">{safe_title}</h1>
    <div class="excerpt">
      {''.join(block_markup)}
    </div>
    <div class="footer">
      <div class="site-label">{safe_site_label}</div>
      <div>{safe_path}</div>
    </div>
  </div>
</body>
</html>
"""


def _meta_attr(name: str, content: str, *, property_attr: bool = False) -> str:
    attr_name = "property" if property_attr else "name"
    return f'<meta {attr_name}="{html.escape(name, quote=True)}" content="{html.escape(content, quote=True)}">'


def build_social_meta_block(
    *,
    title: str,
    description: str,
    page_url_value: str,
    image_url_value: str,
    site_name: str,
) -> str:
    safe_title = _truncate_text(title, 300)
    safe_description = _truncate_text(description or title, DESCRIPTION_LIMIT)
    tags = [
        _meta_attr("og:title", safe_title, property_attr=True),
        _meta_attr("og:description", safe_description, property_attr=True),
        _meta_attr("og:image", image_url_value, property_attr=True),
        _meta_attr("og:url", page_url_value, property_attr=True),
        _meta_attr("og:type", "article", property_attr=True),
        _meta_attr("og:site_name", site_name, property_attr=True),
        _meta_attr("twitter:card", "summary_large_image"),
        _meta_attr("twitter:title", safe_title),
        _meta_attr("twitter:description", safe_description),
        _meta_attr("twitter:image", image_url_value),
    ]
    return "\n".join([SOCIAL_MARKER_BEGIN, *tags, SOCIAL_MARKER_END, ""])


def upsert_social_meta_block(html_text: str, meta_block: str) -> str:
    if _SOCIAL_BLOCK_RE.search(html_text):
        return _SOCIAL_BLOCK_RE.sub(meta_block, html_text, count=1)

    match = _HEAD_CLOSE_RE.search(html_text)
    if not match:
        raise RuntimeError("cannot inject social meta tags: missing </head>")
    return html_text[: match.start()] + meta_block + html_text[match.start() :]


def _site_label_from_config() -> str:
    config = _load_quarto_config()
    website = config.get("website") or {}
    project = config.get("project") or {}
    return _clean_text(
        website.get("title")
        or project.get("title")
        or "Rhythmpress"
    )


def _block_remote(route, request) -> None:
    parsed = urlparse(request.url)
    if parsed.scheme in {"file", "data", "about"}:
        route.continue_()
        return
    route.abort()


def _import_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - import error path
        raise RuntimeError(
            "playwright is required. Install it with: python -m pip install playwright"
        ) from exc
    return sync_playwright


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    output_dir = Path(resolve_output_dir(ns.output_dir)).resolve()
    if not output_dir.is_dir():
        print(f"[render-social-cards] output dir not found: {output_dir}", file=sys.stderr)
        return 2

    try:
        site_url_value = resolve_site_url(ns.site_url)
        browser_executable = resolve_browser_executable(ns.browser_executable)
        site_label = _site_label_from_config()
    except RuntimeError as exc:
        print(f"[render-social-cards] {exc}", file=sys.stderr)
        return 2

    sync_playwright = _import_playwright()

    html_files = list(iter_html_files(output_dir))
    if ns.max_pages > 0:
        html_files = html_files[: ns.max_pages]

    files_changed = 0
    cards_written = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=browser_executable,
        )
        source_context = browser.new_context(
            java_script_enabled=False,
            viewport={"width": 1440, "height": 1400},
            locale="en-US",
        )
        source_context.route("**/*", _block_remote)
        card_context = browser.new_context(
            java_script_enabled=False,
            viewport={"width": CARD_WIDTH, "height": CARD_HEIGHT},
            locale="en-US",
        )

        source_page = source_context.new_page()
        card_page = card_context.new_page()

        try:
            for html_path in html_files:
                rel_html = rel_html_path(output_dir, html_path)
                local_url = html_path.resolve().as_uri()
                page_url_value = page_url(site_url_value, rel_html)
                image_rel = social_image_rel_path(rel_html)
                image_url_value = image_url(site_url_value, image_rel)

                if not ns.quiet:
                    print(f"[render-social-cards] page={rel_html.as_posix()}")

                source_page.goto(local_url, wait_until="load")
                payload = source_page.evaluate(_EXTRACT_CARD_PAYLOAD_JS)

                title = _clean_text(payload.get("title") or "")
                description = _truncate_text(payload.get("description") or title, DESCRIPTION_LIMIT)
                lang = _clean_text(payload.get("lang") or "")
                blocks = payload.get("blocks") or []

                card_html = build_card_html(
                    title=title or rel_html.as_posix(),
                    blocks=blocks,
                    rel_html=rel_html,
                    site_label=site_label,
                    lang=lang,
                )
                meta_block = build_social_meta_block(
                    title=title or rel_html.as_posix(),
                    description=description or title or rel_html.as_posix(),
                    page_url_value=page_url_value,
                    image_url_value=image_url_value,
                    site_name=site_label,
                )

                image_path = output_dir / image_rel
                existing_html = html_path.read_text(encoding="utf-8", errors="ignore")
                patched_html = upsert_social_meta_block(existing_html, meta_block)

                if not ns.dry_run:
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    card_page.set_content(card_html, wait_until="load")
                    card_page.evaluate(_FIT_CARD_JS)
                    card_page.screenshot(path=str(image_path))
                    cards_written += 1

                    if existing_html != patched_html:
                        html_path.write_text(patched_html, encoding="utf-8")
                        files_changed += 1
                else:
                    cards_written += 1
                    if existing_html != patched_html:
                        files_changed += 1
        finally:
            source_context.close()
            card_context.close()
            browser.close()

    if not ns.quiet:
        print(
            f"[render-social-cards] cards_written={cards_written} files_changed={files_changed}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
