#!/usr/bin/env bash
set -euo pipefail

# rhythmpress_render_sidebar.sh
# Generate sidebar YAML + Markdown TOC from a _sidebar.conf

# --- Require RHYTHMPRESS_ROOT -------------------------------------------------
if [ -z "${RHYTHMPRESS_ROOT:-}" ]; then
  printf '%s\n' \
    "RHYTHMPRESS_ROOT is not set." \
    "Please activate the project, e.g.:" \
    "  eval \"\$(rhythmpress env)\"" \
    "" >&2
  exit 1
fi

# --- Locate the conf file ----------------------------------------------------
RAW_CONF="${1:-_sidebar.conf}"
case "$RAW_CONF" in
  /*) CONF_ABS="$RAW_CONF" ;;
  *)  CONF_ABS="$RHYTHMPRESS_ROOT/$RAW_CONF" ;;
esac

if [ ! -f "$CONF_ABS" ]; then
  printf 'Not found: %s\n' "$CONF_ABS" >&2
  exit 1
fi

# Work in the directory that contains the conf (so relative YAMLs inside it work)
CONF_DIR="$(cd "$(dirname "$CONF_ABS")" && pwd)"
cd "$CONF_DIR"

BASE="$(basename "$CONF_ABS")"

# --- Language id -------------------------------------------------------------
LANG_ID=ja
if [[ "$BASE" =~ ^_sidebar\.([^.]+)\.conf$ ]]; then
  LANG_ID="${BASH_REMATCH[1]}"
fi

# --- Collect YAML file list --------------------------------------------------
FILES="$(sed 's/#.*//' "$BASE" | grep -v '^[[:space:]]*$' || true)"

# --- Merge YAMLs -------------------------------------------------------------
if [ -n "$FILES" ]; then
  printf '%s\n' "$FILES" \
    | xargs yq ea '. as $i ireduce ({}; . *+ $i)' \
    > "_sidebar-$LANG_ID.generated.yml"
else
  echo '{}' > "_sidebar-$LANG_ID.generated.yml"
fi

# --- Markdown header ---------------------------------------------------------
printf '**目次**\n\n' > "_sidebar-$LANG_ID.generated.md"

# --- Append generated TOC ----------------------------------------------------
rhythmpress render_toc "$BASE" >> "_sidebar-$LANG_ID.generated.md"

