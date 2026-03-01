#!/usr/bin/env python3
"""
Generate a language-specific Quarto profile YAML by merging:
  - _quarto.yml
  - _metadata-<lang>.yml
  - _sidebar-<lang>.generated.yml

Output:
  - _quarto-<lang>.yml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn

import yaml


class _LiteralBlockDumper(yaml.SafeDumper):
    """Prefer literal block scalars for multi-line strings."""


def _str_representer(dumper: yaml.SafeDumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_LiteralBlockDumper.add_representer(str, _str_representer)


def die(code: int, msg: str) -> NoReturn:
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_quarto_profile",
        description="Generate _quarto-<lang>.yml from metadata + generated sidebar.",
    )
    p.add_argument("--lang", required=True, help="Language id (e.g. ja, en).")
    p.add_argument("--base", default="_quarto.yml", help="Path to base Quarto YAML (default: _quarto.yml).")
    p.add_argument("--metadata", default=None, help="Path to metadata YAML (default: _metadata-<lang>.yml).")
    p.add_argument("--sidebar", default=None, help="Path to generated sidebar YAML (default: _sidebar-<lang>.generated.yml).")
    p.add_argument("--out", default=None, help="Path to output YAML (default: _quarto-<lang>.yml).")
    p.add_argument("--quiet", "-q", action="store_true", help="Suppress informational output.")
    return p.parse_args(argv)


def read_yaml_mapping(path: Path, label: str) -> Dict[str, Any]:
    if not path.is_file():
        die(2, f"{label} not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        die(2, f"failed to parse {label}: {path} ({e})")
    if data is None:
        return {}
    if not isinstance(data, dict):
        die(2, f"{label} must be a YAML mapping: {path}")
    return data


def ensure_mapping(parent: Dict[str, Any], key: str) -> Dict[str, Any]:
    cur = parent.get(key)
    if isinstance(cur, dict):
        return cur
    nxt: Dict[str, Any] = {}
    parent[key] = nxt
    return nxt


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two mappings.
    - Dict values: merged recursively.
    - Non-dict values (including lists/scalars): override wins.
    """
    out: Dict[str, Any] = dict(base)
    for k, v in override.items():
        cur = out.get(k)
        if isinstance(cur, dict) and isinstance(v, dict):
            out[k] = deep_merge(cur, v)
        else:
            out[k] = v
    return out


def extract_sidebar(sidebar_doc: Dict[str, Any], src: Path) -> Dict[str, Any]:
    website = sidebar_doc.get("website")
    if not isinstance(website, dict):
        die(2, f"sidebar YAML missing website mapping: {src}")
    sidebar = website.get("sidebar")
    if not isinstance(sidebar, dict):
        die(2, f"sidebar YAML missing website.sidebar mapping: {src}")
    # Accept either website.sidebar existing or website.sidebar.contents.
    if "contents" in sidebar and not isinstance(sidebar.get("contents"), list):
        die(2, f"website.sidebar.contents must be a list when present: {src}")
    return sidebar


def serialize_yaml(data: Dict[str, Any]) -> str:
    dumped = yaml.dump(
        data,
        Dumper=_LiteralBlockDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    if not dumped.endswith("\n"):
        dumped += "\n"
    return dumped


def write_if_changed(path: Path, text: str) -> bool:
    try:
        existing = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    if existing == text:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def main(argv: List[str]) -> int:
    ns = parse_args(argv)
    lang = ns.lang.strip()
    if not lang:
        die(2, "--lang must not be empty.")

    base_path = Path(ns.base)
    metadata_path = Path(ns.metadata or f"_metadata-{lang}.yml")
    sidebar_path = Path(ns.sidebar or f"_sidebar-{lang}.generated.yml")
    out_path = Path(ns.out or f"_quarto-{lang}.yml")

    base = read_yaml_mapping(base_path, "base Quarto YAML")
    meta = read_yaml_mapping(metadata_path, "metadata YAML")
    sidebar_doc = read_yaml_mapping(sidebar_path, "sidebar YAML")

    sidebar = extract_sidebar(sidebar_doc, sidebar_path)
    merged = deep_merge(base, meta)

    website = ensure_mapping(merged, "website")
    project = ensure_mapping(merged, "project")
    current_sidebar = ensure_mapping(website, "sidebar")
    website["sidebar"] = deep_merge(current_sidebar, sidebar)

    # Profile-only overrides
    merged["lang"] = lang
    project["output-dir"] = f".site-{lang}"
    project["render"] = [
        f"**/{lang}/**/*.qmd",
        "!**/master*.md",
        "!**/master*.qmd",
        "!drafts/*",
    ]

    out_text = serialize_yaml(merged)
    changed = write_if_changed(out_path, out_text)
    if not ns.quiet:
        if changed:
            print(f"[INFO] generated: {out_path}")
        else:
            print(f"[INFO] unchanged: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
