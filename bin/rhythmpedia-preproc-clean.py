#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys, argparse, pathlib, os
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import rhythmpedia  # noqa: E402

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

    # allow file paths: treat as their parent directory
    if p.is_file():
        p = p.parent

    # 1) obvious no-gos
    if p == Path(p.root):
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
    ap = argparse.ArgumentParser(description="Safely clean an article directory.")
    # paths are OPTIONAL; default = current working directory
    ap.add_argument("paths", nargs="*", type=Path, help="Directories to clean (default: .)")
    ap.add_argument("--apply", action="store_true", help="Actually perform deletions")
    ap.add_argument("--force", action="store_true", help="Skip interactive confirmation")
    ap.add_argument("--sentinel", default=SENTINEL_DEFAULT, help="Sentinel filename required in target dir")
    args = ap.parse_args(argv)

    # No paths given → use "."
    targets = args.paths or [Path(".")]

    safe_targets: list[Path] = []
    for a in targets:
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

    # Perform clean per target (v3.2: call lib directly; no cwd/pushd; no qmd_all_masters)
    for p in safe_targets:
        rhythmpedia.clean_directories_except_attachments_qmd(p)
        print(f"[DONE] Cleaned: {p}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

