#!/usr/bin/env bash
set -euo pipefail

#!/usr/bin/env bash
# rhythmpress_render_sidebar.sh
# Generate sidebar YAML + Markdown TOC from a _sidebar.conf
#
# Summary:
#   Generates a merged sidebar YAML and a Markdown TOC for a Quarto project.
#   After writing the YAML, it optionally runs a per-language Python hook.
#
# Usage:
#   ./rhythmpress_render_sidebar.sh [path/to/_sidebar-<lang>.conf]
#   - If no path is given, uses "$RHYTHMPRESS_ROOT/_sidebar.conf".
#
# Behavior:
#   1) Infers <lang> from the conf name (_sidebar-<lang>.conf), default "ja".
#   2) Reads the conf file (one YAML path per line, # for comments).
#   3) Merges all listed YAMLs with `yq ea` (deep merge, last-wins).
#      → writes: _sidebar-<lang>.generated.yml
#   4) (Hook) If present, runs:
#        _rhythmpress.hook-after._sidebar-<lang>.generated.py  <generated-yml>
#      Failures are ignored (non-fatal); runs in the conf’s directory.
#   5) Writes Markdown TOC header and appends:
#        rhythmpress render_toc <conf-basename>
#      → writes: _sidebar-<lang>.generated.md
#
# Requirements:
#   - Environment: RHYTHMPRESS_ROOT must be set (e.g., eval "$(rhythmpress env)").
#   - Tools: yq v4 (Mike Farah), python3.
#
# Outputs (example for "ja"):
#   - _sidebar-ja.generated.yml
#   - _sidebar-ja.generated.md

command -v yq >/dev/null || { echo "yq not found"; exit 127; }

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
if [[ "$BASE" =~ ^_sidebar-([^.]+)\. ]]; then
  LANG_ID="${BASH_REMATCH[1]}"
fi

# --- Collect YAML file list --------------------------------------------------
FILES="$(sed 's/#.*//' "$BASE" | grep -v '^[[:space:]]*$' || true)"

# --- Merge YAMLs -------------------------------------------------------------
YAML_FILE="_sidebar-$LANG_ID.generated.yml"
if [ -n "$FILES" ]; then
  printf '%s\n' "$FILES" \
    | xargs yq ea '. as $i ireduce ({}; . *+ $i)' \
    > "$YAML_FILE"
else
  echo '{}' > "$YAML_FILE"
fi


# --- Optional post-merge hook -----------------------------------------------
HOOK_FILE="_rhythmpress.hook-after.$YAML_FILE.py"
if [ -f "$HOOK_FILE" ]; then
  echo "A hook file found : $HOOK_FILE"
  python3 "$HOOK_FILE" "$YAML_FILE" "$LANG_ID" "$BASE" || true
fi

printf "LANGID=$LANG_ID BASE=$BASE\n"

# --- Markdown header ---------------------------------------------------------
printf '**目次**\n\n' > "_sidebar-$LANG_ID.generated.md"

# --- Append generated TOC ----------------------------------------------------
rhythmpress render_toc "$BASE" >> "_sidebar-$LANG_ID.generated.md"

