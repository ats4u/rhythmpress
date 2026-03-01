#!/usr/bin/env python3
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from watchfiles import run_process, Change

IGNORES  = {".git", ".venv", "node_modules", ".quarto", ".obsidian",
            "__pycache__", ".site", "_site"}
MASTER_SUFFIXES = {".qmd", ".md"}
CONFIG_PATTERNS = (
    "_quarto.yml",
    "_quarto-*.yml",
    "_metadata-*.yml",
    "_sidebar-*.conf",
)
GENERATED_CONFIG_PATTERNS = (
    "_sidebar-*.generated.conf",
)

def build():
    print("[watch] change detected → rebuilding…")
    return subprocess.call(["rhythmpress", "build", "--skip-clean"])

def watch_filter(change, path: str) -> bool:
    p = Path(path)
    # ignore noisy dirs
    if any(part in IGNORES for part in p.parts):
        return False
    if change not in {Change.modified, Change.added}:
        return False

    name = p.name
    # react to master edits, not generated index.qmd etc.
    if p.suffix.lower() in MASTER_SUFFIXES and name.startswith("master-"):
        return True

    # react to Quarto + metadata/sidebar conf updates
    if any(fnmatch(name, pat) for pat in GENERATED_CONFIG_PATTERNS):
        return False
    return any(fnmatch(name, pat) for pat in CONFIG_PATTERNS)

if __name__ == "__main__":
    try:
        run_process(
            ".",
            target=build,
            debounce=1000,
            watch_filter=watch_filter,
        )
    except KeyboardInterrupt:
        print("\n[watch] stopped")
