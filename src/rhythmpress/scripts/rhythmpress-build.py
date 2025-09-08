#!/usr/bin/env python3
"""
rhythmpress-build.py

Batch builder for Rhythmpedia projects.

For each directory listed in a definition file:
  1) rhythmpress preproc-clean <dir> --apply --force
  2) rhythmpress preproc       <dir>
Finally:
  3) rhythmpress render-sidebar <conf>

Definition file format:
  - One directory per line.
  - Lines starting with '#' are comments.
  - Inline comments after ' # ' are allowed.
  - Blank lines are ignored.

Defaults match your current shell script (apply+force clean, then preproc, then render sidebar).
"""

from __future__ import annotations
import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


def die(code: int, msg: str) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress-build",
        description="Run preproc-clean + preproc over a set of pages, then render sidebar.",
    )
    p.add_argument("--defs", default="_rhythmpress.conf",
                   help="Path to definition file (default: _rhythmpress.conf). If '-' use stdin.")
    p.add_argument("--sidebar", default="_sidebar-ja.conf",
                   help="Sidebar conf to render at the end (default: _sidebar-ja.conf).")
    p.add_argument("--no-sidebar", action="store_true",
                   help="Skip render-sidebar step.")
    p.add_argument("--apply-flags", nargs="*", default=["--apply", "--force"],
                   help="Flags passed to `preproc-clean` (default: --apply --force).")
    p.add_argument("--skip-clean", action="store_true",
                   help="Skip the preproc-clean step.")
    p.add_argument("--keep-going", "-k", action="store_true",
                   help="Continue after errors (default: stop at first error).")
    p.add_argument("--chdir", default=".",
                   help="Change working directory before running (default: .).")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print commands before running.")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would run, but don’t execute.")
    return p.parse_args(argv)


def read_def_lines(src: Iterable[str]) -> List[str]:
    out: List[str] = []
    for raw in src:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # allow inline comments after ' # '
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        if line:
            out.append(line.strip())
    return out


def load_def_dirs(defs_path: str) -> List[str]:
    if defs_path == "-":
        lines = sys.stdin.read().splitlines()
    else:
        p = Path(defs_path)
        if not p.exists():
            die(2, f"Definition file not found: {p}")
        lines = p.read_text(encoding="utf-8").splitlines()
    dirs = read_def_lines(lines)
    if not dirs:
        die(2, "No targets found in definition file.")
    # de-dup, keep order
    seen = set()
    ordered: List[str] = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            ordered.append(d)
    return ordered


def run(cmd: List[str], *, verbose: bool, dry_run: bool, env: dict | None = None) -> int:
    if verbose or dry_run:
        print("[RUN]", " ".join(shlex.quote(x) for x in cmd))
    if dry_run:
        return 0
    try:
        return subprocess.run(cmd, env=env).returncode
    except FileNotFoundError:
        print(f"[ERROR] command not found: {cmd[0]}", file=sys.stderr)
        return 127


def main(argv: List[str]) -> int:
    ns = parse_args(argv)

    # CWD
    workdir = Path(ns.chdir).resolve()
    if not workdir.is_dir():
        die(2, f"Not a directory: {workdir}")
    os.chdir(workdir)

    # Explicit environment (easy place to inject vars later if needed)
    env = os.environ.copy()

    targets = load_def_dirs(ns.defs)

    # Verify dirs exist (fail fast unless keep-going)
    existing: List[str] = []
    for d in targets:
        if not Path(d).is_dir():
            msg = f"Missing dir: {d}"
            if ns.keep_going:
                print(f"[WARN] {msg} (skipping)", file=sys.stderr)
                continue
            die(2, msg)
        existing.append(d)

    # Execute
    for d in existing:
        if not ns.skip_clean:
            rc = run(["rhythmpress", "preproc-clean", d, *ns.apply_flags],
                     verbose=ns.verbose, dry_run=ns.dry_run, env=env)
            if rc != 0:
                print(f"[FAIL] preproc-clean: {d} (exit {rc})", file=sys.stderr)
                if not ns.keep_going:
                    return rc
                else:
                    continue

        rc = run(["rhythmpress", "preproc", d],
                 verbose=ns.verbose, dry_run=ns.dry_run, env=env)
        if rc != 0:
            print(f"[FAIL] preproc: {d} (exit {rc})", file=sys.stderr)
            if not ns.keep_going:
                return rc

    if not ns.no_sidebar:
        # 0) First generate aggregated sidebar confs per language
        rc = run(["rhythmpress", "sidebar-confs", "--defs", ns.defs],
                 verbose=ns.verbose, dry_run=ns.dry_run, env=env)
        if rc != 0:
            print(f"[FAIL] sidebar-confs (exit {rc})", file=sys.stderr)
            if not ns.keep_going:
                return rc

        # 1) Ask rhythmpress for all lang IDs (one per line)
        if ns.verbose or ns.dry_run:
            print("[RUN]", "rhythmpress sidebar-langs --defs", shlex.quote(ns.defs))

        if ns.dry_run:
            langs = []
        else:
            proc = subprocess.run(
                ["rhythmpress", "sidebar-langs", "--defs", ns.defs],
                env=env,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                print(f"[WARN] sidebar-langs failed (exit {proc.returncode}); falling back to single sidebar",
                      file=sys.stderr)
                langs = []
            else:
                langs = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]

        # 2) If we received lang IDs, render each _sidebar-<lang>.yml
        if langs:
            seen = set()
            for lang in langs:
                if lang in seen:
                    continue
                seen.add(lang)
                out_name = f"_sidebar-{lang}.generated.conf"
                rc = run(["rhythmpress", "render-sidebar", out_name],
                         verbose=ns.verbose, dry_run=ns.dry_run, env=env)
                if rc != 0:
                    print(f"[FAIL] render-sidebar: {out_name} (exit {rc})", file=sys.stderr)
                    if not ns.keep_going:
                        return rc
        else:
            # 3) Fallback to the original single call if no langids were found
            rc = run(["rhythmpress", "render-sidebar", ns.sidebar],
                     verbose=ns.verbose, dry_run=ns.dry_run, env=env)
            if rc != 0 and not ns.keep_going:
                return rc

    print("[DONE] Build completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

