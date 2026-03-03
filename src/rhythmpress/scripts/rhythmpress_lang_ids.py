#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from rhythmpress.lang_ids import detect_language_ids


def main(argv: list[str] | None = None) -> int:
    _ = argv  # currently no options
    lang_ids = detect_language_ids(Path.cwd())
    for lang_id in lang_ids:
        print(lang_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
