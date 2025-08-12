# -----------------------------------------------
# Rhythmpedia / Quarto Makefile (dispatcher-only)
# -----------------------------------------------
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ---- Tools ----
BIN_RHYTHM := bin/rhythmpedia
Q := quarto
# human-maintained mapping
CONFIG := rhythmpedia.dirs

# ---- Read mapping (portable awk) ----
# Format accepted (ignore blank lines & # comments):
#   split: beat-orientation
#   copy-lang: tatenori-theory
# Also accepts whitespace instead of colon:  split   beat-orientation
SPLIT_DIRS := $(shell \
  [ -f "$(CONFIG)" ] && awk -F'[: \t]+' 'BEGIN{IGNORECASE=1} \
    /^[[:space:]]*$$/||/^[[:space:]]*\#/ {next} \
    $$1=="split" {print $$2}' "$(CONFIG)" | sort -u )

COPY_DIRS := $(shell \
  [ -f "$(CONFIG)" ] && awk -F'[: \t]+' 'BEGIN{IGNORECASE=1} \
    /^[[:space:]]*$$/||/^[[:space:]]*\#/ {next} \
    ($$1=="copy-lang" || $$1=="copy") {print $$2}' "$(CONFIG)" | sort -u )

# ---- Phony ----
.PHONY: help plan sidebar toc split copy prep build render preview clean veryclean check

help:
	@echo ""
	@echo "Targets:"
	@echo "  make plan     # show what will run based on $(CONFIG)"
	@echo "  make split    # run 'rhythmpedia split' for mapped dirs"
	@echo "  make copy     # run 'rhythmpedia copy-lang' for mapped dirs"
	@echo "  make prep     # sidebar + toc"
	@echo "  make build    # prep + split + copy + quarto render"
	@echo "  make preview  # quarto preview (or your wrapper)"
	@echo "  make check    # sanity: ensure dirs exist and no overlaps"
	@echo "  make clean    # remove Quarto outputs"
	@echo ""
	@echo "Dry run: DRYRUN=1 make build"
	@echo "Mapping file: $(CONFIG)"

plan:
	@echo "==> Plan from $(CONFIG)"
	@if [ ! -f "$(CONFIG)" ]; then echo "  (no $(CONFIG) file)"; exit 0; fi
	@echo "  split:"
	@for d in $(SPLIT_DIRS); do echo "    - $$d"; done || true
	@echo "  copy-lang:"
	@for d in $(COPY_DIRS); do echo "    - $$d"; done || true

check:
	@echo "==> Checking mapping"
	@if [ ! -f "$(CONFIG)" ]; then echo "ERROR: $(CONFIG) not found"; exit 1; fi
	# overlap check
	@overlap=$$(comm -12 <(printf "%s\n" $(SPLIT_DIRS) | sort -u) <(printf "%s\n" $(COPY_DIRS) | sort -u) || true); \
	if [ -n "$$overlap" ]; then \
	  echo "ERROR: A directory is listed for BOTH split and copy-lang:"; \
	  echo "$$overlap"; exit 2; \
	fi
	# existence check
	@missing=0; \
	for d in $(SPLIT_DIRS) $(COPY_DIRS); do \
	  if [ ! -d "$$d" ]; then echo "ERROR: directory not found: $$d"; missing=1; fi; \
	done; \
	exit $$missing

sidebar:
	@echo "==> Generating sidebar"
	$(if $(DRYRUN),echo ,) $(BIN_RHYTHM) render-sidebar

toc:
	@echo "==> Generating TOC"
	$(if $(DRYRUN),echo ,) $(BIN_RHYTHM) render-toc

prep: sidebar toc

split: check
	@echo "==> Splitting (dispatcher: $(BIN_RHYTHM))"
	@if [ -z "$(SPLIT_DIRS)" ]; then echo "(no split targets)"; exit 0; fi
	@for d in $(SPLIT_DIRS); do \
	  echo "→ split $$d"; \
	  $(if $(DRYRUN),echo ,) $(BIN_RHYTHM) split "$$d"; \
	done

copy: check
	@echo "==> Copying language indexes (dispatcher: $(BIN_RHYTHM))"
	@if [ -z "$(COPY_DIRS)" ]; then echo "(no copy targets)"; exit 0; fi
	@for d in $(COPY_DIRS); do \
	  echo "→ copy-lang $$d"; \
	  $(if $(DRYRUN),echo ,) $(BIN_RHYTHM) copy-lang "$$d"; \
	done

render:
	@echo "==> Quarto render"
	$(if $(DRYRUN),echo ,) $(Q) render

preview:
	@echo "==> Quarto preview"
	@if [ -x bin/rhythmpedia-start.sh ]; then \
	  $(if $(DRYRUN),echo ,) bin/rhythmpedia-start.sh; \
	else \
	  $(if $(DRYRUN),echo ,) $(Q) preview --no-browser; \
	fi

build: prep split copy render

clean:
	@echo "==> Cleaning"
	@rm -rf .site _site

veryclean: clean
	@rm -rf .quarto .qmd-cache .cache || true

