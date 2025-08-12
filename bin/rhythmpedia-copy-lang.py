#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import rhythmpedia  # noqa: E402

def main() -> int:
    # Dispatcher has already chdir'ed into the target article dir (or you're running in it).
    target = Path(".").resolve()

    # qmd_all_masters scans by CWD; keep target as '.'
    rhythmpedia.qmd_all_masters(
        rhythmpedia.copy_lang_qmd,
        Path("."),
    )
    print(f"[DONE] Copied language files in: {target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

