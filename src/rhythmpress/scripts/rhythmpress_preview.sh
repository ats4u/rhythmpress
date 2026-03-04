#!/usr/bin/env bash
set -euo pipefail

allow_empty=0
pass_args=()

for arg in "$@"; do
  case "$arg" in
    --allow-empty-preview|--no-warn)
      allow_empty=1
      ;;
    *)
      pass_args+=("$arg")
      ;;
  esac
done

if [ "${#pass_args[@]}" -eq 0 ] && [ "$allow_empty" -ne 1 ]; then
  echo "[preview] refusing to run without options." >&2
  echo "[preview] use: rhythmpress preview --profile <id>" >&2
  echo "[preview] or use: rhythmpress preview-all" >&2
  echo "[preview] override: rhythmpress preview --allow-empty-preview" >&2
  exit 2
fi

cmd=(quarto preview)
if [ "${#pass_args[@]}" -gt 0 ]; then
  cmd+=("${pass_args[@]}")
fi
env_cmd=(RHYTHMPRESS_PREVIEW=1 QUARTO_PROJECT_DIR="$(pwd)")
printf '[preview] exec:'
for arg in "${env_cmd[@]}"; do
  printf ' %q' "$arg"
done
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

env "${env_cmd[@]}" "${cmd[@]}"
