#!/usr/bin/env bash
set -euo pipefail

cmd=(quarto preview "$@")
printf '[preview] exec: QUARTO_PROJECT_DIR=%q' "$(pwd)"
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

QUARTO_PROJECT_DIR="$(pwd)" "${cmd[@]}"
