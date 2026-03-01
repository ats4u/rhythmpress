#!/bin/bash

. .venv/bin/activate

# Remove Quarto preview/build state, including language-specific output dirs.
# Examples: .site, .site-ja, .site-en
shopt -s nullglob
site_dirs=(./.site ./.site-*)
rm -rfv "${site_dirs[@]}" ./.quarto

# rhythmpedia render-sidebar
# quarto preview --log-level debug
cmd=(quarto preview "$@")
printf '[clean-start] exec: QUARTO_PROJECT_DIR=%q' "$(pwd)"
for arg in "${cmd[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'
QUARTO_PROJECT_DIR="$(pwd)" "${cmd[@]}"
# quarto preview --no-watch-inputs
