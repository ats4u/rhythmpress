#!/bin/bash

. .venv/bin/activate
rm -rfv ./.site ./.quarto

# rhythmpedia render-sidebar
# quarto preview --log-level debug
quarto preview
# quarto preview --no-watch-inputs
