#!/usr/bin/env bash
set -euo pipefail

# Allow override: first arg = path to _sidebar.conf, default to local file
CONF="${1:-_sidebar.conf}"


# <<< ADDED Wed, 20 Aug 2025 06:18:07 +0900
# Allow override: first arg = path to _sidebar.conf, default to local file
CONF="${1:-_sidebar.conf}"

# Extract filename part only (strip directory)
BASE="$(basename "$CONF")"

# Default
LANG_ID=ja

# If it matches the pattern _sidebar.<langid>.conf → extract it
if [[ "$BASE" =~ ^_sidebar\.([^.]+)\.conf$ ]]; then
    LANG_ID="${BASH_REMATCH[1]}"
fi
# >>> ADDED Wed, 20 Aug 2025 06:18:07 +0900


# Resolve repo root from this script’s location: .../bin -> repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# # 1) Merge YAMLs listed in _sidebar.conf
# #    (expects one path per line; adjust if your list uses a different delimiter)
# xargs <"$CONF" yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar-$LANG_ID.generated.yml

# collect file list (strip inline/full-line # comments, drop blanks)
FILES="$(sed 's/#.*//' "$CONF" | grep -v '^[[:space:]]*$' || true)"

# 1) Merge YAMLs (empty -> {})
if [ -n "$FILES" ]; then
  printf '%s\n' "$FILES" | xargs yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar-$LANG_ID.generated.yml
else
  echo '{}' > _sidebar-$LANG_ID.generated.yml
fi

# 2) Write header with proper newlines (printf is more portable than echo -e)
printf '**目次**\n\n' > _sidebar-$LANG_ID.generated.md

# 3) Append generated TOC
"$REPO_ROOT/bin/rhythmpedia-render-toc.py" "$CONF" >> _sidebar-$LANG_ID.generated.md

