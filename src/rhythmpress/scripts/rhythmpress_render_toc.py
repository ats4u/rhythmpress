#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sidebar → Markdown TOC Generator (Spec v2.1 Final)

- Reads a _sidebar.conf (list of YAMLs) from project root
- Concatenates ONLY website.sidebar.contents arrays (authorial order preserved)
- Renders nested Markdown list to stdout
- Leaf titles come from the target QMD/MD file: front-matter `title` (string) → first ATX H1 → path fallback → "untitled"
- Object-form leaves {href,text}: `text` is used only if the file can't supply a title
- Hrefs are normalized to directory-style: leading + trailing slash, dot-segments resolved, duplicate slashes collapsed
- Paths in conf and YAML are resolved relative to project root (parent of this script’s directory) UNLESS:
    * --root is given, which has highest priority
    * $RHYTHMPRESS_ROOT is set, which overrides script-relative fallback
    * Absolute paths in YAML/conf are preserved as absolute on the filesystem

Warnings are written to stderr. Line numbers are included when ruamel.yaml is available.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# ----------------------------
# Root & defaults
# ----------------------------

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT_FALLBACK = SCRIPT_PATH.parent.parent  # bin/.. → project root (fallback if no flags/env)

DEFAULT_LANGUAGE_TAILS = ("ja", "en")
DEFAULT_CACHE_NAME = "-"

# ----------------------------
# YAML loaders (ruamel preferred for line numbers)
# ----------------------------

_HAVE_RUAMEL = False
try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap, CommentedSeq

    _HAVE_RUAMEL = True
    _YAML_RUAMEL = YAML(typ="rt")
    _YAML_RUAMEL.preserve_quotes = False
except Exception:
    _HAVE_RUAMEL = False

try:
    import yaml as pyyaml
except Exception:  # pragma: no cover
    pyyaml = None  # PyYAML optional; if missing, we skip FM parse and go H1→fallback


def _yaml_load_text(text: str) -> Optional[dict]:
    if _HAVE_RUAMEL:
        return _YAML_RUAMEL.load(text)
    if pyyaml is None:
        return None
    return pyyaml.safe_load(text)


# ----------------------------
# Front-matter & H1 extraction
# ----------------------------

# BOM-tolerant front matter block, '---' ... '---' or '...'
_FM_RE = re.compile(r'^\ufeff?---\s*\n(.*?)\n(?:---|\.\.\.)\s*(?:\n|$)', re.DOTALL)
# First ATX H1 (ignore Setext H1 intentionally)
_H1_RE = re.compile(r'(?m)^\s*#\s+(.+?)\s*$')


def extract_title_from_text(text: str) -> Optional[str]:
    """
    Title resolution in a single file's text (QMD/MD parity):
      1) front-matter 'title' (string) → return as-is (inline HTML preserved)
      2) first ATX H1 line → return raw (inline HTML preserved)
      else None (caller decides fallbacks)
    """
    # 1) front-matter
    m = _FM_RE.match(text)
    if m:
        fm_block = m.group(1)
        if _HAVE_RUAMEL:
            try:
                data = _YAML_RUAMEL.load(fm_block)
                t = data.get("title") if isinstance(data, dict) else None
                if isinstance(t, str) and t.strip():
                    return t.strip()
            except Exception:
                pass
        if pyyaml is not None:
            try:
                data = pyyaml.safe_load(fm_block)
                t = data.get("title") if isinstance(data, dict) else None
                if isinstance(t, str) and t.strip():
                    return t.strip()
            except Exception:
                pass
        # no valid scalar title → fall through

    # 2) first ATX H1 in body
    body = text[m.end():] if m else text
    m2 = _H1_RE.search(body)
    if m2:
        return m2.group(1).strip()

    return None


# ----------------------------
# Cache (optional)
# ----------------------------

class TitleCache:
    def __init__(self, path: Path):
        self.path = path
        self._data: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self._data = {}

    def save(self) -> None:
        try:
            self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get(self, abspath: Path) -> Optional[str]:
        self.load()
        key = str(abspath)
        try:
            st = abspath.stat()
        except FileNotFoundError:
            return None
        rec = self._data.get(key)
        if not rec:
            return None
        if rec.get("mtime_ns") == st.st_mtime_ns and rec.get("size") == st.st_size:
            return rec.get("title") or None
        return None

    def put(self, abspath: Path, title: str) -> None:
        self.load()
        try:
            st = abspath.stat()
        except FileNotFoundError:
            return
        self._data[str(abspath)] = {
            "title": title,
            "mtime_ns": st.st_mtime_ns,
            "size": st.st_size,
        }


# ----------------------------
# Href normalization
# ----------------------------

def normalize_href(path_like: str) -> str:
    """
    Strict normalization to directory-style:
      - leading '/'
      - collapse //, resolve '.' and '..'
      - enforce trailing '/'
    """
    s = (path_like or "").strip().replace("\\", "/")
    # treat as relative for normalization
    if s.startswith("/"):
        s = s[1:]

    parts = []
    for p in s.split("/"):
        if not p or p == ".":
            continue
        if p == "..":
            if parts:
                parts.pop()
            continue
        parts.append(p)

    joined = "/".join(parts)
    if joined:
        return "/" + joined + "/"
    return "/"  # root special-case


# ----------------------------
# Filesystem resolution (new)
# ----------------------------

def yaml_path_for_fs(p: str) -> str:
    """YAML path → POSIX-ish string for FILESYSTEM resolution (preserve absolute)."""
    return (p or "").strip().replace("\\", "/")

def resolve_fs_path(root: Path, yaml_path: str) -> Path:
    """Resolve a YAML-provided path against root, preserving absolutes."""
    s = yaml_path_for_fs(yaml_path)
    p = Path(s)
    return p if p.is_absolute() else (root / s)

def is_directory_item(raw_path: str, root: Path) -> bool:
    """Heuristic: treat trailing '/' as directory; else check filesystem."""
    s = yaml_path_for_fs(raw_path)
    if s.endswith("/"):
        return True
    return resolve_fs_path(root, s).is_dir()

def pick_dir_index_fs(fs_dir: Path) -> Optional[Path]:
    """Prefer index.qmd over index.md within a concrete filesystem directory."""
    cand_qmd = fs_dir / "index.qmd"
    cand_md = fs_dir / "index.md"
    if cand_qmd.is_file():
        return cand_qmd
    if cand_md.is_file():
        return cand_md
    return None


# ----------------------------
# Path → href helpers (unchanged)
# ----------------------------

def file_href_for(p_rel_or_abs: str) -> str:
    """Convert a file path ('.qmd' / '.md') to a directory-style href.
    - '.../index.qmd' or '.../index.md' → '/.../'
    - otherwise 'foo/bar.qmd' → '/foo/bar/'
    - normalization: leading '/', trailing '/', collapse //, resolve '.' and '..'
    """
    s = (p_rel_or_abs or "").strip().replace("\\", "/")
    if s.startswith("/"):
        s = s[1:]

    posix = PurePosixPath(s)
    parent = str(posix.parent).strip("/")

    stem_lower = posix.stem.lower()
    ext_lower  = posix.suffix.lower()
    name_lower = posix.name.lower()

    if ext_lower in (".qmd", ".md") and (stem_lower == "index" or name_lower.startswith("index.")):
        return normalize_href(f"{parent}/" if parent else "/")

    return normalize_href(f"{parent}/{posix.stem}/" if parent else f"{posix.stem}/")


def dir_href_for(p_rel_or_abs_dir: str) -> str:
    """Convert 'foo/ja/' to '/foo/ja/' (normalized)."""
    s = (p_rel_or_abs_dir or "").strip().replace("\\", "/")
    return normalize_href(s)


# ----------------------------
# Fallback title heuristics
# ----------------------------

_ASCII_LETTER_RE = re.compile(r'[A-Za-z]')

def humanize_segment(seg: str) -> str:
    seg = seg.replace("-", " ").replace("_", " ").strip()
    if not seg:
        return "untitled"
    if _ASCII_LETTER_RE.search(seg):
        return " ".join(w.capitalize() if w else w for w in seg.split())
    return seg


def fallback_title_for_path(path_like: str, is_dir: bool, language_tails: Sequence[str]) -> str:
    s = (path_like or "").strip().replace("\\", "/").strip("/")
    if not s:
        return "untitled"
    if not is_dir and (s.endswith(".qmd") or s.endswith(".md")):
        stem = PurePosixPath(s).stem
        return humanize_segment(stem)

    parts = s.split("/")
    last = parts[-1] if parts else ""
    if last in language_tails and len(parts) >= 2:
        base = parts[-2]
        return humanize_segment(base)
    return humanize_segment(last or "untitled")


# ----------------------------
# Title resolver (uses FS resolver)
# ----------------------------

def read_text_safe(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        try:
            return p.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            return None


def resolve_title_for(
    root: Path,
    path_like: str,
    is_dir_item_flag: bool,
    prefer_title_mode: str,
    object_text: Optional[str],
    cache: Optional[TitleCache],
    language_tails: Sequence[str],
) -> Tuple[str, Optional[Path], bool]:
    """
    Return (title, src_file_used, file_exists)
    - prefer_title_mode: 'qmd' (default) or 'yaml'
      * 'yaml' forces object_text to win (when provided), regardless of file presence
    - object_text: possible 'text' from object-form leaves
    - path_like: raw YAML string (absolute or relative)
    """
    if prefer_title_mode == "yaml" and object_text and object_text.strip():
        return (object_text.strip(), None, False)

    fs_path = resolve_fs_path(root, path_like)

    # Decide the source file (index.* for dirs, or the file itself)
    src_path: Optional[Path] = None
    if is_dir_item_flag:
        src_path = pick_dir_index_fs(fs_path)
    else:
        # Only consider .qmd/.md as content files
        if fs_path.suffix.lower() in (".qmd", ".md"):
            src_path = fs_path

    # Try cache → file content
    if src_path and src_path.is_file():
        if cache:
            cached = cache.get(src_path)
            if isinstance(cached, str) and cached.strip():
                return (cached.strip(), src_path, True)
        text = read_text_safe(src_path)
        if text is not None:
            t = extract_title_from_text(text)
            if isinstance(t, str) and t.strip():
                t = t.strip()
                if cache:
                    cache.put(src_path, t)
                return (t, src_path, True)

    # file missing or no title → object_text if provided
    if object_text and object_text.strip():
        return (object_text.strip(), src_path, bool(src_path and src_path.exists() if src_path else False))

    # final: path fallback → 'untitled'
    return (
        fallback_title_for_path(path_like, is_dir_item_flag, language_tails) or "untitled",
        src_path,
        bool(src_path and src_path.exists() if src_path else False),
    )


# ----------------------------
# YAML item utilities (line numbers with ruamel)
# ----------------------------

def _node_line(obj: Any) -> Optional[int]:
    if not _HAVE_RUAMEL:
        return None
    try:
        if hasattr(obj, "lc") and hasattr(obj.lc, "line"):
            line = obj.lc.line
            return int(line) + 1  # ruamel is 0-based
    except Exception:
        pass
    return None


def _is_section_object(x: Any) -> bool:
    try:
        return isinstance(x, dict) and "section" in x and "contents" in x and isinstance(x["contents"], list)
    except Exception:
        return False


def _is_string_path(x: Any) -> bool:
    return isinstance(x, str)


def _extract_leaf_path_and_text(obj: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Object-form leaf:
      - Path key search order: href → path → file → first string value
      - 'text' is optional (fallback label)
    """
    keys = ("href", "path", "file")
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip(), obj.get("text") if isinstance(obj.get("text"), str) else None
    for v in obj.values():
        if isinstance(v, str) and v.strip():
            return v.strip(), obj.get("text") if isinstance(obj.get("text"), str) else None
    return None, obj.get("text") if isinstance(obj.get("text"), str) else None


# ----------------------------
# Renderer
# ----------------------------

class Renderer:
    def __init__(
        self,
        root: Path,
        language_tails: Sequence[str],
        prefer_title_mode: str = "qmd",
        cache: Optional[TitleCache] = None,
        strict: bool = False,
        prune_empty: bool = False,
    ):
        self.root = root
        self.language_tails = tuple(language_tails)
        self.prefer_title_mode = prefer_title_mode
        self.cache = cache
        self.strict = strict
        self.prune_empty = prune_empty
        self.warnings = 0

    def warn(self, msg: str) -> None:
        self.warnings += 1
        sys.stderr.write(f"WARNING: {msg}\n")

    def _render_items(
        self,
        items: Sequence[Any],
        depth: int,
        origin_yaml: Path,
    ) -> List[str]:
        out: List[str] = []
        for it in items:
            if _is_section_object(it):
                title = str(it["section"])
                child_lines = self._render_items(it["contents"], depth + 1, origin_yaml)
                if self.prune_empty and not child_lines:
                    continue
                out.append(("  " * depth) + f"- {title}")
                out.extend(child_lines)
                continue

            line_no = _node_line(it)

            # leaf: string path
            if _is_string_path(it):
                raw = it  # keep as-is (absolute or relative)
                is_dir = is_directory_item(raw, self.root)
                href = dir_href_for(raw) if is_dir else file_href_for(raw)
                title, src, exists = resolve_title_for(
                    self.root, raw, is_dir, self.prefer_title_mode, None, self.cache, self.language_tails
                )
                if not exists:
                    where = f"{origin_yaml}"
                    if line_no is not None:
                        where += f":{line_no}"
                    self.warn(f"Missing file for leaf '{raw}' (emitting link anyway). Source: {where}")
                out.append(("  " * depth) + f"- [{title}]({href})")
                continue

            # leaf: object form
            if isinstance(it, dict):
                p, txt = _extract_leaf_path_and_text(it)
                if not p:
                    where = f"{origin_yaml}"
                    if line_no is not None:
                        where += f":{line_no}"
                    self.warn(f"Unresolvable leaf object (no path-like key). Skipping. Source: {where}")
                    continue
                raw = p  # absolute or relative
                is_dir = is_directory_item(raw, self.root)
                href = dir_href_for(raw) if is_dir else file_href_for(raw)
                title, src, exists = resolve_title_for(
                    self.root, raw, is_dir, self.prefer_title_mode, txt, self.cache, self.language_tails
                )
                if not exists:
                    where = f"{origin_yaml}"
                    if line_no is not None:
                        where += f":{line_no}"
                    self.warn(f"Missing file for leaf '{raw}' (emitting link anyway). Source: {where}")
                out.append(("  " * depth) + f"- [{title}]({href})")
                continue

            # Unknown node → skip with warning
            where = f"{origin_yaml}"
            if line_no is not None:
                where += f":{line_no}"
            self.warn(f"Unknown item type at leaf level; skipping. Source: {where}")
        return out


# ----------------------------
# Reading _sidebar.conf and YAMLs
# ----------------------------

def read_conf_lines(conf_path: Path) -> List[str]:
    try:
        raw = conf_path.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"ERROR: cannot read conf '{conf_path}': {e}\n")
        sys.exit(2)
    out = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def read_sidebar_yaml(root: Path, yaml_path_str: str) -> Optional[Tuple[Path, Sequence[Any]]]:
    ypath = resolve_fs_path(root, yaml_path_str)
    if not ypath.is_file():
        sys.stderr.write(f"WARNING: sidebar YAML missing: {ypath}\n")
        return None
    try:
        text = ypath.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"WARNING: failed to read YAML {ypath}: {e}\n")
        return None
    data = _yaml_load_text(text)
    if not isinstance(data, dict):
        return None
    try:
        ws = data.get("website", {})
        sb = ws.get("sidebar", {})
        contents = sb.get("contents", None)
        if isinstance(contents, list):
            return (ypath, contents)
    except Exception:
        pass
    # Lacking website.sidebar.contents → skip silently (per spec)
    return None


# ----------------------------
# Main
# ----------------------------

def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build Markdown TOC from Quarto sidebars (Spec v2.1 Final)."
    )
    ap.add_argument("conf", help="Path to _sidebar.conf (relative to project root or absolute).")
    ap.add_argument(
        "--root",
        help="Override project root. If not given, $RHYTHMPRESS_ROOT is used; "
             "if unset, defaults to parent of this script directory.",
        default=None,
    )
    ap.add_argument(
        "--langs",
        help="Comma-separated language tails used in path fallback (default: ja,en).",
        default="ja,en",
    )
    ap.add_argument(
        "--prefer-title",
        choices=("qmd", "yaml"),
        default="qmd",
        help="If 'yaml', object {text} wins even when the file exists (default: qmd).",
    )
    ap.add_argument(
        "--cache",
        default=DEFAULT_CACHE_NAME,
        help=f"Title cache JSON path (default: {DEFAULT_CACHE_NAME}). Set to '-' to disable cache.",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="If set, missing file becomes an error (non-zero exit) after emitting the TOC.",
    )
    ap.add_argument(
        "--prune-empty",
        action="store_true",
        help="Drop sections with no printable descendants.",
    )
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    # Root resolution precedence: --root > $RHYTHMPRESS_ROOT > script-relative fallback
    if args.root:
        root = Path(args.root).resolve()
    else:
        env_root = os.environ.get("RHYTHMPRESS_ROOT")
        if env_root:
            root = Path(env_root).resolve()
        else:
            root = PROJECT_ROOT_FALLBACK

    conf_path = Path(args.conf)
    if not conf_path.is_absolute():
        conf_path = (root / conf_path).resolve()

    language_tails = tuple([s for s in (args.langs or "").split(",") if s.strip()]) or DEFAULT_LANGUAGE_TAILS

    cache: Optional[TitleCache]
    if args.cache and args.cache != "-":
        cache = TitleCache((root / args.cache).resolve())
        cache.load()
    else:
        cache = None

    # Gather root-level items by concatenating website.sidebar.contents arrays
    conf_lines = read_conf_lines(conf_path)
    root_items: List[Tuple[Path, Sequence[Any]]] = []
    for yaml_line in conf_lines:
        # Accept absolute or relative (relative resolved against root)
        res = read_sidebar_yaml(root, yaml_line)
        if res is None:
            continue
        root_items.append(res)

    renderer = Renderer(
        root=root,
        language_tails=language_tails,
        prefer_title_mode=args.prefer_title,
        cache=cache,
        strict=args.strict,
        prune_empty=args.prune_empty,
    )

    # Render
    lines_out: List[str] = []
    for origin_yaml, items in root_items:
        lines_out.extend(renderer._render_items(items, depth=0, origin_yaml=origin_yaml))

    # Print Markdown TOC
    sys.stdout.write("\n".join(lines_out).rstrip() + ("\n" if lines_out else ""))

    # Save cache
    if cache:
        cache.save()

    # Strict mode: missing files → non-zero exit
    if args.strict and renderer.warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

