#!/usr/bin/env bash
set -euo pipefail

# Remove Quarto preview/build state, including language-specific output dirs.
# Examples: .site, .site-ja, .site-en
shopt -s nullglob
site_dirs=(./.site ./.site-*)
rm -rfv "${site_dirs[@]}" ./.quarto

exec rhythmpress start "$@"
