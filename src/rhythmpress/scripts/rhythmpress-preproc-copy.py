#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys, pathlib
import argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import rhythmpress  # noqa: E402

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Copy master-<lang>.qmd -> <lang>/index.qmd and emit sidebar YAML (use --no-toc to skip appending the sidebar include)."
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Article directories (default: .)",
    )
    ap.add_argument(
        "--no-toc",
        action="store_true",
        help="Suppress appending the sidebar include (/_sidebar.generated.md) to <lang>/index.qmd",
    )
    args = ap.parse_args()

    toc = not args.no_toc

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
        rhythmpress.qmd_all_masters(
            rhythmpress.copy_lang_qmd,
            root,  # v3.2: explicit Path dir
            toc=toc,
        )
        print(f"[DONE] Copied language files in: {root}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
