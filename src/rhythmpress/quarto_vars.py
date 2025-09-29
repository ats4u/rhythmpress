# rhythmpress/vars.py
# Minimal variables loader with Quarto-like conventions + interpolation.
from __future__ import annotations
import os
import re
import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Iterable, Mapping, Tuple

try:
    import yaml  # PyYAML (preferred if present)
except Exception:
    yaml = None  # Fallback to JSON only if PyYAML isn’t available


# ------------------------- public API ----------------------------------------
# --- replace the old get_variables + add an internal cached loader -----------

from functools import lru_cache

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

    merged = dict(base_vars)
    if extra:
        _deep_merge(merged, dict(extra))

    # ctx must reflect the final merged map for ${var} lookups
    ctx = dict(base_ctx)
    ctx.update(merged)
    return _resolve_all(merged, ctx)

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
    root, start = _detect_project_root(cwd_str, project_root_markers)

    sources: list[Mapping[str, Any]] = []
    q = _read_quarto_vars(root)
    if q:
        sources.append(q)

    for name in ("_variables.yml", "_variables.yaml", "_variables.json"):
        p = (root / name)
        if p.is_file():
            sources.append(_read_any(p))
            break

    if lang:
        for name in (f"_variables-{lang}.yml", f"_variables-{lang}.yaml", f"_variables-{lang}.json"):
            p = (root / name)
            if p.is_file():
                sources.append(_read_any(p))
                break

    if allow_env:
        env_map = {
            k[len("RHYTHMPRESS_"):].lower(): v
            for k, v in os.environ.items()
            if k.startswith("RHYTHMPRESS_")
        }
        if env_map:
            sources.append(env_map)

    merged: Dict[str, Any] = {}
    for s in sources:
        _deep_merge(merged, s)

    ctx_basics: Dict[str, Any] = {
        "cwd": str(start),
        "project_root": str(root),
    }
    if allow_env:
        ctx_basics["env"] = _EnvProxy()

    return merged, ctx_basics


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


def _read_quarto_vars(root: Path) -> Dict[str, Any]:
    for name in ("_quarto.yml", "_quarto.yaml"):
        p = root / name
        if p.is_file():
            data = _read_any(p)
            # Quarto-like spots to pull variables from:
            # - top-level 'variables'
            # - top-level 'metadata'
            # Both may be dicts; later fields override earlier ones.
            out: Dict[str, Any] = {}
            if isinstance(data, dict):
                if isinstance(data.get("variables"), dict):
                    _deep_merge(out, data["variables"])
                if isinstance(data.get("metadata"), dict):
                    _deep_merge(out, data["metadata"])
            return out
    return {}


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


def _deep_merge(dst: Dict[str, Any], src: Mapping[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, Mapping) and isinstance(dst.get(k), Mapping):
            _deep_merge(dst[k], v)  # type: ignore[index]
        else:
            dst[k] = v


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

