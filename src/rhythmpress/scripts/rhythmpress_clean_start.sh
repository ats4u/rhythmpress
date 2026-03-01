#!/bin/bash

. .venv/bin/activate

# Remove Quarto preview/build state, including language-specific output dirs.
# Examples: .site, .site-ja, .site-en
shopt -s nullglob
site_dirs=(./.site ./.site-*)
rm -rfv "${site_dirs[@]}" ./.quarto

# rhythmpedia render-sidebar
# quarto preview --log-level debug
QUARTO_PROJECT_DIR="$(pwd)" quarto preview "$@"
# quarto preview --no-watch-inputs
