#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from rhythmpress.scripts.rhythmpress_post_render_patch import resolve_output_dir


STEP_SPECS = (
    {
        "name": "sitemap",
        "command": ("rhythmpress", "sitemap"),
        "skip_attr": "skip_sitemap",
    },
    {
        "name": "render-social-cards",
        "command": ("rhythmpress", "render-social-cards"),
        "skip_attr": "skip_social_cards",
    },
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_finalize",
        description=(
            "Finalize a rendered Rhythmpress site artifact. "
            "Runs sitemap and social-card generation against one output directory."
        ),
    )
    p.add_argument(
        "--output-dir",
        default="",
        help=(
            "Final site output directory. "
            "Default: QUARTO_PROJECT_OUTPUT_DIR env, else _quarto.yml project.output-dir, else _site."
        ),
    )
    p.add_argument(
        "--site-url",
        default="",
        help="Absolute deployed site URL. Passed through to sitemap and render-social-cards.",
    )
    p.add_argument(
        "--skip-sitemap",
        action="store_true",
        help="Skip sitemap generation.",
    )
    p.add_argument(
        "--skip-social-cards",
        action="store_true",
        help="Skip social-card generation.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned commands without executing them.",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print commands before running them.",
    )
    return p.parse_args(argv)


def _resolved_output_dir(cli_output_dir: str) -> Path:
    return Path(resolve_output_dir(cli_output_dir)).resolve()


def _build_env(output_dir: Path, site_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env["QUARTO_PROJECT_OUTPUT_DIR"] = str(output_dir)
    if site_url.strip():
        normalized = site_url.strip().rstrip("/") + "/"
        env["SITE_URL"] = normalized
        env["RHYTHMPRESS_SITE_URL"] = normalized
    return env


def _iter_steps(ns: argparse.Namespace) -> list[tuple[str, tuple[str, ...]]]:
    steps: list[tuple[str, tuple[str, ...]]] = []
    for spec in STEP_SPECS:
        if getattr(ns, spec["skip_attr"]):
            continue
        steps.append((spec["name"], spec["command"]))
    return steps


def _run(cmd: Sequence[str], *, env: dict[str, str], verbose: bool, dry_run: bool) -> int:
    if verbose or dry_run:
        print("[finalize] exec:", " ".join(shlex.quote(part) for part in cmd))
    if dry_run:
        return 0
    try:
        return subprocess.run(list(cmd), env=env).returncode
    except FileNotFoundError:
        print(f"[finalize] command not found: {cmd[0]}", file=sys.stderr)
        return 127


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    output_dir = _resolved_output_dir(ns.output_dir)
    if not output_dir.is_dir():
        print(f"[finalize] output dir not found: {output_dir}", file=sys.stderr)
        return 2

    steps = _iter_steps(ns)
    if not steps:
        print("[finalize] all steps are skipped; nothing to do", file=sys.stderr)
        return 2

    env = _build_env(output_dir, ns.site_url)
    for step_name, cmd in steps:
        rc = _run(cmd, env=env, verbose=ns.verbose, dry_run=ns.dry_run)
        if rc != 0:
            print(f"[finalize] step failed: {step_name} (exit {rc})", file=sys.stderr)
            return rc

    print(f"[finalize] completed: output={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
