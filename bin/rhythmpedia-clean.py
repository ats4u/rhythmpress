#!/usr/bin/env python3

from pathlib import Path
import sys, argparse, pathlib, os
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));
from lib import rhythmpedia

SENTINEL_DEFAULT = ".article_dir"  # create this empty file in dirs you allow to clean

def find_project_root(start: Path) -> Path | None:
    # Treat either a git repo root or Quarto project root as the boundary
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists() or (p / "_quarto.yml").exists():
            return p
    return None

def ensure_safe_dir(target: Path, sentinel: str) -> Path:
    p = target.resolve()
    # 1) obvious no-gos
    if p == p.root:
        raise SystemExit("Refusing to operate on filesystem root.")
    if p == Path.home():
        raise SystemExit("Refusing to operate on your HOME directory.")
    if any(part in {".git", ".hg", ".svn"} for part in p.parts):
        raise SystemExit("Refusing to operate inside a VCS metadata path.")
    if p.is_symlink():
        raise SystemExit("Refusing to operate on a symlink target.")

    # 2) must be inside a recognized project
    root = find_project_root(p)
    if root is None:
        raise SystemExit("Not inside a recognized project (no .git or _quarto.yml found).")
    try:
        p.relative_to(root)
    except ValueError:
        raise SystemExit("Target is outside the project root.")

    # 3) sentinel file
    if not (p / sentinel).exists():
        raise SystemExit(f"Missing sentinel file: {p / sentinel}. Create it to allow cleaning.")

    # 4) depth sanity (helps catch '.', '..', etc.)
    if len(p.parts) < len(root.parts) + 1:
        raise SystemExit("Target path is too shallow; refusing to proceed.")

    return p

def confirm_interactive(paths: list[Path]) -> None:
    print("You are about to run a CLEAN operation on:")
    for p in paths:
        print("  -", p)
    print("\nType EXACTLY: DELETE")
    ans = input("> ").strip()
    if ans != "DELETE":
        raise SystemExit("Aborted.")

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Safe wrapper for cleaning directories.")
    ap.add_argument("paths", nargs="+", type=Path, help="Directories to clean")
    ap.add_argument("--apply", action="store_true", help="Actually perform deletions")
    ap.add_argument("--force", action="store_true", help="Skip interactive confirmation")
    ap.add_argument("--sentinel", default=SENTINEL_DEFAULT, help="Sentinel filename required in target dir")
    args = ap.parse_args(argv)

    safe_targets: list[Path] = []
    for a in args.paths:
        try:
            safe_targets.append(ensure_safe_dir(Path(a), args.sentinel))
        except SystemExit as e:
            print(f"[SAFEGUARD] {e}", file=sys.stderr)
            return 2

    if not args.apply:
        for p in safe_targets:
            print(f"[DRY-RUN] Would clean: {p}")
        print("Add --apply to actually modify files.")
        return 0

    if not args.force:
        confirm_interactive(safe_targets)

    # Optional: let the library read a deletion mode env var if you wire it up there
    # os.environ.setdefault("RHythmpedia_DELETE_MODE", "trash")  # if you implement 'send2trash' in the library

    for p in safe_targets:
        # Wrap the thunk: you can create more wrappers if you later add dry-run/plan support inside the library.
        rhythmpedia.qmd_all_masters(
            rhythmpedia.clean_directories_except_attachments_qmd,
            p
        )
        print(f"[DONE] Cleaned: {p}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

