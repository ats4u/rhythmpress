#!/usr/bin/env python3
"""
Regression check for project-level TOC template override resolution.
"""

from __future__ import annotations

import json
import sys
import tempfile
import types
from pathlib import Path

from rhythmpress import rhythmpress


class _JsonYamlShim:
    @staticmethod
    def safe_load(stream):
        text = stream.read() if hasattr(stream, "read") else str(stream)
        return json.loads(text) if text.strip() else {}


try:
    import yaml  # noqa: F401
except ModuleNotFoundError:
    yaml = types.ModuleType("yaml")
    yaml.safe_load = _JsonYamlShim.safe_load
    sys.modules["yaml"] = yaml


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_config(path: Path, data: dict) -> None:
    _write(path, json.dumps(data, ensure_ascii=False, indent=2))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rhythmpress-toc-template-") as td:
        tmp = Path(td)
        article = tmp / "article" / "master-en.qmd"
        _write(article, "---\ntitle: Test\n---\n\n## Heading\n")

        default_template = rhythmpress._default_toc_template_path()

        resolved = rhythmpress._resolve_toc_template_path(article)
        if resolved != default_template:
            raise AssertionError(f"unexpected default template without _quarto.yml: {resolved}")

        _write_config(tmp / "_quarto.yml", {"project": {"type": "website"}})
        resolved = rhythmpress._resolve_toc_template_path(article)
        if resolved != default_template:
            raise AssertionError(f"unexpected default template without override: {resolved}")

        custom_template = tmp / ".rhythmpress" / "templates" / "toc.markdown"
        _write(custom_template, "$toc$\n")
        _write_config(
            tmp / "_quarto.yml",
            {
                "project": {"type": "website"},
                "rhythmpress": {
                    "templates": {
                        "toc": ".rhythmpress/templates/toc.markdown",
                    },
                },
            },
        )

        resolved = rhythmpress._resolve_toc_template_path(article)
        if resolved != custom_template.resolve():
            raise AssertionError(f"unexpected custom template: {resolved}")

        _write_config(
            tmp / "_quarto.yml",
            {
                "project": {"type": "website"},
                "rhythmpress": {
                    "templates": {
                        "toc": ".rhythmpress/templates/missing.markdown",
                    },
                },
            },
        )
        try:
            rhythmpress._resolve_toc_template_path(article)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing configured template did not fail")

    print("OK: TOC template override resolves from _quarto.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
