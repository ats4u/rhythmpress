#!/usr/bin/env python3
"""
rhythmpedia-render-nav

Render a language-specific global navigation by calling
lib.rhythmpedia.create_global_navigation(), then write it to
'_sidebar-<lang>.generated.md' next to the defs file (or stdout).

Usage:
  bin/rhythmpedia-render-nav --lang ja
  bin/rhythmpedia-render-nav --lang en --defs /path/to/_rhythmpedia.conf
  bin/rhythmpedia-render-nav --lang ja --out ./_sidebar-ja.generated.md
  bin/rhythmpedia-render-nav --lang ja --stdout
  bin/rhythmpedia-render-nav --lang ja --no-strict -v

Exit codes:
  0 success
  1 runtime/usage error
  2 write error
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from typing import List, NoReturn, Optional

# Ensure project lib/ is importable relative to this script’s location
BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(ROOT))

# Import library
from lib import rhythmpedia as rp  # type: ignore


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpedia-render-nav",
        description="Render global navigation Markdown from directories listed in a defs file.",
    )
    p.add_argument(
        "--lang",
        required=True,
        help="Language id (e.g., ja, en). Mandatory.",
    )
    p.add_argument(
        "--defs",
        default="_rhythmpedia.conf",
        help="Path to the definitions file listing article directories (default: %(default)s).",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Output file path. Defaults to '<defs dir>/_sidebar-<lang>.generated.md'.",
    )
    p.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of writing a file.",
    )
    p.add_argument(
        "--no-strict",
        action="store_true",
        help="Relax errors into warnings when possible.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate but do not write. Implies --stdout unless --out is provided.",
    )
    p.add_argument(
        "--chdir",
        default=None,
        help="Temporarily chdir before processing (useful in scripts).",
    )
    p.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times).",
    )
    p.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-error logs.",
    )
    return p.parse_args(argv)


class _Logger:
    def __init__(self, verbose: int = 0, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet

    def _emit(self, level: str, msg: str):
        if self.quiet and level.lower() in ("info", "debug"):
            return
        if level.lower() == "debug" and self.verbose < 2:
            return
        if level.lower() == "info" and self.verbose < 1:
            return
        print(f"[{level.upper()}] {msg}", file=sys.stderr)

    def info(self, msg: str): self._emit("info", msg)
    def warning(self, msg: str): self._emit("warning", msg)
    def error(self, msg: str): self._emit("error", msg)
    def debug(self, msg: str): self._emit("debug", msg)


def atomic_write(path: Path, data: str) -> None:
    """
    Write file only if content changed. Atomic replace via a temp file in the same dir.
    """
    try:
        existing = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    except Exception as e:
        # If we can't read, we still try to write anew.
        existing = None

    if existing == data:
        return  # no change

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(path)


def main(argv: Optional[List[str]] = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    logger = _Logger(verbose=ns.verbose, quiet=ns.quiet)

    if ns.chdir:
        try:
            os.chdir(ns.chdir)
        except Exception as e:
            die(1, f"chdir failed: {e}")

    defs_path = Path(ns.defs).expanduser().resolve()
    if not defs_path.exists() or not defs_path.is_file():
        die(1, f"defs not found or not a file: {defs_path}")

    strict = not ns.no_strict

    try:
        md = rp.create_global_navigation(defs_path, ns.lang, strict=strict, logger=logger)
    except Exception as e:
        die(1, f"navigation generation failed: {e}")

    # Ensure trailing newline for POSIXy friendliness
    if md and not md.endswith("\n"):
        md += "\n"

    if ns.stdout or (ns.dry_run and ns.out is None):
        sys.stdout.write(md)
        return 0

    out_path = Path(ns.out) if ns.out else defs_path.parent / f"_sidebar-{ns.lang}.generated.md"
    out_path = out_path.expanduser().resolve()

    if ns.dry_run:
        logger.info(f"[dry-run] Would write: {out_path} ({len(md)} bytes)")
        return 0

    try:
        atomic_write(out_path, md)
        logger.info(f"Wrote: {out_path}")
        return 0
    except Exception as e:
        print(f"[ERROR] write failed: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

