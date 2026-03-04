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
            switcher = rp.create_runtime_language_switcher("../_rhythmpress.conf", "en", strict=True)
            switcher_links = rp.create_runtime_language_switcher_links(
                "../_rhythmpress.conf", "en", strict=True
            )
            switcher_data_js = rp.create_runtime_language_switcher_data_js(
                "../_rhythmpress.conf", "en", strict=True
            )
            switcher_ui_js = rp.create_runtime_language_switcher_ui_js()
            switcher_js = rp.create_runtime_language_switcher_js("../_rhythmpress.conf", "en", strict=True)
            root_default = rp.create_runtime_root_entry("../_rhythmpress.conf", "en", strict=True)
            os.environ["RHYTHMPRESS_PREVIEW"] = "1"
            root_preview = rp.create_runtime_root_entry("../_rhythmpress.conf", "en", strict=True)
        finally:
            os.environ.pop("RHYTHMPRESS_PREVIEW", None)
            os.environ.pop("QUARTO_PROJECT_DIR", None)
            os.chdir(cwd)

        if "const AVAILABLE = [\"en\", \"ja\"];" not in out:
            raise AssertionError("missing expected language ids in script output")
        if "const DEFAULT_LANG = \"ja\";" not in out:
            raise AssertionError("missing expected default language in script output")
        if "window.location.replace(target);" not in out:
            raise AssertionError("missing redirect call in script output")

        if 'id="rhythmpress-lang-switcher"' not in switcher:
            raise AssertionError("missing language switcher select element")
        if "localStorage.setItem('rhythmpress_lang'" not in switcher:
            raise AssertionError("missing choice persistence in switcher output")
        if "window.location.assign(targetUrl);" not in switcher:
            raise AssertionError("missing current-page redirect in switcher output")
        if 'class="rhythmpress-lang-anchor"' not in switcher_links:
            raise AssertionError("missing anchor links in link switcher output")
        if "<br>" not in switcher_links:
            raise AssertionError("link switcher should use line breaks between entries")
        if "localStorage.setItem('rhythmpress_lang'" not in switcher_links:
            raise AssertionError("missing choice persistence in link switcher output")
        if "function mount()" not in switcher_js:
            raise AssertionError("missing toolbar mount function in switcher JS output")
        if "rhythmpress-lang-switcher" not in switcher_js:
            raise AssertionError("missing switcher element id in generated JS output")
        if "globalThis.RHYTHMPRESS_LANG_SWITCHER" not in switcher_data_js:
            raise AssertionError("missing global data object in switcher data JS output")
        if "const DATA = globalThis.RHYTHMPRESS_LANG_SWITCHER;" not in switcher_ui_js:
            raise AssertionError("missing global data read in switcher UI JS output")
        if "window.location.replace(target);" not in root_default:
            raise AssertionError("default root entry should emit router redirect")
        if 'class="rhythmpress-lang-anchor"' not in root_preview:
            raise AssertionError("preview root entry should emit anchor link switcher")

        try:
            rp.create_runtime_language_router("./_does_not_exist.conf", "en", strict=True)
            raise AssertionError("strict mode should raise on missing config")
        except FileNotFoundError:
            pass

        soft = rp.create_runtime_language_router("./_does_not_exist.conf", "en", strict=False)
        if "router warning" not in soft:
            raise AssertionError("non-strict mode should emit warning comment")
        soft_switcher = rp.create_runtime_language_switcher("./_does_not_exist.conf", "en", strict=False)
        if "router warning" not in soft_switcher:
            raise AssertionError("switcher non-strict mode should emit warning comment")
        soft_switcher_links = rp.create_runtime_language_switcher_links(
            "./_does_not_exist.conf", "en", strict=False
        )
        if "router warning" not in soft_switcher_links:
            raise AssertionError("link switcher non-strict mode should emit warning comment")
        soft_switcher_js = rp.create_runtime_language_switcher_js("./_does_not_exist.conf", "en", strict=False)
        if "generated no-op switcher" not in soft_switcher_js:
            raise AssertionError("switcher JS non-strict mode should emit no-op warning")
        soft_data_js = rp.create_runtime_language_switcher_data_js("./_does_not_exist.conf", "en", strict=False)
        if "generated no-op switcher" not in soft_data_js:
            raise AssertionError("switcher data JS non-strict mode should emit no-op warning")

    print("OK: runtime language router/switcher(+js) strict/non-strict behavior verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
