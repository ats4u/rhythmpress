#!/usr/bin/env bash
set -euo pipefail

preview_dir=""
port="5150"
pass_args=()

args=( "$@" )
i=0
while [ "$i" -lt "${#args[@]}" ]; do
  arg="${args[$i]}"
  case "$arg" in
    --output-dir)
      if [ $((i + 1)) -ge "${#args[@]}" ]; then
        echo "[preview-all] --output-dir requires a value" >&2
        exit 2
      fi
      preview_dir="${args[$((i + 1))]}"
      i=$((i + 1))
      ;;
    --output-dir=*)
      preview_dir="${arg#--output-dir=}"
      ;;
    --port)
      if [ $((i + 1)) -ge "${#args[@]}" ]; then
        echo "[preview-all] --port requires a value" >&2
        exit 2
      fi
      port="${args[$((i + 1))]}"
      i=$((i + 1))
      ;;
    --port=*)
      port="${arg#--port=}"
      ;;
    *)
      pass_args+=("$arg")
      ;;
  esac
  i=$((i + 1))
done

if [ -z "$preview_dir" ]; then
  preview_dir=".site"
fi

cmd=(python3 -m http.server "$port" --directory "$preview_dir")
if [ "${#pass_args[@]}" -gt 0 ]; then
  cmd+=("${pass_args[@]}")
fi

if [ ! -d "$preview_dir" ]; then
  echo "[preview-all] $preview_dir not found." >&2
  echo "[preview-all] run: rhythmpress assemble" >&2
  exit 1
fi

printf '[preview-all] exec:'
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

"${cmd[@]}"
