#!/bin/bash

. .venv/bin/activate
bin/render-sidebar.sh
quarto preview
