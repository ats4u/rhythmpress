#!/usr/bin/env python3
"""
Regression check for title shortcode interpolation.

It creates a temporary mini project with both legacy variables and Quarto
metadata, then asserts that:

* `{{< var ... >}}` resolves only from variable sources
* `{{< meta ... >}}` resolves from the merged Quarto metadata document
* both title interpolation paths share the same behavior
"""

from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from rhythmpress import rhythmpress
from rhythmpress import quarto_vars


class _JsonYamlShim:
    @staticmethod
    def safe_load(stream: Any) -> Dict[str, Any]:
        text = stream.read() if hasattr(stream, "read") else str(stream)
        return json.loads(text) if text.strip() else {}


if quarto_vars.yaml is None:
    quarto_vars.yaml = _JsonYamlShim()


def _write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rhythmpress-title-shortcodes-") as td:
        tmp = Path(td)

        _write_yaml(
            tmp / "_quarto.yml",
            {
                "variables": {
                    "shared": "quarto-var",
                    "var_only_from_quarto": "quarto-only-var",
                },
                "var": {
                    "MORA_SPEAKERS": {
                        "en": "Mora-Timed Language Speakers",
                        "ja": "Mora-Timed Language Speakers in Japanese",
                    }
                },
                "metadata": {
                    "shared": "quarto-meta",
                    "meta_only_from_quarto": "quarto-only-meta",
                    "nested": {"label": "base-meta-label"},
                },
            },
        )
        _write_yaml(
            tmp / "_variables.yml",
            {
                "shared": "root-var",
                "var_only": "root-var-only",
                "nested": {"label": "root-var-label"},
            },
        )
        _write_yaml(
            tmp / "_variables-ja.yml",
            {
                "shared": "ja-var",
                "var_only": "ja-var-only",
                "nested": {"label": "ja-var-label"},
            },
        )
        _write_yaml(
            tmp / "_metadata-ja.yml",
            {
                "shared": "ja-meta",
                "meta_only": "ja-meta-only",
                "nested": {"label": "ja-meta-label"},
            },
        )

        old_env = os.environ.get("TITLE_SUFFIX")
        os.environ["TITLE_SUFFIX"] = "preview"
        try:
            contexts = quarto_vars.get_title_shortcode_contexts(cwd=tmp, lang="ja")
            if contexts["var"].get("shared") != "ja-var":
                raise AssertionError(f"unexpected var shared: {contexts['var'].get('shared')!r}")
            if contexts["meta"].get("shared") != "ja-meta":
                raise AssertionError(f"unexpected meta shared: {contexts['meta'].get('shared')!r}")
            if contexts["var"].get("var_only_from_quarto") != "quarto-only-var":
                raise AssertionError("missing _quarto.yml variables in var context")
            if contexts["meta"].get("meta_only_from_quarto") != "quarto-only-meta":
                raise AssertionError("missing _quarto.yml metadata in meta context")
            if contexts["meta"].get("var", {}).get("MORA_SPEAKERS", {}).get("en") != "Mora-Timed Language Speakers":
                raise AssertionError("missing top-level Quarto metadata in meta context")

            direct = rhythmpress._interpolate_quarto_vars_in_text(
                "{{< var shared >}} / {{< meta shared >}} / {{< var env:TITLE_SUFFIX >}}",
                str(tmp),
                "ja",
            )
            if direct != "ja-var / ja-meta / preview":
                raise AssertionError(f"unexpected direct interpolation: {direct!r}")

            wrong_scope = rhythmpress._interpolate_quarto_vars_in_text(
                "{{< var meta_only >}}|{{< meta var_only >}}",
                str(tmp),
                "ja",
            )
            if wrong_scope != "|":
                raise AssertionError(f"unexpected wrong-scope interpolation: {wrong_scope!r}")

            actual_case = rhythmpress._interpolate_quarto_vars_in_text(
                "A Letter to {{< meta var.MORA_SPEAKERS.en >}}",
                str(tmp),
                "ja",
            )
            if actual_case != "A Letter to Mora-Timed Language Speakers":
                raise AssertionError(f"unexpected actual-case interpolation: {actual_case!r}")

            items = [
                {
                    "level": 2,
                    "title_raw": "{{< meta nested.label >}}",
                    "header_title": "{{< var nested.label >}}",
                    "header_slug": None,
                    "description": "",
                }
            ]
            processed = rhythmpress.proc_qmd_teasers(deepcopy(items), str(tmp), "ja")
            item = processed[0]
            if item["title_raw"] != "ja-meta-label":
                raise AssertionError(f"unexpected title_raw: {item['title_raw']!r}")
            if item["header_title"] != "ja-var-label":
                raise AssertionError(f"unexpected header_title: {item['header_title']!r}")
            if item["slug"] != "ja-meta-label":
                raise AssertionError(f"unexpected slug: {item['slug']!r}")
        finally:
            if old_env is None:
                os.environ.pop("TITLE_SUFFIX", None)
            else:
                os.environ["TITLE_SUFFIX"] = old_env

    print("OK: title shortcode interpolation keeps var/meta sources separate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
