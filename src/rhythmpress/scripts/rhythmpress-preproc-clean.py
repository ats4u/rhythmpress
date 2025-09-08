#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys, argparse, pathlib, os, shutil
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import rhythmpress  # noqa: E402

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

# ---------- NEW: sidebar purge helpers ----------
def _sidebar_candidates(root: Path, lang: str | None) -> list[Path]:
    """
    Return sidebar files in `root` (non-recursive).
    If `lang` is provided, only language-specific files are targeted.
    """
    pats: list[str]
    if lang:
        pats = [f"_sidebar-{lang}.yml", f"_sidebar-{lang}.generated.*"]
    else:
        pats = ["_sidebar-*.yml", "_sidebar-*.generated.*", "_sidebar.generated.*"]

    found: list[Path] = []
    for pat in pats:
        found.extend(root.glob(pat))
    # Dedup & sort for stable output
    uniq = sorted(set(p.resolve() for p in found))
    return uniq

def _purge_sidebars(root: Path, *, lang: str | None, apply: bool) -> int:
    """
    Delete matching sidebar files in `root`. Returns count deleted (or would delete in dry-run).
    """
    files = _sidebar_candidates(root, lang)
    count = 0
    for f in files:
        if apply:
            try:
                f.unlink()
                print(f"🗑️  removed: {f}")
            except FileNotFoundError:
                pass
        else:
            print(f"[DRY-RUN] Would remove sidebar: {f}")
        count += 1
    return count
# ------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Safely clean an article directory.")
    # paths are OPTIONAL; default = current working directory
    ap.add_argument("paths", nargs="*", type=Path, help="Directories to clean (default: .)")
    ap.add_argument("--apply", action="store_true", help="Actually perform deletions")
    ap.add_argument("--force", action="store_true", help="Skip interactive confirmation")
    ap.add_argument("--sentinel", default=SENTINEL_DEFAULT, help="Sentinel filename required in target dir")
    # NEW flags
    # Default: purge sidebars (use --no-purge-sidebars to keep them)
    ap.add_argument(
        "--purge-sidebars",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete _sidebar-*.yml and *_generated.* in target dirs (default: yes). "
             "Use --no-purge-sidebars to keep them.",
    )

    ap.add_argument("--lang", help="Limit sidebar purge to a language id (e.g., ja)")
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

    # Dry-run preview
    if not args.apply:
        for p in safe_targets:
            print(f"[DRY-RUN] Would clean: {p}")
            if args.purge_sidebars:
                _purge_sidebars(p, lang=args.lang, apply=False)
        print("Add --apply to actually modify files.")
        return 0

    # Confirm destructive action
    if not args.force:
        confirm_interactive(safe_targets)

    # Perform operations
    for p in safe_targets:
        rhythmpress.clean_directories_except_attachments_qmd(p)
        if args.purge_sidebars:
            _purge_sidebars(p, lang=args.lang, apply=True)
        print(f"[DONE] Cleaned: {p}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

