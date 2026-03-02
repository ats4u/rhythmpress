#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob
profiles=( _quarto-*.yml )
shopt -u nullglob

if [ "${#profiles[@]}" -eq 0 ]; then
  echo "[render-all] no _quarto-*.yml files found in $(pwd)" >&2
  exit 1
fi

for f in "${profiles[@]}"; do
  p="${f#_quarto-}"
  p="${p%.yml}"
  echo "[render-all] profile=$p file=$f"
  rhythmpress render --profile "$p" "$@"
done
