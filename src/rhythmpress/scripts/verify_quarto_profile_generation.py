#!/usr/bin/env python3
"""
Regression check for rhythmpress_quarto_profile profile config generation.

It creates a temporary mini project, generates _quarto-en.yml/_quarto-ja.yml,
and asserts language-scoped render rules, output dirs, and preserved post-render.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict, List

import yaml

from rhythmpress.lang_registry import to_bcp47_lang_tag
from rhythmpress.scripts import rhythmpress_quarto_profile


def _write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _assert_profile(tmp: Path, lang: str) -> None:
    exit_code = rhythmpress_quarto_profile.main(["--lang", lang, "--quiet"])
    if exit_code != 0:
        raise AssertionError(f"quarto-profile failed for {lang}: exit {exit_code}")

    doc = _load_yaml(tmp / f"_quarto-{lang}.yml")
    project = doc.get("project", {})
    render = project.get("render")
    expected_render: List[str] = [
        "**/*.qmd",
        "!**/master*.md",
        "!**/master*.qmd",
        "!drafts/*",
        "index.md",
        "*.qmd",
        f"**/{lang}/**/*.qmd",
        "!**/master*.md",
        "!**/master*.qmd",
        "!drafts/**",
    ]
    if render != expected_render:
        raise AssertionError(f"unexpected render for {lang}: {render!r}")
    if project.get("output-dir") != f".site-{lang}":
        raise AssertionError(f"unexpected output-dir for {lang}: {project.get('output-dir')!r}")

    expected_post_render = [
        f"rhythmpress post-render-patch --output-dir .site-{lang} --lang-id {lang}",
        "rhythmpress sitemap",
    ]
    if project.get("post-render") != expected_post_render:
        raise AssertionError(f"unexpected post-render for {lang}: {project.get('post-render')!r}")

    if doc.get("lang") != to_bcp47_lang_tag(lang):
        raise AssertionError(f"unexpected lang tag for {lang}: {doc.get('lang')!r}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rhythmpress-quarto-profile-") as td:
        tmp = Path(td)
        _write_yaml(
            tmp / "_quarto.yml",
            {
                "project": {
                    "type": "website",
                    "output-dir": ".site",
                    "preview": {"port": 5150, "browser": False},
                    "render": [
                        "**/*.qmd",
                        "!**/master*.md",
                        "!**/master*.qmd",
                        "!drafts/*",
                    ],
                    "post-render": ["rhythmpress sitemap"],
                }
            },
        )

        for lang in ("en", "ja"):
            _write_yaml(tmp / f"_metadata-{lang}.yml", {"lang": lang})
            _write_yaml(
                tmp / f"_sidebar-{lang}.generated.yml",
                {"website": {"sidebar": {"contents": [f"demo/{lang}/index.qmd"]}}},
            )

        # Ensure legacy malformed gated command is stripped during generation.
        base = _load_yaml(tmp / "_quarto.yml")
        base["project"]["post-render"].append(
            "bash -lc '[ \"${QUARTO_PROFILE:-}\" = \"en\" ] && rhythmpress sitemap || true'"
        )
        _write_yaml(tmp / "_quarto.yml", base)

        cwd = Path.cwd()
        try:
            # The generator resolves default paths relative to cwd.
            import os

            os.chdir(tmp)
            _assert_profile(tmp, "en")
            _assert_profile(tmp, "ja")
        finally:
            os.chdir(cwd)

    print("OK: generated profile YAMLs have expected render/output/post-render settings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
