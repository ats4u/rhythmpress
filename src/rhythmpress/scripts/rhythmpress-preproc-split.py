#!/usr/bin/env python3

from pathlib import Path
import sys, pathlib; import argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));
import rhythmpress

# CLI
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Split master-<lang>.qmd into <slug>/<lang>/index.qmd and generate language index + YAML."
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
        rhythmpress.qmd_all_masters(rhythmpress.split_master_qmd, root,toc=toc )  # v3.2: explicit Path dir
        print(f"[DONE] Split masters in: {root}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

