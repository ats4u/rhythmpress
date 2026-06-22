from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import tempfile

import yaml

from rhythmpress.plugin_system import discover_state, inspect_package, render_plugin_wiring
from rhythmpress.scripts import rhythmpress_plugin


@contextlib.contextmanager
def chdir(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def capture_main(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = rhythmpress_plugin.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


def make_manifest(package_dir: Path, package_id: str, name: str) -> None:
    for rel in (
        "assets/example.css",
        "assets/example-resource.txt",
        "filters/example.lua",
        "includes/example-header.html",
        "includes/example-after-body.html",
        "assets/example-en.css",
    ):
        path = package_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    write_yaml(
        package_dir / "plugin.yml",
        {
            "id": package_id,
            "name": name,
            "version": "0.1.0",
            "quarto": {
                "global": {
                    "resources": ["assets/example-resource.txt"],
                    "format.html.css": ["assets/example.css"],
                    "format.html.filters": ["filters/example.lua"],
                    "format.html.include-in-header": ["includes/example-header.html"],
                    "format.html.include-after-body": ["includes/example-after-body.html"],
                },
                "metadata": {
                    "en": {
                        "format.html.css": ["assets/example-en.css"],
                    },
                },
            },
            "deploy": {
                "files": [
                    {
                        "from": "assets/example.css",
                        "to": "assets/example.css",
                    },
                ],
            },
        },
    )


def test_empty_project(root: Path) -> None:
    with chdir(root):
        code, stdout, stderr = capture_main(["list"])
    assert code == 0
    assert "No Rhythmpress plugins configured." in stdout
    assert stderr == ""


def test_discovery_and_list(root: Path) -> None:
    plugin_root = root / ".rhythmpress-plugins"
    write_yaml(
        plugin_root / "packages.yml",
        {
            "packages": [
                "alpha",
                "missing",
            ],
        },
    )
    make_manifest(plugin_root / "packages" / "alpha", "alpha", "Alpha Plugin")
    make_manifest(plugin_root / "packages" / "beta", "beta", "Beta Plugin")

    state = discover_state(root)
    assert [status.id for status in state.statuses] == ["alpha", "missing", "beta"]
    assert [status.status for status in state.statuses] == [
        "ok",
        "missing-package",
        "ok",
    ]
    assert [status.active for status in state.statuses] == [True, True, False]

    with chdir(root):
        code, stdout, stderr = capture_main(["list"])
    assert code == 0
    assert "alpha: ok (active)" in stdout
    assert "missing: missing-package (active)" in stdout
    assert "beta: ok (installed)" in stdout
    assert stderr == ""


def test_inspect(root: Path) -> None:
    by_id = inspect_package("alpha", root)
    assert by_id.status == "ok"
    assert by_id.manifest is not None
    assert by_id.manifest.name == "Alpha Plugin"

    by_path = inspect_package(str(root / ".rhythmpress-plugins" / "packages" / "beta"), root)
    assert by_path.status == "ok"
    assert by_path.manifest is not None
    assert by_path.manifest.id == "beta"

    with chdir(root):
        code, stdout, stderr = capture_main(["inspect", "alpha"])
    assert code == 0
    assert "id: alpha" in stdout
    assert "active: yes" in stdout
    assert "quarto.global keys: 5" in stdout
    assert "quarto.metadata languages: 1" in stdout
    assert "deploy.files: 1" in stdout
    assert stderr == ""

    with chdir(root):
        code, stdout, stderr = capture_main(["inspect", "missing"])
    assert code == 1
    assert stdout == ""
    assert "missing-package" in stderr


def test_render() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        plugin_root = root / ".rhythmpress-plugins"
        write_yaml(plugin_root / "packages.yml", {"packages": ["alpha", "beta"]})
        make_manifest(plugin_root / "packages" / "alpha", "alpha", "Alpha Plugin")
        make_manifest(plugin_root / "packages" / "beta", "beta", "Beta Plugin")

        result = render_plugin_wiring(root)
        assert [item.path.name for item in result.files] == [
            "_quarto.plugins.yml",
            "_metadata-en.plugins.yml",
        ]
        assert all(item.changed for item in result.files)

        quarto = yaml.safe_load(
            (plugin_root / "generated" / "_quarto.plugins.yml").read_text(encoding="utf-8")
        )
        assert quarto == {
            "resources": [
                ".rhythmpress-plugins/packages/alpha/assets/example-resource.txt",
                ".rhythmpress-plugins/packages/beta/assets/example-resource.txt",
            ],
            "format": {
                "html": {
                    "css": [
                        ".rhythmpress-plugins/packages/alpha/assets/example.css",
                        ".rhythmpress-plugins/packages/beta/assets/example.css",
                    ],
                    "filters": [
                        ".rhythmpress-plugins/packages/alpha/filters/example.lua",
                        ".rhythmpress-plugins/packages/beta/filters/example.lua",
                    ],
                    "include-in-header": [
                        ".rhythmpress-plugins/packages/alpha/includes/example-header.html",
                        ".rhythmpress-plugins/packages/beta/includes/example-header.html",
                    ],
                    "include-after-body": [
                        ".rhythmpress-plugins/packages/alpha/includes/example-after-body.html",
                        ".rhythmpress-plugins/packages/beta/includes/example-after-body.html",
                    ],
                },
            },
        }

        metadata = yaml.safe_load(
            (plugin_root / "generated" / "_metadata-en.plugins.yml").read_text(encoding="utf-8")
        )
        assert metadata == {
            "format": {
                "html": {
                    "css": [
                        ".rhythmpress-plugins/packages/alpha/assets/example-en.css",
                        ".rhythmpress-plugins/packages/beta/assets/example-en.css",
                    ],
                },
            },
        }

        second = render_plugin_wiring(root)
        assert not any(item.changed for item in second.files)

        with chdir(root):
            code, stdout, stderr = capture_main(["render"])
        assert code == 0
        assert "Active packages: 2" in stdout
        assert "unchanged: .rhythmpress-plugins/generated/_quarto.plugins.yml" in stdout
        assert stderr == ""


def test_render_rejects_invalid_quarto_key() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        plugin_root = root / ".rhythmpress-plugins"
        write_yaml(plugin_root / "packages.yml", {"packages": ["bad"]})
        write_yaml(
            plugin_root / "packages" / "bad" / "plugin.yml",
            {
                "id": "bad",
                "version": "0.1.0",
                "quarto": {
                    "global": {
                        "website.title": ["not-supported"],
                    },
                },
            },
        )

        with chdir(root):
            code, stdout, stderr = capture_main(["render"])
        assert code == 1
        assert stdout == ""
        assert "unsupported quarto.global key: website.title" in stderr


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        test_empty_project(root)
        test_discovery_and_list(root)
        test_inspect(root)
    test_render()
    test_render_rejects_invalid_quarto_key()

    print("OK: plugin system")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
