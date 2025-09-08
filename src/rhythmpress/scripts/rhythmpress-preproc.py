#!/usr/bin/env python3
"""
rhythmpress-preproc.py

Dispatcher for:  rhythmpress preproc [DIR]

- Reads ./[DIR]/master-[langid].qmd (langid from $LANG_ID or auto)
- Front matter keys:
    - 'rhythmpress-preproc'       → handler name (default: 'copy')
    - 'rhythmpress-preproc-args'  → list of strings (extra args)
- Delegates to:  rhythmpress preproc-<PREPROC> [fm-args] [dirname] [extra CLI args]
"""

from __future__ import annotations
import argparse, os, re, sys, subprocess
from pathlib import Path
from shutil import which
from typing import Optional, Tuple, List

FRONT_MATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*", re.DOTALL)


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(
        prog="rhythmpress preproc",
        description="Dispatch to rhythmpress preproc-* based on front matter.",
        add_help=True,
    )
    p.add_argument(
        "dirname",
        nargs="?",
        default=".",
        help="Directory containing master-[langid].qmd (default: .)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print what is being delegated.",
    )
    return p.parse_known_args(argv)


# def find_langid(dirpath: Path) -> Tuple[str, Path]:
#     env_lang = os.environ.get("LANG_ID")
#     if env_lang:
#         p = dirpath / f"master-{env_lang}.qmd"
#         if p.exists():
#             return env_lang, p
#     matches = sorted(dirpath.glob("master-*.qmd"))
#     if not matches:
#         die(2, f"No master-*.qmd found under {dirpath}")
#     if len(matches) > 1:
#         die(2, f"Ambiguous: {', '.join(m.name for m in matches)}. Set $LANG_ID.")
#     m = re.match(r"master-(.+)\.qmd$", matches[0].name)
#     if not m:
#         die(2, f"Cannot extract langid from {matches[0].name}")
#     return m.group(1), matches[0]

import os, re
from pathlib import Path
from typing import Tuple

def find_langid(dirpath: Path) -> Tuple[str, Path]:
    """
    Find master-{lang}.qmd or master-{lang}.md under dirpath.
    Preference order per lang: .qmd > .md
    If $LANG_ID is set: require that lang; check .qmd first then .md.
    """
    env_lang = os.environ.get("LANG_ID")

    # Helper: path for a given lang with preference .qmd > .md
    def pick_for_lang(lang: str) -> Path | None:
        qmd = dirpath / f"master-{lang}.qmd"
        if qmd.exists():
            return qmd
        md = dirpath / f"master-{lang}.md"
        if md.exists():
            return md
        return None

    if env_lang:
        p = pick_for_lang(env_lang)
        if p:
            return env_lang, p
        # Show what *does* exist to help the user
        existing = sorted([*dirpath.glob("master-*.qmd"), *dirpath.glob("master-*.md")])
        names = ", ".join(x.name for x in existing) or "none"
        die(2, f"No master-{env_lang}.qmd/md found under {dirpath}. Existing: {names}")

    # Auto-detect: collect candidates for all langs, preferring .qmd when both exist
    candidates = {}
    for p in sorted([*dirpath.glob("master-*.qmd"), *dirpath.glob("master-*.md")]):
        m = re.match(r"master-(.+)\.(qmd|md)$", p.name)
        if not m:
            continue
        lang = m.group(1)
        # prefer .qmd if present; only set if lang not seen or current is .qmd
        if lang not in candidates or p.suffix == ".qmd":
            candidates[lang] = p

    if not candidates:
        die(2, f"No master-*.qmd/md found under {dirpath}")

    if len(candidates) > 1:
        # Ambiguous across languages
        listed = ", ".join(sorted(p.name for p in dirpath.glob("master-*.qmd")) +
                           sorted(p.name for p in dirpath.glob("master-*.md")))
        die(2, f"Ambiguous: {listed}. Set $LANG_ID.")

    # Exactly one language selected
    lang, path = next(iter(candidates.items()))
    return lang, path



def parse_front_matter(block: str) -> tuple[str, List[str]]:
    preproc, preproc_args = None, []
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("rhythmpress-preproc:"):
            val = line.split(":", 1)[1].strip().strip("'\"")
            if val: preproc = val
            continue
        if line.startswith("rhythmpress-preproc-args:"):
            after = line.split(":", 1)[1].strip()
            if after.startswith("[") and after.endswith("]"):
                inner = after[1:-1].strip()
                if inner:
                    for item in inner.split(","):
                        preproc_args.append(item.strip().strip("'\""))
                continue
            while i < len(lines):
                li = lines[i]
                if re.match(r"^\s*-\s+.+", li):
                    item = re.sub(r"^\s*-\s+", "", li).strip().strip("'\"")
                    preproc_args.append(item)
                    i += 1; continue
                if li.strip() == "":
                    i += 1; continue
                if re.match(r"^[^\s].*:\s*", li):
                    break
                break
    return preproc or "copy", preproc_args


def extract_preproc_and_args(qmd_path: Path) -> tuple[str, List[str]]:
    text = qmd_path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return "copy", []
    return parse_front_matter(m.group(1))


def resolve_rhythmpress_exe(this_file: Path) -> Optional[str]:
    exe = which("rhythmpress")
    if exe: return exe
    here = Path(__file__).resolve()
    for cand in [here.parent / "rhythmpress", here.parent.parent / "bin" / "rhythmpress"]:
        if cand.exists() and os.access(cand, os.X_OK):
            return str(cand)
    return None


def main(argv: list[str]) -> int:
    ns, unknown = parse_args(argv)
    dirpath = Path(ns.dirname).resolve()
    if not dirpath.is_dir():
        die(2, f"Not a directory: {dirpath}")
    lang, master_qmd = find_langid(dirpath)
    preproc, fm_args = extract_preproc_and_args(master_qmd)

    exe = resolve_rhythmpress_exe(Path(__file__))
    if not exe:
        die(3, "Cannot find 'rhythmpress' executable.")

    env = os.environ.copy()
    env.setdefault("LANG_ID", lang)

    passthru = [ns.dirname] + unknown
    delegate_argv = [exe, f"preproc-{preproc}", *fm_args, *passthru]

    if ns.verbose:
        print(f"[preproc] lang={lang} file={master_qmd.name} handler={preproc} fm_args={fm_args}")
        print(f"[preproc] passthru={passthru}")
        print(f"[preproc] exec: {' '.join(delegate_argv)}")

    try:
        return subprocess.run(delegate_argv, env=env).returncode
    except Exception as e:
        die(3, f"Delegate failed: {e!r}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

