#!/usr/bin/env python3
"""
rhythmpedia-preproc.py

Dispatcher for:  rhythmpedia preproc [DIR]

- Reads ./[DIR]/master-[langid].qmd (langid from --lang, $LANG_ID, or auto)
- Front matter keys:
    - 'rhythmpedia-preproc'       → handler name (default: 'copy')
    - 'rhythmpedia-preproc-args'  → array of strings passed to handler
- Delegates to external command:  rhythmpedia preproc-<PREPROC>  (args injected)

Exit codes:
  0  success
  1  usage / argument error
  2  file not found / multiple candidates
  3  delegate command missing / failed
"""

from __future__ import annotations
import argparse
import os
import re
import sys
import subprocess
from pathlib import Path
from shutil import which
from typing import Optional, Tuple, List


FRONT_MATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*", re.DOTALL)


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpedia preproc",
        description="Dispatch to rhythmpedia preproc-* based on front matter keys.",
        add_help=True,
    )
    p.add_argument(
        "dirname",
        nargs="?",
        default=".",
        help="Directory containing master-[langid].qmd (default: .)",
    )
    p.add_argument(
        "--lang",
        dest="lang",
        help="Language ID (overrides $LANG_ID). If omitted, auto-detect master-*.qmd when unambiguous.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print what is being delegated.",
    )
    return p.parse_args(argv)


def find_langid(dirpath: Path, cli_lang: Optional[str]) -> Tuple[str, Path]:
    if cli_lang:  # explicit
        lang = cli_lang
        candidate = dirpath / f"master-{lang}.qmd"
        if not candidate.exists():
            die(2, f"master-{lang}.qmd not found under {dirpath}")
        return lang, candidate

    env_lang = os.environ.get("LANG_ID")
    if env_lang:
        candidate = dirpath / f"master-{env_lang}.qmd"
        if candidate.exists():
            return env_lang, candidate
        # fall through to auto if not found

    matches = sorted(dirpath.glob("master-*.qmd"))
    if not matches:
        die(2, f"No master-*.qmd found under {dirpath}")
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        die(2, f"Multiple candidates found under {dirpath}: {names}. Use --lang or set $LANG_ID.")
    only = matches[0]
    m = re.match(r"master-(.+)\.qmd$", only.name)
    if not m:
        die(2, f"Cannot extract langid from {only.name}")
    return m.group(1), only


def parse_front_matter_block(block: str) -> tuple[str, List[str]]:
    """
    Minimal YAML-ish parser for two keys:
      - rhythmpedia-preproc: <scalar>
      - rhythmpedia-preproc-args: [inline,list] or block list:
            rhythmpedia-preproc-args:
              - "--flag"
              - "value"
    Returns (preproc, preproc_args)
    """
    preproc: Optional[str] = None
    preproc_args: List[str] = []

    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        strip = line.strip()
        i += 1

        if not strip or strip.startswith("#"):
            continue

        # scalar key
        if strip.startswith("rhythmpedia-preproc:"):
            val = strip.split(":", 1)[1].strip().strip("'").strip('"')
            if val:
                preproc = val
            continue

        # args key (inline or block)
        if strip.startswith("rhythmpedia-preproc-args:"):
            after = strip.split(":", 1)[1].strip()
            # inline list: [a, "b", 'c d']
            if after.startswith("[") and after.endswith("]"):
                inner = after[1:-1].strip()
                if inner:
                    for item in inner.split(","):
                        preproc_args.append(item.strip().strip("'").strip('"'))
                continue

            # block list:
            #   - item
            #   - "item two"
            # Stop when a non-list top-level line appears.
            while i < len(lines):
                li = lines[i]
                li_strip = li.strip()
                if re.match(r"^\s*-\s+.+", li):
                    item = re.sub(r"^\s*-\s+", "", li).strip().strip("'").strip('"')
                    preproc_args.append(item)
                    i += 1
                    continue
                # empty line: keep scanning
                if li_strip == "":
                    i += 1
                    continue
                # new top-level key (no indent + has colon) → stop
                if re.match(r"^[^\s].*:\s*", li):
                    break
                # anything else → stop
                break
            continue

    return (preproc or "copy"), preproc_args


def extract_preproc_and_args(qmd_path: Path) -> tuple[str, List[str]]:
    text = qmd_path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return "copy", []
    return parse_front_matter_block(m.group(1))


def resolve_rhythmpedia_exe(this_file: Path) -> Optional[str]:
    # 1) PATH
    exe = which("rhythmpedia")
    if exe:
        return exe
    # 2) Project-local bin/rhythmpedia relative to this script
    bin_local = (this_file.parent / "rhythmpedia").resolve()
    if bin_local.exists() and os.access(bin_local, os.X_OK):
        return str(bin_local)
    # 3) One level up (common layout: project/bin/…)
    bin_up = (this_file.parent.parent / "bin" / "rhythmpedia").resolve()
    if bin_up.exists() and os.access(bin_up, os.X_OK):
        return str(bin_up)
    return None


def main(argv: list[str]) -> int:
    ns = parse_args(argv)
    dirpath = Path(ns.dirname).resolve()

    if not dirpath.exists() or not dirpath.is_dir():
        die(2, f"Not a directory: {dirpath}")

    lang, master_qmd = find_langid(dirpath, ns.lang)
    preproc, preproc_args = extract_preproc_and_args(master_qmd)

    # Build delegate command
    sub = f"preproc-{preproc}"
    this_file = Path(__file__).resolve()
    exe = resolve_rhythmpedia_exe(this_file)
    if not exe:
        die(3, "Cannot find 'rhythmpedia' executable (not in PATH and not in local bin/).")

    # Inject preproc-args before passthrough CLI args
    delegate_argv = [exe, sub, *preproc_args, *sys.argv[1:]]

    # Ensure LANG_ID is exported downstream if not explicitly set
    env = os.environ.copy()
    env.setdefault("LANG_ID", lang)

    if ns.verbose:
        print(f"[preproc] lang={lang} file={master_qmd.name} handler='{preproc}' args={preproc_args}")
        print(f"[preproc] exec: {' '.join(delegate_argv)}")
    try:
        r = subprocess.run(delegate_argv, env=env, check=False)
        return r.returncode
    except FileNotFoundError:
        die(3, f"Delegate command not found: {delegate_argv[0]}")
    except Exception as e:
        die(3, f"Delegate failed: {e!r}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

