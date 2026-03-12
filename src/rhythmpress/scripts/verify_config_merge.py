#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

from rhythmpress.config_merge import recursive_merge


def main() -> int:
    base = {
        "project": {
            "render": ["base-a", "base-b"],
            "flags": {"draft": False},
        },
        "format": {
            "html": {
                "filters": ["base-filter"],
            }
        },
        "title": "base",
    }
    override = {
        "project": {
            "render": ["override-a"],
            "flags": {"execute": True},
        },
        "format": {
            "html": {
                "filters": ["override-filter"],
            }
        },
        "title": "override",
    }

    base_before = deepcopy(base)
    override_before = deepcopy(override)
    merged = recursive_merge(base, override)

    expected = {
        "project": {
            "render": ["base-a", "base-b", "override-a"],
            "flags": {"draft": False, "execute": True},
        },
        "format": {
            "html": {
                "filters": ["base-filter", "override-filter"],
            }
        },
        "title": "override",
    }

    if merged != expected:
        raise AssertionError(f"unexpected merged config: {merged!r}")
    if base != base_before:
        raise AssertionError("base config mutated")
    if override != override_before:
        raise AssertionError("override config mutated")

    print("OK: recursive_merge merges mappings, concatenates lists, and preserves inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
