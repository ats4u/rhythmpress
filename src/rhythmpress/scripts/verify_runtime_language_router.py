#!/usr/bin/env python3
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from rhythmpress import rhythmpress as rp


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rhythmpress-runtime-router-") as td:
        root = Path(td)
        _write(root / "_quarto-en.yml", "lang: en\n")
        _write(root / "_metadata-ja.yml", "lang: ja\n")
        _write(
            root / "_rhythmpress.conf",
            "\n".join(
                [
                    "# router config",
                    "default_lang=ja",
                    "lang_path.en=/en/",
                    "lang_path.ja=/ja/",
                    "",
                ]
            ),
        )
        (root / "en").mkdir()

        cwd = Path.cwd()
        try:
            os.chdir(root / "en")
            os.environ["QUARTO_PROJECT_DIR"] = str(root)
            out = rp.create_runtime_language_router("../_rhythmpress.conf", "en", strict=True)
        finally:
            os.environ.pop("QUARTO_PROJECT_DIR", None)
            os.chdir(cwd)

        if "const AVAILABLE = [\"en\", \"ja\"];" not in out:
            raise AssertionError("missing expected language ids in script output")
        if "const DEFAULT_LANG = \"ja\";" not in out:
            raise AssertionError("missing expected default language in script output")
        if "window.location.replace(target);" not in out:
            raise AssertionError("missing redirect call in script output")

        try:
            rp.create_runtime_language_router("./_does_not_exist.conf", "en", strict=True)
            raise AssertionError("strict mode should raise on missing config")
        except FileNotFoundError:
            pass

        soft = rp.create_runtime_language_router("./_does_not_exist.conf", "en", strict=False)
        if "router warning" not in soft:
            raise AssertionError("non-strict mode should emit warning comment")

    print("OK: runtime language router strict/non-strict behavior verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
