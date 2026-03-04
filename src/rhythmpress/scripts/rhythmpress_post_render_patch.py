#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    yaml = None


TARGET_CLASS_NAMES = ("navbar-brand", "sidebar-logo-link")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_post_render_patch",
        description=(
            "Patch rendered HTML links after Quarto render. "
            "Targets navbar brand and sidebar logo links."
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
        "--lang-id",
        default="",
        help=(
            "Language id to route to (e.g., en, ja). "
            "Default: QUARTO_PROFILE env, else inferred from output-dir suffix '.site-<lang>'."
        ),
    )
    p.add_argument(
        "--conf",
        default="_rhythmpress.conf",
        help="Path to _rhythmpress.conf for lang_path.<lang> routes (default: _rhythmpress.conf).",
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


def _load_output_dir_from_quarto() -> str:
    q = Path("_quarto.yml")
    if not q.is_file():
        return "_site"
    if yaml is None:
        return "_site"
    try:
        data = yaml.safe_load(q.read_text(encoding="utf-8")) or {}
    except Exception:
        return "_site"
    return str((data.get("project", {}) or {}).get("output-dir", "_site"))


def resolve_output_dir(cli_output_dir: str) -> str:
    if cli_output_dir.strip():
        return cli_output_dir.strip()
    env = os.getenv("QUARTO_PROJECT_OUTPUT_DIR", "").strip()
    if env:
        return env
    return _load_output_dir_from_quarto()


def resolve_lang_id(cli_lang_id: str, output_dir: str) -> str:
    if cli_lang_id.strip():
        return cli_lang_id.strip().lower()
    profile = os.getenv("QUARTO_PROFILE", "").strip().lower()
    if profile:
        return profile

    # infer from output naming convention (.site-<lang>)
    base = Path(output_dir).name
    m = re.match(r"^\.(?:site|_site)-([a-z0-9_-]+)$", base, flags=re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return ""


def parse_lang_paths(conf_path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not conf_path.is_file():
        return out
    for raw in conf_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip()
        if not key.startswith("lang_path.") or not val:
            continue
        lang = key[len("lang_path.") :].strip().lower()
        if not lang:
            continue
        path_val = val if val.startswith("/") else "/" + val
        if not path_val.endswith("/"):
            path_val += "/"
        out[lang] = path_val
    return out


def route_for_lang(lang_id: str, conf_path: Path) -> str:
    if not lang_id:
        return "/"
    lang_paths = parse_lang_paths(conf_path)
    return lang_paths.get(lang_id, f"/{lang_id}/")


def _replace_href_in_tag(tag: str, target: str) -> Tuple[str, bool]:
    href_re = re.compile(r"""(\bhref\s*=\s*)(["'])([^"']*)(\2)""", re.IGNORECASE)
    m = href_re.search(tag)
    if not m:
        return tag, False
    old_href = m.group(3)
    if old_href == target:
        return tag, False
    new_tag = href_re.sub(rf"\1{m.group(2)}{target}{m.group(2)}", tag, count=1)
    return new_tag, True


def patch_html_text(text: str, target_href: str) -> Tuple[str, int]:
    # Target only <a> tags that include the configured class name.
    tag_re = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
    class_re_template = r"""\bclass\s*=\s*(["'])[^"']*\b{cls}\b[^"']*\1"""

    changed_count = 0

    def _patch_tag(match: re.Match[str]) -> str:
        nonlocal changed_count
        tag = match.group(0)
        for cls in TARGET_CLASS_NAMES:
            class_re = re.compile(class_re_template.format(cls=re.escape(cls)), re.IGNORECASE)
            if class_re.search(tag):
                new_tag, changed = _replace_href_in_tag(tag, target_href)
                if changed:
                    changed_count += 1
                    return new_tag
                return tag
        return tag

    out = tag_re.sub(_patch_tag, text)
    return out, changed_count


def iter_html_files(root: Path) -> Iterable[Path]:
    yield from root.rglob("*.html")


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    output_dir = Path(resolve_output_dir(ns.output_dir))
    if not output_dir.is_dir():
        print(f"[post-render-patch] output dir not found: {output_dir}", file=sys.stderr)
        return 2

    lang_id = resolve_lang_id(ns.lang_id, str(output_dir))
    if not lang_id:
        print(
            "[post-render-patch] cannot determine language id. "
            "Use --lang-id or set QUARTO_PROFILE.",
            file=sys.stderr,
        )
        return 2

    target_href = route_for_lang(lang_id, Path(ns.conf))
    if not ns.quiet:
        print(
            f"[post-render-patch] output={output_dir} lang={lang_id} target={target_href} dry_run={ns.dry_run}"
        )

    files_changed = 0
    links_changed = 0
    for html_path in iter_html_files(output_dir):
        src = html_path.read_text(encoding="utf-8", errors="ignore")
        patched, cnt = patch_html_text(src, target_href)
        if cnt <= 0:
            continue
        links_changed += cnt
        files_changed += 1
        if not ns.dry_run:
            html_path.write_text(patched, encoding="utf-8")

    if not ns.quiet:
        print(
            f"[post-render-patch] files_changed={files_changed} links_changed={links_changed}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
