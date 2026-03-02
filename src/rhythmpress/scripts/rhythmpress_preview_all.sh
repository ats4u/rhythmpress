#!/usr/bin/env bash
set -euo pipefail

seen_output_dir=0
seen_no_render=0

args=( "$@" )
i=0
while [ "$i" -lt "${#args[@]}" ]; do
  arg="${args[$i]}"
  case "$arg" in
    --output-dir)
      seen_output_dir=1
      i=$((i + 1))
      ;;
    --output-dir=*)
      seen_output_dir=1
      ;;
    --no-render)
      seen_no_render=1
      ;;
  esac
  i=$((i + 1))
done

cmd=(quarto preview)
if [ "$seen_output_dir" -eq 0 ]; then
  cmd+=(--output-dir .site-merged)
fi
if [ "$seen_no_render" -eq 0 ]; then
  cmd+=(--no-render)
fi
cmd+=("$@")

if [ "$seen_output_dir" -eq 0 ] && [ ! -d ".site-merged" ]; then
  echo "[preview-all] .site-merged not found." >&2
  echo "[preview-all] run: rhythmpress assemble" >&2
  exit 1
fi

printf '[preview-all] exec: QUARTO_PROJECT_DIR=%q' "$(pwd)"
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

QUARTO_PROJECT_DIR="$(pwd)" "${cmd[@]}"
