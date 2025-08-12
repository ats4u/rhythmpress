#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys, pathlib
import argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import rhythmpedia  # noqa: E402

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Copy master-<lang>.qmd -> <lang>/index.qmd and emit sidebar YAML."
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Article directories (default: .)",
    )
    args = ap.parse_args()

    targets = args.paths or [Path(".")]

    roots: list[Path] = []
    for t in targets:
        p = (t if t.is_absolute() else (Path.cwd() / t)).resolve()
        if not p.exists():
            print(f"[ERROR] not found: {t}", file=sys.stderr)
            return 2
        if not p.is_dir():
            print(f"[ERROR] not a directory: {t}", file=sys.stderr)
            return 2
        roots.append(p)

    for root in roots:
        rhythmpedia.qmd_all_masters(
            rhythmpedia.copy_lang_qmd,
            root,  # v3.2: explicit Path dir
        )
        print(f"[DONE] Copied language files in: {root}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())


