#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import rhythmpress as rp


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rhythmpress_render_lang_switcher_js",
        description="Generate a runtime toolbar language switcher JavaScript file.",
    )
    p.add_argument(
        "--conf",
        default="_rhythmpress.conf",
        help="Path to rhythmpress config (default: _rhythmpress.conf).",
    )
    p.add_argument(
        "--current-lang",
        default="en",
        help="Current language hint (default: en).",
    )
    p.add_argument(
        "--out",
        default="lang-switcher.generated.mjs",
        help="Output JS file path (default: ./lang-switcher.generated.mjs).",
    )
    p.add_argument(
        "--mode",
        choices=("all", "data", "ui"),
        default="all",
        help="Output mode: combined data+ui, data only, or ui only (default: all).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing/invalid runtime config.",
    )
    p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output.",
    )
    return p.parse_args(argv)


def write_if_changed(path: Path, text: str) -> bool:
    try:
        old = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        old = None
    if old == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    out_path = Path(ns.out)

    if ns.mode == "data":
        js = rp.create_runtime_language_switcher_data_js(
            input_conf=ns.conf,
            current_lang=ns.current_lang,
            strict=ns.strict,
        )
    elif ns.mode == "ui":
        js = rp.create_runtime_language_switcher_ui_js()
    else:
        js = rp.create_runtime_language_switcher_js(
            input_conf=ns.conf,
            current_lang=ns.current_lang,
            strict=ns.strict,
        )
    if not js.endswith("\n"):
        js += "\n"

    changed = write_if_changed(out_path, js)
    if not ns.quiet:
        if changed:
            print(f"[INFO] generated: {out_path}")
        else:
            print(f"[INFO] unchanged: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
