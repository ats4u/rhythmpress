#!/usr/bin/env python3
"""
rhythmpedia-preproc.py

Dispatcher for:  rhythmpedia preproc [DIR]

- Reads ./[DIR]/master-[langid].qmd (langid from --lang, $LANG_ID, or auto)
- Parses front matter and gets 'rhythmpedia-preproc' (defaults to 'copy')
- Delegates to external command:  rhythmpedia preproc-<PREPROC>  (pass-through args)

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
from typing import Optional, Tuple


FRONT_MATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*", re.DOTALL)


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpedia preproc",
        description="Dispatch to rhythmpedia preproc-* based on front matter key 'rhythmpedia-preproc'.",
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
        # If exactly one, we could infer; multiple is ambiguous.
        names = ", ".join(m.name for m in matches)
        die(2, f"Multiple candidates found under {dirpath}: {names}. Use --lang or set $LANG_ID.")
    only = matches[0]
    # extract langid from filename
    m = re.match(r"master-(.+)\.qmd$", only.name)
    if not m:
        die(2, f"Cannot extract langid from {only.name}")
    return m.group(1), only


def read_front_matter(doc: str) -> dict:
    # Minimal YAML loader without external deps.
    # We only need the single key 'rhythmpedia-preproc' (string).
    # We'll parse a tiny subset safely.
    m = FRONT_MATTER_RE.match(doc)
    if not m:
        return {}
    block = m.group(1)
    fm: dict[str, str] = {}
    for line in block.splitlines():
        # ignore comments and empty lines
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            # strip quotes and whitespace
            val = val.strip().strip("'").strip('"')
            fm[key] = val
    return fm


def extract_preproc(qmd_path: Path) -> str:
    text = qmd_path.read_text(encoding="utf-8")
    fm = read_front_matter(text)
    preproc = fm.get("rhythmpedia-preproc", "").strip()
    return preproc or "copy"


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
    preproc = extract_preproc(master_qmd)

    # Build delegate command
    sub = f"preproc-{preproc}"
    this_file = Path(__file__).resolve()
    exe = resolve_rhythmpedia_exe(this_file)
    if not exe:
        die(3, "Cannot find 'rhythmpedia' executable (not in PATH and not in local bin/).")

    # Pass through original args (dirname/flags) to the delegate.
    delegate_argv = [exe, sub] + sys.argv[1:]

    # Ensure LANG_ID is exported for downstream if not explicitly set
    env = os.environ.copy()
    env.setdefault("LANG_ID", lang)

    if ns.verbose:
        print(f"[preproc] lang={lang} file={master_qmd.name} key=rhythmpedia-preproc value='{preproc}'")
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

