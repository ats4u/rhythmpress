from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml


PLUGIN_ROOT_NAME = ".rhythmpress-plugins"
PACKAGES_DIR_NAME = "packages"
PACKAGES_FILE_NAME = "packages.yml"
MANIFEST_FILE_NAME = "plugin.yml"
PACKAGE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class PluginSystemError(RuntimeError):
    """Base error for user-facing plugin system failures."""


@dataclass(frozen=True)
class ActivePackage:
    id: str


@dataclass(frozen=True)
class PluginManifest:
    id: str
    name: str | None
    version: str | None
    raw: dict[str, Any]
    path: Path

    @property
    def package_dir(self) -> Path:
        return self.path.parent


@dataclass(frozen=True)
class PackageStatus:
    id: str
    package_dir: Path
    active: bool
    status: str
    manifest: PluginManifest | None = None
    message: str | None = None


@dataclass(frozen=True)
class PluginState:
    project_root: Path
    plugin_root: Path
    packages_dir: Path
    packages_file: Path
    active_packages: tuple[ActivePackage, ...]
    statuses: tuple[PackageStatus, ...]


def normalize_project_root(project_root: Path | str | None = None) -> Path:
    if project_root is None:
        return Path.cwd()
    return Path(project_root)


def plugin_root(project_root: Path | str | None = None) -> Path:
    return normalize_project_root(project_root) / PLUGIN_ROOT_NAME


def packages_dir(project_root: Path | str | None = None) -> Path:
    return plugin_root(project_root) / PACKAGES_DIR_NAME


def packages_file(project_root: Path | str | None = None) -> Path:
    return plugin_root(project_root) / PACKAGES_FILE_NAME


def is_valid_package_id(package_id: str) -> bool:
    return bool(PACKAGE_ID_RE.fullmatch(package_id))


def read_yaml_file(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except OSError as exc:
        raise PluginSystemError(f"cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise PluginSystemError(f"invalid YAML in {path}: {exc}") from exc


def read_active_packages(project_root: Path | str | None = None) -> tuple[ActivePackage, ...]:
    path = packages_file(project_root)
    if not path.exists():
        return ()

    data = read_yaml_file(path)
    if data is None:
        return ()
    if not isinstance(data, dict):
        raise PluginSystemError(f"{path} must contain a YAML mapping")

    packages = data.get("packages", [])
    if packages is None:
        return ()
    if not isinstance(packages, list):
        raise PluginSystemError(f"{path}: packages must be a list")

    seen: set[str] = set()
    active: list[ActivePackage] = []
    for index, item in enumerate(packages):
        package = parse_active_package_item(path, index, item)
        if package.id in seen:
            raise PluginSystemError(f"{path}: duplicate package id: {package.id}")
        seen.add(package.id)
        active.append(package)
    return tuple(active)


def parse_active_package_item(path: Path, index: int, item: Any) -> ActivePackage:
    label = f"{path}: packages[{index}]"
    if not isinstance(item, str):
        raise PluginSystemError(f"{label} must be a package id string")

    package_id = item
    if not isinstance(package_id, str) or not package_id:
        raise PluginSystemError(f"{label}: id must be a non-empty string")
    if not is_valid_package_id(package_id):
        raise PluginSystemError(f"{label}: invalid package id: {package_id}")

    return ActivePackage(id=package_id)


def read_manifest(package_dir: Path) -> PluginManifest:
    manifest_path = package_dir / MANIFEST_FILE_NAME
    if not manifest_path.exists():
        raise PluginSystemError(f"missing manifest: {manifest_path}")

    data = read_yaml_file(manifest_path)
    if not isinstance(data, dict):
        raise PluginSystemError(f"{manifest_path} must contain a YAML mapping")

    manifest_id = data.get("id")
    if not isinstance(manifest_id, str) or not manifest_id:
        raise PluginSystemError(f"{manifest_path}: id must be a non-empty string")
    if not is_valid_package_id(manifest_id):
        raise PluginSystemError(f"{manifest_path}: invalid id: {manifest_id}")

    name = data.get("name")
    if name is not None and not isinstance(name, str):
        raise PluginSystemError(f"{manifest_path}: name must be a string")

    version = data.get("version")
    if version is not None and not isinstance(version, str):
        raise PluginSystemError(f"{manifest_path}: version must be a string")

    return PluginManifest(
        id=manifest_id,
        name=name,
        version=version,
        raw=data,
        path=manifest_path,
    )


def discover_state(project_root: Path | str | None = None) -> PluginState:
    root = normalize_project_root(project_root)
    active_packages = read_active_packages(root)
    active_by_id = {package.id: package for package in active_packages}
    installed_ids = discover_installed_package_ids(root)

    ordered_ids = list(active_by_id)
    ordered_ids.extend(package_id for package_id in installed_ids if package_id not in active_by_id)

    statuses = tuple(
        status_for_package(root, package_id, active_by_id.get(package_id))
        for package_id in ordered_ids
    )

    return PluginState(
        project_root=root,
        plugin_root=plugin_root(root),
        packages_dir=packages_dir(root),
        packages_file=packages_file(root),
        active_packages=active_packages,
        statuses=statuses,
    )


def discover_installed_package_ids(project_root: Path | str | None = None) -> tuple[str, ...]:
    root = packages_dir(project_root)
    if not root.is_dir():
        return ()

    package_ids: list[str] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_dir() and is_valid_package_id(child.name):
            package_ids.append(child.name)
    return tuple(package_ids)


def status_for_package(
    project_root: Path,
    package_id: str,
    active_package: ActivePackage | None,
) -> PackageStatus:
    package_dir = packages_dir(project_root) / package_id
    active = active_package is not None

    if not package_dir.exists():
        return PackageStatus(
            id=package_id,
            package_dir=package_dir,
            active=active,
            status="missing-package",
            message=f"package directory not found: {package_dir}",
        )
    if not package_dir.is_dir():
        return PackageStatus(
            id=package_id,
            package_dir=package_dir,
            active=active,
            status="invalid-package",
            message=f"package path is not a directory: {package_dir}",
        )

    try:
        manifest = read_manifest(package_dir)
    except PluginSystemError as exc:
        return PackageStatus(
            id=package_id,
            package_dir=package_dir,
            active=active,
            status="invalid-manifest",
            message=str(exc),
        )

    if manifest.id != package_id:
        return PackageStatus(
            id=package_id,
            package_dir=package_dir,
            active=active,
            status="manifest-id-mismatch",
            manifest=manifest,
            message=f"manifest id {manifest.id!r} does not match package id {package_id!r}",
        )

    return PackageStatus(
        id=package_id,
        package_dir=package_dir,
        active=active,
        status="ok",
        manifest=manifest,
    )


def resolve_package_dir(
    package_id_or_path: str,
    project_root: Path | str | None = None,
) -> Path:
    candidate = Path(package_id_or_path)
    if candidate.exists():
        if candidate.is_file() and candidate.name == MANIFEST_FILE_NAME:
            return candidate.parent
        if candidate.is_dir():
            return candidate
        raise PluginSystemError(f"not a package directory or {MANIFEST_FILE_NAME}: {candidate}")

    if not is_valid_package_id(package_id_or_path):
        raise PluginSystemError(f"invalid package id or path: {package_id_or_path}")
    return packages_dir(project_root) / package_id_or_path


def inspect_package(
    package_id_or_path: str,
    project_root: Path | str | None = None,
) -> PackageStatus:
    root = normalize_project_root(project_root)
    package_dir = resolve_package_dir(package_id_or_path, root)
    package_id = package_dir.name

    active_by_id = {package.id: package for package in read_active_packages(root)}
    active_package = active_by_id.get(package_id)
    status = status_for_package(root, package_id, active_package)

    if package_dir != packages_dir(root) / package_id:
        try:
            manifest = read_manifest(package_dir)
        except PluginSystemError as exc:
            return PackageStatus(
                id=package_id,
                package_dir=package_dir,
                active=False,
                status="invalid-manifest",
                message=str(exc),
            )
        return PackageStatus(
            id=manifest.id,
            package_dir=package_dir,
            active=manifest.id in active_by_id,
            status="ok",
            manifest=manifest,
        )

    return status


def count_quarto_global_keys(manifest: PluginManifest) -> int:
    quarto = manifest.raw.get("quarto")
    if not isinstance(quarto, dict):
        return 0
    global_config = quarto.get("global")
    if not isinstance(global_config, dict):
        return 0
    return len(global_config)


def count_quarto_metadata_languages(manifest: PluginManifest) -> int:
    quarto = manifest.raw.get("quarto")
    if not isinstance(quarto, dict):
        return 0
    metadata = quarto.get("metadata")
    if not isinstance(metadata, dict):
        return 0
    return len(metadata)


def count_deploy_files(manifest: PluginManifest) -> int:
    deploy = manifest.raw.get("deploy")
    if not isinstance(deploy, dict):
        return 0
    files = deploy.get("files")
    if not isinstance(files, list):
        return 0
    return len(files)
