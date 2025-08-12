#!/usr/bin/env bash
set -euo pipefail

# Allow override: first arg = path to _sidebar.conf, default to local file
CONF="${1:-_sidebar.conf}"

# Resolve repo root from this script’s location: .../bin -> repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 1) Merge YAMLs listed in _sidebar.conf
#    (expects one path per line; adjust if your list uses a different delimiter)
xargs <"$CONF" yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar.generated.yml

# 2) Write header with proper newlines (printf is more portable than echo -e)
printf '**目次**\n\n' > _sidebar.generated.md

# 3) Append generated TOC
"$REPO_ROOT/bin/rhythmpedia-render-toc.py" "$CONF" >> _sidebar.generated.md

