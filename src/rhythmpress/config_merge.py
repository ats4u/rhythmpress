from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any


def recursive_merge(base: Any, override: Any) -> Any:
    """
    Recursively merge two config values.

    Policy:
    - mappings recurse key-by-key
    - lists concatenate in order
    - all other values are replaced by override
    """
    if isinstance(base, Mapping) and isinstance(override, Mapping):
        out = {k: deepcopy(v) for k, v in base.items()}
        for key, value in override.items():
            if key in out:
                out[key] = recursive_merge(out[key], value)
            else:
                out[key] = deepcopy(value)
        return out

    if isinstance(base, list) and isinstance(override, list):
        return deepcopy(base) + deepcopy(override)

    return deepcopy(override)
