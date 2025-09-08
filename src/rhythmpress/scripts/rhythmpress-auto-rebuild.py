#!/usr/bin/env python3
import subprocess
from pathlib import Path
from watchfiles import run_process, Change

IGNORES  = {".git", ".venv", "node_modules", ".quarto", ".obsidian",
            "__pycache__", ".site", "_site"}
SUFFIXES = {".qmd", ".md"}  # what we care about

def build():
    print("[watch] master changed → rebuilding…")
    return subprocess.call(["rhythmpress-build.py", "--skip-clean"])

def watch_filter(change, path: str) -> bool:
    p = Path(path)
    # ignore noisy dirs
    if any(part in IGNORES for part in p.parts):
        return False
    # only react to master files, not generated index.qmd etc.
    if p.suffix.lower() not in SUFFIXES:
        return False
    if not p.name.startswith("master-"):
        return False
    # trigger on edits (and optionally on new masters)
    return change in {Change.modified, Change.added}

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
