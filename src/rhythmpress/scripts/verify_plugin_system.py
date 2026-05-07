from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import tempfile

import yaml

from rhythmpress.plugin_system import discover_state, inspect_package
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
    write_yaml(
        package_dir / "plugin.yml",
        {
            "id": package_id,
            "name": name,
            "version": "0.1.0",
            "quarto": {
                "global": {
                    "format": {
                        "html": {
                            "css": ["assets/example.css"],
                        },
                    },
                },
                "metadata": {
                    "en": {
                        "website": {
                            "title": "Example",
                        },
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
    assert "quarto.global keys: 1" in stdout
    assert "quarto.metadata languages: 1" in stdout
    assert "deploy.files: 1" in stdout
    assert stderr == ""

    with chdir(root):
        code, stdout, stderr = capture_main(["inspect", "missing"])
    assert code == 1
    assert stdout == ""
    assert "missing-package" in stderr


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        test_empty_project(root)
        test_discovery_and_list(root)
        test_inspect(root)

    print("OK: plugin system")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
