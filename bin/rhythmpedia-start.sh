#!/bin/bash

. .venv/bin/activate
rhythmpedia render-sidebar
quarto preview
