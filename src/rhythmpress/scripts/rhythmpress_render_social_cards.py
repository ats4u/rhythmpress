#!/usr/bin/env python3
from __future__ import annotations

import argparse
from functools import partial
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import re
import sys
import threading
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import quote, urljoin, urlparse

from rhythmpress.scripts.rhythmpress_post_render_patch import resolve_output_dir

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    yaml = None


CARD_WIDTH = 1200
CARD_HEIGHT = 630
CARD_VERTICAL_PADDING = 52 + 56
CARD_INNER_HEIGHT = CARD_HEIGHT - CARD_VERTICAL_PADDING
MOBILE_VIEWPORT_WIDTH = 800
MOBILE_VIEWPORT_HEIGHT = 600
PLAYWRIGHT_OPERATION_TIMEOUT_MS = 15_000
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
DEFAULT_RENDER_MODE = "mobile-page"
DEFAULT_CROP_SELECTORS = (
    "main#quarto-document-content",
    "main.content",
    "article",
    "#quarto-content",
    "body",
)
DEFAULT_HIDE_SELECTORS = (
    "nav",
    ".navbar",
    "#quarto-sidebar",
    ".sidebar",
    "#TOC",
    ".toc-actions",
    ".page-navigation",
    ".quarto-margin-sidebar",
    ".quarto-secondary-nav",
    ".quarto-sidebar-toggle",
    "footer",
)

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

_MOBILE_PAGE_CROP_JS = """
({ cropSelectors, targetHeight, viewportWidth }) => {
  let target = null;
  for (const selector of cropSelectors) {
    target = document.querySelector(selector);
    if (target) break;
  }
  if (!target) {
    target = document.body;
  }
  const rect = target.getBoundingClientRect();
  const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
  const top = Math.max(0, rect.top + scrollY);
  const doc = document.documentElement;
  const body = document.body;
  const docHeight = Math.max(
    doc.scrollHeight,
    body ? body.scrollHeight : 0,
    top + targetHeight
  );
  const y = Math.min(top, Math.max(0, docHeight - targetHeight));

  return {
    x: 0,
    y,
    width: viewportWidth,
    height: targetHeight
  };
}
"""

_INJECT_HIDE_CSS_JS = """
(css) => {
  let style = document.getElementById("rhythmpress-social-card-hide-css");
  if (!style) {
    style = document.createElement("style");
    style.id = "rhythmpress-social-card-hide-css";
    document.head.appendChild(style);
  }
  style.textContent = css;
  return true;
}
"""

_VALIDATE_SELECTORS_JS = """
(selectors) => {
  const invalid = [];
  for (const selector of selectors) {
    try {
      document.querySelectorAll(selector);
    } catch (error) {
      invalid.push({ selector, message: String(error && error.message || error) });
    }
  }
  return invalid;
}
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
        "--allow-remote",
        dest="allow_remote",
        action="store_true",
        default=None,
        help=(
            "Allow remote network requests while rendering cards. "
            "Default is to block remote requests for deterministic local rendering."
        ),
    )
    p.add_argument(
        "--no-allow-remote",
        dest="allow_remote",
        action="store_false",
        help="Block remote network requests even if _quarto.yml enables them.",
    )
    javascript_group = p.add_mutually_exclusive_group()
    javascript_group.add_argument(
        "--enable-javascript",
        dest="enable_javascript",
        action="store_true",
        default=None,
        help="Enable page JavaScript while rendering social-card source pages.",
    )
    javascript_group.add_argument(
        "--disable-javascript",
        dest="enable_javascript",
        action="store_false",
        help="Disable page JavaScript even if _quarto.yml enables it.",
    )
    p.add_argument(
        "--render-mode",
        choices=("mobile-page", "template"),
        default=None,
        help=(
            "Rendering strategy. mobile-page screenshots the rendered page in a "
            "mobile viewport; template uses the legacy dedicated card template. "
            f"Default: {DEFAULT_RENDER_MODE}."
        ),
    )
    p.add_argument(
        "--viewport",
        default="",
        help=(
            "Mobile CSS viewport for --render-mode mobile-page, formatted WIDTHxHEIGHT. "
            f"Default: {MOBILE_VIEWPORT_WIDTH}x{MOBILE_VIEWPORT_HEIGHT}."
        ),
    )
    p.add_argument(
        "--screenshot-size",
        default="",
        help=(
            "Output screenshot size, formatted WIDTHxHEIGHT. "
            f"Default: {CARD_WIDTH}x{CARD_HEIGHT}."
        ),
    )
    p.add_argument(
        "--crop-selector",
        action="append",
        default=[],
        help=(
            "CSS selector whose top edge anchors the mobile-page screenshot crop. "
            "May be repeated for fallback order. Commas remain normal CSS selector "
            f"group syntax. Default order: {', '.join(DEFAULT_CROP_SELECTORS)}"
        ),
    )
    p.add_argument(
        "--hide-selector",
        action="append",
        default=[],
        help=(
            "Additional CSS selector, or comma-separated selector list, to hide before "
            "mobile-page screenshots. May be repeated. Whitespace is not a separator."
        ),
    )
    default_hide_group = p.add_mutually_exclusive_group()
    default_hide_group.add_argument(
        "--default-hide-selectors",
        dest="default_hide_selectors",
        action="store_true",
        default=None,
        help="Use the built-in Rhythmpress/Quarto chrome hide selectors.",
    )
    default_hide_group.add_argument(
        "--no-default-hide-selectors",
        dest="default_hide_selectors",
        action="store_false",
        help="Do not hide Rhythmpress/Quarto chrome with the default selector list.",
    )
    p.add_argument(
        "--css",
        action="append",
        default=[],
        help=(
            "Raw screenshot-only CSS to inject after generated hide rules. "
            "May be repeated for multiple override blocks."
        ),
    )
    p.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Process at most N pages (debug helper; 0 means all pages).",
    )
    p.add_argument(
        "--wait-ms",
        type=int,
        default=None,
        help=(
            "Milliseconds to wait after page load before extracting metadata and "
            "taking screenshots. Default: 0."
        ),
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


def _social_cards_config(config: dict) -> dict:
    rhythmpress_config = config.get("rhythmpress") or {}
    if not isinstance(rhythmpress_config, dict):
        return {}
    social_config = rhythmpress_config.get("social-cards") or {}
    if not isinstance(social_config, dict):
        raise RuntimeError("rhythmpress.social-cards in _quarto.yml must be a mapping")
    return social_config


def _config_string(config: dict, key: str, *, label: str) -> str:
    if key not in config or config.get(key) is None:
        return ""
    value = config.get(key)
    if not isinstance(value, str):
        raise RuntimeError(f"{label} in _quarto.yml must be a string")
    return value.strip()


def _config_bool(config: dict, key: str, *, label: str) -> bool | None:
    if key not in config or config.get(key) is None:
        return None
    value = config.get(key)
    if not isinstance(value, bool):
        raise RuntimeError(f"{label} in _quarto.yml must be a boolean")
    return value


def _config_int(config: dict, key: str, *, label: str) -> int | None:
    if key not in config or config.get(key) is None:
        return None
    value = config.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise RuntimeError(f"{label} in _quarto.yml must be an integer")
    return value


def _config_string_list(config: dict, key: str, *, label: str) -> list[str]:
    if key not in config or config.get(key) is None:
        return []
    value = config.get(key)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise RuntimeError(f"{label} in _quarto.yml must contain only strings")
            values.append(item)
        return values
    raise RuntimeError(f"{label} in _quarto.yml must be a string or list of strings")


def resolve_social_card_options(ns: argparse.Namespace, config: dict) -> argparse.Namespace:
    social_config = _social_cards_config(config)

    config_render_mode = _config_string(
        social_config,
        "render-mode",
        label="rhythmpress.social-cards.render-mode",
    )
    render_mode = ns.render_mode or config_render_mode or DEFAULT_RENDER_MODE
    if render_mode not in {"mobile-page", "template"}:
        raise RuntimeError(
            "rhythmpress.social-cards.render-mode must be one of: mobile-page, template"
        )

    config_allow_remote = _config_bool(
        social_config,
        "allow-remote",
        label="rhythmpress.social-cards.allow-remote",
    )
    allow_remote = (
        ns.allow_remote
        if ns.allow_remote is not None
        else config_allow_remote
        if config_allow_remote is not None
        else False
    )

    config_enable_javascript = _config_bool(
        social_config,
        "enable-javascript",
        label="rhythmpress.social-cards.enable-javascript",
    )
    enable_javascript = (
        ns.enable_javascript
        if ns.enable_javascript is not None
        else config_enable_javascript
        if config_enable_javascript is not None
        else False
    )

    config_default_hide_selectors = _config_bool(
        social_config,
        "default-hide-selectors",
        label="rhythmpress.social-cards.default-hide-selectors",
    )
    default_hide_selectors = (
        ns.default_hide_selectors
        if ns.default_hide_selectors is not None
        else config_default_hide_selectors
        if config_default_hide_selectors is not None
        else True
    )

    config_browser_executable = _config_string(
        social_config,
        "browser-executable",
        label="rhythmpress.social-cards.browser-executable",
    )
    browser_executable = ns.browser_executable.strip() or config_browser_executable

    viewport = (
        ns.viewport.strip()
        or _config_string(
            social_config,
            "viewport",
            label="rhythmpress.social-cards.viewport",
        )
        or f"{MOBILE_VIEWPORT_WIDTH}x{MOBILE_VIEWPORT_HEIGHT}"
    )
    screenshot_size = (
        ns.screenshot_size.strip()
        or _config_string(
            social_config,
            "screenshot-size",
            label="rhythmpress.social-cards.screenshot-size",
        )
        or f"{CARD_WIDTH}x{CARD_HEIGHT}"
    )

    config_wait_ms = _config_int(
        social_config,
        "wait-ms",
        label="rhythmpress.social-cards.wait-ms",
    )
    wait_ms = ns.wait_ms if ns.wait_ms is not None else config_wait_ms
    if wait_ms is None:
        wait_ms = 0
    if wait_ms < 0:
        raise RuntimeError("wait-ms must be zero or greater")

    config_crop_selectors = _config_string_list(
        social_config,
        "crop-selector",
        label="rhythmpress.social-cards.crop-selector",
    )
    crop_selector = ns.crop_selector if ns.crop_selector else config_crop_selectors

    hide_selector = [
        *_config_string_list(
            social_config,
            "hide-selector",
            label="rhythmpress.social-cards.hide-selector",
        ),
        *ns.hide_selector,
    ]
    css = [
        *_config_string_list(
            social_config,
            "css",
            label="rhythmpress.social-cards.css",
        ),
        *ns.css,
    ]

    return argparse.Namespace(
        allow_remote=allow_remote,
        browser_executable=browser_executable,
        crop_selector=crop_selector,
        css=css,
        default_hide_selectors=default_hide_selectors,
        enable_javascript=enable_javascript,
        hide_selector=hide_selector,
        render_mode=render_mode,
        screenshot_size=screenshot_size,
        viewport=viewport,
        wait_ms=wait_ms,
    )


def resolve_site_url(cli_site_url: str, config: dict | None = None) -> str:
    if cli_site_url.strip():
        return _normalize_site_url(cli_site_url.strip())
    env_site_url = os.getenv("RHYTHMPRESS_SITE_URL", "").strip()
    if env_site_url:
        return _normalize_site_url(env_site_url)

    if config is None:
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


def local_http_page_url(base_url: str, rel_html: PurePosixPath) -> str:
    return urljoin(base_url.rstrip("/") + "/", quote(rel_html.as_posix(), safe="/"))


def _is_local_http_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {
        "127.0.0.1",
        "localhost",
        "::1",
    }


class _QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def start_static_server(root: Path) -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    handler = partial(_QuietStaticHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _, port = server.server_address
    return server, thread, f"http://127.0.0.1:{port}/"


def stop_static_server(server: ThreadingHTTPServer, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def _clean_text(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", (value or "").strip())


def _truncate_text(value: str, limit: int) -> str:
    cleaned = _clean_text(value)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def parse_size(value: str, *, label: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)x(\d+)\s*", value or "")
    if not match:
        raise RuntimeError(f"{label} must be formatted as WIDTHxHEIGHT: {value!r}")
    width = int(match.group(1))
    height = int(match.group(2))
    if width <= 0 or height <= 0:
        raise RuntimeError(f"{label} must use positive dimensions: {value!r}")
    return width, height


def resolve_hide_selectors(
    extra_selectors: list[str],
    *,
    use_defaults: bool = True,
) -> list[str]:
    selectors: list[str] = []
    if use_defaults:
        selectors.extend(DEFAULT_HIDE_SELECTORS)
    selectors.extend(extra_selectors)
    return [selector.strip() for selector in selectors if selector.strip()]


def resolve_crop_selectors(cli_selectors: list[str]) -> list[str]:
    selectors = cli_selectors if cli_selectors else list(DEFAULT_CROP_SELECTORS)
    resolved = [selector.strip() for selector in selectors if selector.strip()]
    if not resolved:
        raise RuntimeError("at least one crop selector is required")
    return resolved


def resolve_css_overrides(css_blocks: list[str]) -> list[str]:
    return [css_block.strip() for css_block in css_blocks if css_block.strip()]


def build_hide_css(selectors: list[str]) -> str:
    if not selectors:
        return ""
    selector_list = ",\n".join(selectors)
    return f"""
{selector_list} {{
  display: none !important;
  visibility: hidden !important;
}}

html,
body {{
  overflow-x: hidden !important;
}}
"""


def build_screenshot_css(hide_selectors: list[str], css_overrides: list[str]) -> str:
    sections = [
        build_hide_css(hide_selectors).strip(),
        *css_overrides,
    ]
    return "\n\n".join(section for section in sections if section)


def validate_hide_selectors(page, selectors: list[str]) -> None:
    if not selectors:
        return
    invalid = page.evaluate(_VALIDATE_SELECTORS_JS, selectors)
    if invalid:
        first = invalid[0]
        selector = first.get("selector", "")
        message = first.get("message", "")
        raise RuntimeError(f"invalid --hide-selector {selector!r}: {message}")


def validate_crop_selectors(page, selectors: list[str]) -> None:
    invalid = page.evaluate(_VALIDATE_SELECTORS_JS, selectors)
    if invalid:
        first = invalid[0]
        selector = first.get("selector", "")
        message = first.get("message", "")
        raise RuntimeError(f"invalid --crop-selector {selector!r}: {message}")


def mobile_device_scale_factor(
    viewport_size: tuple[int, int],
    screenshot_size: tuple[int, int],
) -> float:
    viewport_width, _viewport_height = viewport_size
    screenshot_width, _screenshot_height = screenshot_size
    return screenshot_width / viewport_width


def build_fit_card_js(card_inner_height: int) -> str:
    return f"""
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

  const fits = () => card.scrollHeight <= {card_inner_height};

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


def build_card_html(
    *,
    title: str,
    blocks: list[dict[str, str]],
    rel_html: PurePosixPath,
    site_label: str,
    lang: str,
    card_size: tuple[int, int] = (CARD_WIDTH, CARD_HEIGHT),
) -> str:
    card_width, card_height = card_size
    safe_title = html.escape(_truncate_text(title or rel_html.as_posix(), 120))
    safe_site_label = html.escape(_clean_text(site_label or "Rhythmpress"))
    safe_path = html.escape("/" + rel_html.as_posix())
    safe_lang = html.escape(lang or "en")
    uses_japanese_font = (lang or "").lower().startswith("ja")
    font_stack = (
        '"VL PGothic", "Hiragino Sans", "Yu Gothic", "MS PGothic", sans-serif'
        if uses_japanese_font
        else '"Avenir Next", "Hiragino Sans", "Yu Gothic", "Helvetica Neue", sans-serif'
    )
    safe_font_stack = html.escape(font_stack)

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
      width: {card_width}px;
      height: {card_height}px;
      overflow: hidden;
      background:
        radial-gradient(circle at top right, rgba(149, 81, 36, 0.16), transparent 36%),
        linear-gradient(135deg, var(--paper), var(--paper-deep));
      color: var(--ink);
    }}

    body {{
      font-family: {safe_font_stack};
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


def _site_label_from_config(config: dict | None = None) -> str:
    if config is None:
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
    if _is_local_http_url(request.url):
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


def wait_for_fonts(page) -> None:
    try:
        page.evaluate(
            "() => document.fonts ? document.fonts.ready.then(() => true).catch(() => false) : true"
        )
    except Exception:
        return


def wait_after_load(page, wait_ms: int) -> None:
    if wait_ms > 0:
        page.wait_for_timeout(wait_ms)


def inject_hide_css(page, hide_css: str) -> None:
    if hide_css:
        page.evaluate(_INJECT_HIDE_CSS_JS, hide_css)


def screenshot_mobile_page(
    page,
    image_path: Path,
    *,
    viewport_size: tuple[int, int],
    screenshot_size: tuple[int, int],
    crop_selectors: list[str],
    hide_selectors: list[str],
    css_overrides: list[str],
) -> None:
    viewport_width, viewport_height = viewport_size
    _screenshot_width, screenshot_height = screenshot_size
    device_scale_factor = mobile_device_scale_factor(viewport_size, screenshot_size)
    capture_css_height = max(1, round(screenshot_height / device_scale_factor))

    screenshot_css = build_screenshot_css(hide_selectors, css_overrides)
    validate_hide_selectors(page, hide_selectors)
    validate_crop_selectors(page, crop_selectors)
    inject_hide_css(page, screenshot_css)
    wait_for_fonts(page)

    page.set_viewport_size({"width": viewport_width, "height": capture_css_height})
    try:
        crop = page.evaluate(
            _MOBILE_PAGE_CROP_JS,
            {
                "cropSelectors": crop_selectors,
                "targetHeight": capture_css_height,
                "viewportWidth": viewport_width,
            },
        )
        page.evaluate("(y) => window.scrollTo(0, y)", crop["y"])
        page.screenshot(path=str(image_path))
    finally:
        page.set_viewport_size({"width": viewport_width, "height": viewport_height})


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    output_dir = Path(resolve_output_dir(ns.output_dir)).resolve()
    if not output_dir.is_dir():
        print(f"[render-social-cards] output dir not found: {output_dir}", file=sys.stderr)
        return 2

    try:
        quarto_config = _load_quarto_config()
        social_options = resolve_social_card_options(ns, quarto_config)
        site_url_value = resolve_site_url(ns.site_url, config=quarto_config)
        browser_executable = resolve_browser_executable(social_options.browser_executable)
        site_label = _site_label_from_config(quarto_config)
        viewport_size = parse_size(social_options.viewport, label="--viewport")
        screenshot_size = parse_size(
            social_options.screenshot_size,
            label="--screenshot-size",
        )
        crop_selectors = resolve_crop_selectors(social_options.crop_selector)
        hide_selectors = resolve_hide_selectors(
            social_options.hide_selector,
            use_defaults=social_options.default_hide_selectors,
        )
        css_overrides = resolve_css_overrides(social_options.css)
    except RuntimeError as exc:
        print(f"[render-social-cards] {exc}", file=sys.stderr)
        return 2

    sync_playwright = _import_playwright()

    html_files = list(iter_html_files(output_dir))
    if ns.max_pages > 0:
        html_files = html_files[: ns.max_pages]

    files_changed = 0
    cards_written = 0

    static_server = None
    static_thread = None
    local_base_url = ""

    try:
        if social_options.render_mode == "mobile-page":
            static_server, static_thread, local_base_url = start_static_server(output_dir)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=browser_executable,
            )
            if social_options.render_mode == "mobile-page":
                source_context = browser.new_context(
                    java_script_enabled=social_options.enable_javascript,
                    viewport={"width": viewport_size[0], "height": viewport_size[1]},
                    locale="en-US",
                    is_mobile=True,
                    has_touch=True,
                    device_scale_factor=mobile_device_scale_factor(
                        viewport_size,
                        screenshot_size,
                    ),
                )
            else:
                source_context = browser.new_context(
                    java_script_enabled=social_options.enable_javascript,
                    viewport={"width": 1440, "height": 1400},
                    locale="en-US",
                )
            if not social_options.allow_remote:
                source_context.route("**/*", _block_remote)
            card_context = None
            card_page = None
            if social_options.render_mode == "template":
                card_context = browser.new_context(
                    java_script_enabled=False,
                    viewport={"width": screenshot_size[0], "height": screenshot_size[1]},
                    locale="en-US",
                )
                card_page = card_context.new_page()

            source_page = source_context.new_page()
            source_page.set_default_timeout(PLAYWRIGHT_OPERATION_TIMEOUT_MS)
            source_page.set_default_navigation_timeout(PLAYWRIGHT_OPERATION_TIMEOUT_MS)
            if card_page is not None:
                card_page.set_default_timeout(PLAYWRIGHT_OPERATION_TIMEOUT_MS)

            try:
                for html_path in html_files:
                    rel_html = rel_html_path(output_dir, html_path)
                    local_url = (
                        local_http_page_url(local_base_url, rel_html)
                        if local_base_url
                        else html_path.resolve().as_uri()
                    )
                    page_url_value = page_url(site_url_value, rel_html)
                    image_rel = social_image_rel_path(rel_html)
                    image_url_value = image_url(site_url_value, image_rel)

                    if not ns.quiet:
                        print(f"[render-social-cards] page={rel_html.as_posix()}")

                    source_page.goto(local_url, wait_until="load")
                    wait_after_load(source_page, social_options.wait_ms)
                    payload = source_page.evaluate(_EXTRACT_CARD_PAYLOAD_JS)

                    title = _clean_text(payload.get("title") or "")
                    description = _truncate_text(
                        payload.get("description") or title,
                        DESCRIPTION_LIMIT,
                    )
                    lang = _clean_text(payload.get("lang") or "")
                    blocks = payload.get("blocks") or []

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
                        if social_options.render_mode == "template":
                            if card_page is None:
                                raise RuntimeError("template render mode missing card page")
                            card_html = build_card_html(
                                title=title or rel_html.as_posix(),
                                blocks=blocks,
                                rel_html=rel_html,
                                site_label=site_label,
                                lang=lang,
                                card_size=screenshot_size,
                            )
                            card_page.set_content(card_html, wait_until="load")
                            card_page.evaluate(
                                build_fit_card_js(
                                    max(120, screenshot_size[1] - CARD_VERTICAL_PADDING)
                                )
                            )
                            card_page.screenshot(path=str(image_path))
                        else:
                            screenshot_mobile_page(
                                source_page,
                                image_path,
                                viewport_size=viewport_size,
                                screenshot_size=screenshot_size,
                                crop_selectors=crop_selectors,
                                hide_selectors=hide_selectors,
                                css_overrides=css_overrides,
                            )
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
                if card_context is not None:
                    card_context.close()
                browser.close()
    finally:
        if static_server is not None and static_thread is not None:
            stop_static_server(static_server, static_thread)

    if not ns.quiet:
        print(
            f"[render-social-cards] cards_written={cards_written} files_changed={files_changed}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
