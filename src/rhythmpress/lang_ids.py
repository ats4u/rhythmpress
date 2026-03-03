from __future__ import annotations

import re
from pathlib import Path

_QUARTO_RE = re.compile(r"^_quarto-([^.]+)\.ya?ml$")
_METADATA_RE = re.compile(r"^_metadata-([^.]+)\.ya?ml$")


def detect_language_ids(root: Path) -> list[str]:
    """Detect language ids from root-level profile/metadata files."""
    ids: set[str] = set()
    for p in root.iterdir():
        if not p.is_file():
            continue
        m = _QUARTO_RE.match(p.name) or _METADATA_RE.match(p.name)
        if m:
            ids.add(m.group(1))
    return sorted(ids)

