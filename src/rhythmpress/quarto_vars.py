# rhythmpress/vars.py
# Minimal variables loader with Quarto-like conventions + interpolation.
from __future__ import annotations
import os
import re
import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Iterable, Mapping, Tuple
from rhythmpress.config_merge import recursive_merge

try:
    import yaml  # PyYAML (preferred if present)
except Exception:
    yaml = None  # Fallback to JSON only if PyYAML isn’t available


# ------------------------- public API ----------------------------------------
# --- replace the old get_variables + add an internal cached loader -----------

def get_variables(
    cwd: str | os.PathLike[str] | None = None,
    *,
    lang: str | None = None,
    extra: Mapping[str, Any] | None = None,
    allow_env: bool = True,
    project_root_markers: Tuple[str, ...] = ("_quarto.yml", "_quarto.yaml"),
) -> Dict[str, Any]:
    """
    Public API: Same behavior as before, but 'extra' no longer breaks caching.
    """
    cwd_str = str(Path(cwd or os.getcwd()).resolve())
    base_vars, base_ctx = _load_base_variables(
        cwd_str, lang, allow_env, project_root_markers
    )

    merged = recursive_merge(base_vars, dict(extra) if extra else {})

    # ctx must reflect the final merged map for ${var} lookups
    ctx = dict(base_ctx)
    ctx.update(merged)
    return _resolve_all(merged, ctx)


def get_title_shortcode_contexts(
    cwd: str | os.PathLike[str] | None = None,
    *,
    lang: str | None = None,
    allow_env: bool = True,
    project_root_markers: Tuple[str, ...] = ("_quarto.yml", "_quarto.yaml"),
) -> Dict[str, Dict[str, Any]]:
    """
    Load separate contexts for title shortcodes.

    `var` stays on the legacy variable path (`variables` + `_variables*` + env),
    while `meta` resolves from Quarto metadata (`metadata` + `_metadata-<lang>.yml`).
    """
    cwd_str = str(Path(cwd or os.getcwd()).resolve())
    source_groups, base_ctx = _load_source_groups(
        cwd_str, lang, allow_env, project_root_markers
    )

    raw_contexts = {
        "var": _merge_sources(
            source_groups["quarto_variables"],
            source_groups["legacy_variables"],
            source_groups["lang_variables"],
            source_groups["env"],
        ),
        "meta": _merge_sources(
            source_groups["quarto_metadata"],
            source_groups["lang_metadata"],
        ),
    }

    resolved: Dict[str, Dict[str, Any]] = {}
    for name, raw in raw_contexts.items():
        ctx = dict(base_ctx)
        ctx.update(raw)
        resolved[name] = _resolve_all(raw, ctx)
    return resolved


def interpolate_title_shortcodes(
    text: Any,
    *,
    contexts: Mapping[str, Mapping[str, Any]],
) -> Any:
    """
    Replace `{{< var ... >}}` and `{{< meta ... >}}` in title-like strings.
    """
    if not isinstance(text, str):
        return text

    def repl(m: re.Match[str]) -> str:
        scope = m.group(1)
        key = m.group(2)
        if scope == "var" and key.startswith("env:"):
            return os.environ.get(key[4:], "")
        ctx = contexts.get(scope)
        if not isinstance(ctx, Mapping):
            return ""
        val = _get_dotted(ctx, key)
        return "" if val is None else str(val)

    return _TITLE_SHORTCODE_PATTERN.sub(repl, text)


@lru_cache(maxsize=64)
def _load_base_variables(
    cwd_str: str,
    lang: str | None,
    allow_env: bool,
    project_root_markers: Tuple[str, ...],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load everything *except* 'extra', and return (merged, ctx_basics).
    Cached: all args are hashable (strings/tuples/bools).
    """
    source_groups, ctx_basics = _load_source_groups(
        cwd_str, lang, allow_env, project_root_markers
    )
    merged = _merge_sources(
        source_groups["quarto_variables"],
        source_groups["quarto_metadata"],
        source_groups["legacy_variables"],
        source_groups["lang_variables"],
        source_groups["env"],
    )
    return merged, ctx_basics


@lru_cache(maxsize=64)
def _load_source_groups(
    cwd_str: str,
    lang: str | None,
    allow_env: bool,
    project_root_markers: Tuple[str, ...],
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    root, start = _detect_project_root(cwd_str, project_root_markers)
    quarto_variables, quarto_metadata = _read_quarto_blocks(root)

    source_groups = {
        "quarto_variables": quarto_variables,
        "quarto_metadata": quarto_metadata,
        "legacy_variables": _read_first_existing(
            root,
            ("_variables.yml", "_variables.yaml", "_variables.json"),
        ),
        "lang_variables": _read_first_existing(
            root,
            (
                f"_variables-{lang}.yml",
                f"_variables-{lang}.yaml",
                f"_variables-{lang}.json",
            ),
        ) if lang else {},
        "lang_metadata": _read_first_existing(
            root,
            (
                f"_metadata-{lang}.yml",
                f"_metadata-{lang}.yaml",
            ),
        ) if lang else {},
        "env": _env_map() if allow_env else {},
    }

    ctx_basics: Dict[str, Any] = {
        "cwd": str(start),
        "project_root": str(root),
    }
    if allow_env:
        ctx_basics["env"] = _EnvProxy()

    return source_groups, ctx_basics


# ------------------------- helpers ------------------------------------------

def _detect_project_root(cwd: str | os.PathLike[str] | None,
                         markers: Tuple[str, ...]) -> Tuple[Path, Path]:
    start = Path(cwd or os.getcwd()).resolve()
    cur = start
    while True:
        if any((cur / m).is_file() for m in markers):
            return cur, start
        if cur.parent == cur:
            # fall back to start dir if marker not found
            return start, start
        cur = cur.parent


def _read_quarto_blocks(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    for name in ("_quarto.yml", "_quarto.yaml"):
        p = root / name
        if p.is_file():
            data = _read_any(p)
            variables: Dict[str, Any] = {}
            metadata: Dict[str, Any] = {}
            if isinstance(data, dict):
                if isinstance(data.get("variables"), dict):
                    variables = recursive_merge(variables, data["variables"])
                if isinstance(data.get("metadata"), dict):
                    metadata = recursive_merge(metadata, data["metadata"])
            return variables, metadata
    return {}, {}


def _read_first_existing(root: Path, names: Iterable[str]) -> Dict[str, Any]:
    for name in names:
        p = root / name
        if p.is_file():
            return _read_any(p)
    return {}


def _env_map() -> Dict[str, Any]:
    return {
        k[len("RHYTHMPRESS_"):].lower(): v
        for k, v in os.environ.items()
        if k.startswith("RHYTHMPRESS_")
    }


def _merge_sources(*sources: Mapping[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for source in sources:
        if source:
            merged = recursive_merge(merged, source)
    return merged


def _read_any(path: Path) -> Dict[str, Any]:
    if path.suffix.lower() in (".yml", ".yaml"):
        if yaml is None:
            raise RuntimeError(f"PyYAML not installed but YAML file requested: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    elif path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported file type: {path}")
    return data if isinstance(data, dict) else {}

_TITLE_SHORTCODE_PATTERN = re.compile(
    r"\{\{<\s*(var|meta)\s+([A-Za-z0-9_.:-]+)\s*>\}\}"
)

_VAR_PATTERN = re.compile(r"""
    \$\{
        \s*(
            env:[A-Za-z_][A-Za-z0-9_]* |     # ${env:NAME}
            [A-Za-z_][A-Za-z0-9_.-]*   |     # ${var} (dot-path allowed)
            cwd | project_root
        )\s*
    \}
""", re.VERBOSE)


def _resolve_all(obj: Any, ctx: Mapping[str, Any], depth: int = 0) -> Any:
    if depth > 20:
        return obj  # safety
    if isinstance(obj, str):
        return _resolve_str(obj, ctx, depth)
    if isinstance(obj, list):
        return [_resolve_all(x, ctx, depth) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = _resolve_all(v, ctx, depth)
        return out
    return obj


def _resolve_str(s: str, ctx: Mapping[str, Any], depth: int) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1).strip()
        if key == "cwd":
            return str(ctx.get("cwd", ""))
        if key == "project_root":
            return str(ctx.get("project_root", ""))
        if key.startswith("env:"):
            env_name = key.split(":", 1)[1]
            env = ctx.get("env")
            return "" if env is None else str(env.get(env_name, ""))
        # dotted lookup in ctx (merged variables)
        val = _get_dotted(ctx, key)
        if val is None:
            return ""
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)

    # iterate until stable or depth limit
    last = s
    for _ in range(6):
        cur = _VAR_PATTERN.sub(repl, last)
        if cur == last:
            break
        last = cur
    return last


def _get_dotted(ctx: Mapping[str, Any], dotted: str) -> Any:
    cur: Any = ctx
    for part in dotted.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            return None
        cur = cur[part]
    return cur


class _EnvProxy(dict):
    def __getitem__(self, k: str) -> str:
        return os.environ.get(k, "")
    def get(self, k: str, default: str = "") -> str:
        return os.environ.get(k, default)
