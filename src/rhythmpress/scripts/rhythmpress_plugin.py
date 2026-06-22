from __future__ import annotations

import sys
from pathlib import Path

from rhythmpress.plugin_system import (
    PluginSystemError,
    count_deploy_files,
    count_quarto_global_keys,
    count_quarto_metadata_languages,
    discover_state,
    render_plugin_wiring,
    inspect_package,
)


USAGE = """Usage:
  rhythmpress plugin list
  rhythmpress plugin inspect <plugin-id-or-path>
  rhythmpress plugin render
"""


def print_usage() -> None:
    print(USAGE.rstrip())


def format_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def command_list(argv: list[str]) -> int:
    if argv:
        if argv == ["--help"] or argv == ["-h"]:
            print("Usage: rhythmpress plugin list")
            return 0
        print("Usage: rhythmpress plugin list", file=sys.stderr)
        return 2

    try:
        state = discover_state()
    except PluginSystemError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not state.statuses:
        print("No Rhythmpress plugins configured.")
        print(f"Packages file: {format_path(state.packages_file)}")
        return 0

    print("Rhythmpress plugins:")
    for status in state.statuses:
        activity = "active" if status.active else "installed"

        details = ""
        if status.manifest is not None:
            label = status.manifest.name or status.manifest.id
            version = f" {status.manifest.version}" if status.manifest.version else ""
            details = f" - {label}{version}"
        elif status.message:
            details = f" - {status.message}"

        print(f"- {status.id}: {status.status} ({activity}){details}")
    return 0


def command_inspect(argv: list[str]) -> int:
    if argv == ["--help"] or argv == ["-h"]:
        print("Usage: rhythmpress plugin inspect <plugin-id-or-path>")
        return 0
    if len(argv) != 1:
        print("Usage: rhythmpress plugin inspect <plugin-id-or-path>", file=sys.stderr)
        return 2

    try:
        status = inspect_package(argv[0])
    except PluginSystemError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if status.status != "ok" or status.manifest is None:
        print(f"ERROR: {status.id}: {status.status}", file=sys.stderr)
        if status.message:
            print(status.message, file=sys.stderr)
        return 1

    manifest = status.manifest
    print(f"id: {manifest.id}")
    print(f"name: {manifest.name or ''}")
    print(f"version: {manifest.version or ''}")
    print(f"path: {format_path(status.package_dir)}")
    print(f"active: {'yes' if status.active else 'no'}")
    print(f"quarto.global keys: {count_quarto_global_keys(manifest)}")
    print(f"quarto.metadata languages: {count_quarto_metadata_languages(manifest)}")
    print(f"deploy.files: {count_deploy_files(manifest)}")
    return 0


def command_render(argv: list[str]) -> int:
    if argv == ["--help"] or argv == ["-h"]:
        print("Usage: rhythmpress plugin render")
        return 0
    if argv:
        print("Usage: rhythmpress plugin render", file=sys.stderr)
        return 2

    try:
        result = render_plugin_wiring()
    except PluginSystemError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Active packages: {len(result.active_package_ids)}")
    for generated in result.files:
        state = "generated" if generated.changed else "unchanged"
        print(f"{state}: {format_path(generated.path)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv == ["--help"] or argv == ["-h"]:
        print_usage()
        return 0 if argv else 2

    command = argv[0].replace("_", "-")
    rest = argv[1:]

    if command == "list":
        return command_list(rest)
    if command == "inspect":
        return command_inspect(rest)
    if command == "render":
        return command_render(rest)

    print_usage()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
