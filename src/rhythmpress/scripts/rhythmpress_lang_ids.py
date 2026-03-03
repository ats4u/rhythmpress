#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


QUARTO_RE = re.compile(r"^_quarto-([^.]+)\.ya?ml$")
METADATA_RE = re.compile(r"^_metadata-([^.]+)\.ya?ml$")


def _collect_lang_ids(cwd: Path) -> list[str]:
    ids: set[str] = set()

    for p in cwd.iterdir():
        if not p.is_file():
            continue
        m = QUARTO_RE.match(p.name) or METADATA_RE.match(p.name)
        if m:
            ids.add(m.group(1))

    return sorted(ids)


def main(argv: list[str] | None = None) -> int:
    _ = argv  # currently no options
    lang_ids = _collect_lang_ids(Path.cwd())
    for lang_id in lang_ids:
        print(lang_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
