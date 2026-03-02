#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "[render] no arguments supplied. Refusing to run bare 'quarto render'." >&2
  echo "[render] use: rhythmpress render --profile <id>  (or --config <file>)" >&2
  echo "[render] hint: rhythmpress render-all" >&2
  exit 2
fi

cmd=(quarto render "$@")
printf '[render] exec: QUARTO_PROJECT_DIR=%q' "$(pwd)"
for a in "${cmd[@]}"; do printf ' %q' "$a"; done
printf '\n'

QUARTO_PROJECT_DIR="$(pwd)" "${cmd[@]}"
