#!/bin/bash

. .venv/bin/activate
# rm -rfv ./.site ./.quarto

# rhythmpedia render-sidebar
# quarto preview --log-level debug
cmd=(quarto preview "$@")
printf '[start] exec: QUARTO_PROJECT_DIR=%q' "$(pwd)"
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'
QUARTO_PROJECT_DIR="$(pwd)" "${cmd[@]}"
# quarto preview --no-watch-inputs
