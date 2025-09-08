#!/usr/bin/env python3
# Creates an article directory scaffold:
#   - <dir>/.article_dir
#   - <dir>/.gitignore
#   - <dir>/master-<lang>.qmd  (default lang: ja)

import sys
from pathlib import Path
import pathlib

# Ensure project lib/ is importable relative to this script's location
BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(ROOT))

from lib import rhythmpedia

def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: rhythmpedia-create-page <directory-name> [--lang ja]")
        return 2

    target_dir: Path | None = None
    lang = "ja"

    it = iter(argv)
    for a in it:
        if a == "--lang":
            try:
                lang = next(it)
            except StopIteration:
                print("Error: --lang requires a value (e.g., ja).")
                return 2
        elif target_dir is None:
            target_dir = Path(a)
        else:
            print(f"Ignoring extra argument: {a}")

    if target_dir is None:
        print("Error: missing <directory-name> argument.")
        return 2

    try:
        created = rhythmpedia.create_page(target_dir, lang=lang)
    except Exception as e:
        print(f"create-page failed: {e}")
        return 1

    print("Created/kept:", *[str(p) for p in created], sep="\n  - ")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)

