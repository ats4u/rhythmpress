#!/usr/bin/env python3
"""
rhythmpress-sidebar-langs.py

Scan directories listed in a definition file (default: _rhythmpress.conf),
collect language IDs from files named `_sidebar-<langid>.yml`, de-duplicate
(preserve first-seen order), and print one <langid> per line.

Usage:
  ./rhythmpress-sidebar-langs.py
  ./rhythmpress-sidebar-langs.py --defs mylist.txt
  ./rhythmpress-sidebar-langs.py --chdir /path/to/project -v
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import re
from typing import Iterable, List


SIDEBAR_PATTERN = re.compile(r"^_sidebar-([A-Za-z0-9_-]+)\.yml$")

def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress-sidebar-langs",
        description="List unique <langid> from _sidebar-<langid>.yml across project dirs.",
    )
    p.add_argument("--defs", default="_rhythmpress.conf",
                   help="Definition file with one directory per line (default: _rhythmpress.conf). Use '-' to read from stdin.")
    p.add_argument("--chdir", default=".",
                   help="Change working directory before scanning (default: .).")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Print directories as they are scanned.")
    return p.parse_args(argv)

def read_def_lines(src: Iterable[str]) -> List[str]:
    out: List[str] = []
    for raw in src:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
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
    dirs = read_def_lines(lines)
    if not dirs:
        die(2, "No directories found in definition file.")
    return [Path(d) for d in dirs]

def main(argv: List[str]) -> int:
    ns = parse_args(argv)

    root = Path(ns.chdir).resolve()
    if not root.is_dir():
        die(2, f"Not a directory: {root}")
    # switch cwd for consistent relative paths
    try:
        os_chdir = __import__("os").chdir
    except Exception:
        die(2, "Failed to import os for chdir.")
    os_chdir(root)

    langids: List[str] = []
    seen = set()

    for d in load_dirs(ns.defs):
        if ns.verbose:
            print(f"[SCAN] {d}")
        if not d.is_dir():
            # Non-fatal: just skip
            print(f"[WARN] Skipping missing dir: {d}", file=sys.stderr)
            continue
        for f in d.iterdir():
            if not f.is_file():
                continue
            m = SIDEBAR_PATTERN.match(f.name)
            if not m:
                continue
            lang = m.group(1)
            if lang not in seen:
                seen.add(lang)
                langids.append(lang)

    # Output: one langid per line
    for lang in langids:
        print(lang)

    # Exit 0 even if none found (empty output can be meaningful),
    # but you could switch to die(1, ...) if you prefer strictness.
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

