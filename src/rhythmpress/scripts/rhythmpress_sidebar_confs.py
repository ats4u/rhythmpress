#!/usr/bin/env python3
"""
rhythmpress_build_sidebars.py

Reads a definition file (default: _rhythmpress.conf), scans each listed
directory for files named `_sidebar-<langid>.yml`, groups them by <langid>,
and generates root-level sidebars:

  ./_sidebar-<langid>.generated.conf

Each generated file contains:
  1) _sidebar-<langid>.before.yml
  2) <one line per discovered per-dir sidebar path>
  3) _sidebar-<langid>.after.yml

- Duplicates are removed while preserving the first-seen order based on the
  order of directories in the definition file.
- Missing directories are warned and skipped.
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List


SIDEBAR_RE = re.compile(r"^_sidebar-([A-Za-z0-9_-]+)\.yml$")


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_build_sidebars",
        description="Generate root _sidebar-<lang>.generated.conf files by aggregating per-dir sidebars.",
    )
    p.add_argument("--defs", default="_rhythmpress.conf",
                   help="Definition file listing directories (default: _rhythmpress.conf). Use '-' to read from stdin.")
    p.add_argument("--chdir", default=".",
                   help="Change working directory before running (default: .).")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Print what is being scanned and written.")
    p.add_argument("--dry-run", action="store_true",
                   help="Show actions without writing files.")
    return p.parse_args(argv)


def read_def_lines(src: Iterable[str]) -> List[str]:
    out: List[str] = []
    for raw in src:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # allow inline comments with ' # '
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        if line:
            out.append(line.strip())
    return out


def load_dirs(defs_path: str) -> List[Path]:
    if defs_path == "-":
        lines = sys.stdin.read().splitlines()
    else:
        p = Path(defs_path)
        if not p.exists():
            die(2, f"Definition file not found: {p}")
        lines = p.read_text(encoding="utf-8").splitlines()
    items = read_def_lines(lines)
    if not items:
        die(2, "No directories found in definition file.")
    return [Path(d) for d in items]


def collect_per_lang_paths(dirs: List[Path], verbose: bool) -> Dict[str, List[str]]:
    """
    Returns a mapping: lang -> [relative per-dir sidebar paths], deduped in order.
    """
    per_lang: Dict[str, List[str]] = {}
    seen_per_lang: Dict[str, set] = {}

    for d in dirs:
        if not d.is_dir():
            print(f"[WARN] Skipping missing dir: {d}", file=sys.stderr)
            continue
        if verbose:
            print(f"[SCAN] {d}")

        for entry in d.iterdir():
            if not entry.is_file():
                continue
            m = SIDEBAR_RE.match(entry.name)
            if not m:
                continue
            lang = m.group(1)
            rel = str(entry.as_posix())  # keep relative path as written in defs
            bucket = per_lang.setdefault(lang, [])
            seen = seen_per_lang.setdefault(lang, set())
            if rel not in seen:
                bucket.append(rel)
                seen.add(rel)

    return per_lang


def write_root_sidebars(per_lang: Dict[str, List[str]], *, verbose: bool, dry_run: bool) -> None:
    """
    For each lang, write ./_sidebar-<lang>.generated.conf:
      first line:  _sidebar-<lang>.before.yml
      middle:      collected per-dir sidebar paths
      last line:   _sidebar-<lang>.after.yml
    """
    for lang, paths in per_lang.items():
        out_name = f"_sidebar-{lang}.generated.conf"
        lines = [f"_sidebar-{lang}.before.yml", *paths, f"_sidebar-{lang}.after.yml"]
        if verbose or dry_run:
            print(f"[WRITE] {out_name}")
            for ln in lines:
                print(f"         {ln}")
        if not dry_run:
            Path(out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: List[str]) -> int:
    ns = parse_args(argv)

    root = Path(ns.chdir).resolve()
    if not root.is_dir():
        die(2, f"Not a directory: {root}")
    # operate relative to project root
    import os
    os.chdir(root)

    dirs = load_dirs(ns.defs)
    per_lang = collect_per_lang_paths(dirs, verbose=ns.verbose)

    if not per_lang:
        # No sidebars found anywhere; still exit 0 with no files written.
        if ns.verbose or ns.dry_run:
            print("[INFO] No _sidebar-<lang>.yml files found in any directory.")
        return 0

    write_root_sidebars(per_lang, verbose=ns.verbose, dry_run=ns.dry_run)
    if ns.verbose or ns.dry_run:
        langs = ", ".join(per_lang.keys())
        print(f"[DONE] Generated sidebars for languages: {langs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


