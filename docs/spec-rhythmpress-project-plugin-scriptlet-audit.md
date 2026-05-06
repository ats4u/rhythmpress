# Project Plugin And Scriptlet Audit Specification

Created: 20260506-133847
Updated: 20260507-062236

Status: draft audit specification.

## Purpose

Define how Rhythmpress should audit and eventually package reusable project scriptlets as project plugins.

The immediate goal is not implementation. The immediate goal is to inspect the existing `rhythmdo-com` CSS, JavaScript, filters, and support files, then decide which pieces belong in generic Rhythmpress project generation and which pieces remain site-specific.

## Problem Statement

`rhythmdo-com` contains many accumulated scriptlets:

- Pandoc Lua filters
- CSS files
- JavaScript modules
- LilyPond support files
- social-card configuration
- runtime language/404 helpers
- deployment/router support

These files solve real problems, but their dependencies are no longer obvious. Migrating all of them blindly would make a new project skeleton too heavy and too site-specific. Migrating none of them would lose important reusable behavior.

The audit must recover the dependency graph and classify each scriptlet from evidence.

## Plugin Concept

A Rhythmpress project plugin is a declarative bundle of source-level project behavior.

A plugin may provide:

- source files, such as `.quarto-filters/*.lua`, `.quarto-theme/**/*.scss`, `assets/*.mjs`, `assets/*.css`, or `.project-lilypond/*`;
- `_quarto.yml` patches;
- `_metadata-<lang>.yml` patches;
- `.gitignore` and `.quartoignore` patterns;
- external dependency notes;
- verification checks;
- generated-artifact exclusions.

A plugin must not be an arbitrary executable installer in the first design. It should be inspectable and deterministic.

## Classification Categories

Each scriptlet or support file must be classified as one of:

| Category | Meaning |
|---|---|
| Core generic | Required for the minimum healthy Rhythmpress project skeleton. |
| Optional generic plugin | Reusable across projects, but only when explicitly enabled or when a related feature is requested. |
| Site-specific | Belongs to `rhythmdo-com` branding/content/operations; do not migrate to generic project creation. |
| Obsolete or unused | No current dependency found; do not migrate unless a later dependency proves it is still needed. |
| Generated | Generated output; never migrate as canonical source. |

## Plugin Manifest Model

Candidate plugin manifest fields:

```yml
id: filter-lilypond
kind: pandoc-filter
default: false
description: Render LilyPond notation during Quarto render.

depends-on:
  - core

external-tools:
  - lilypond

source-files:
  - .quarto-filters/lilypond.lua
  - .project-lilypond/lilypond-preamble.ly

quarto-patch:
  format.html.filters:
    - .quarto-filters/lilypond.lua
  resources:
    - .project-lilypond/*.ly

metadata-patch: {}

gitignore:
  - /lilypond-out/

quartoignore: []

generated-exclusions:
  - lilypond-out/

verification:
  - file-exists: .quarto-filters/lilypond.lua
  - quarto-config-contains: format.html.filters
```

Manifest rules:

- `id` must be stable and safe for file names.
- `depends-on` must name other plugin IDs.
- `source-files` must be authored source, not generated files.
- `quarto-patch` must be deterministic and mergeable.
- External dependencies must be declared explicitly.
- Verification checks should be lightweight and deterministic.

## Initial Plugin Candidate IDs

Initial candidates to evaluate during the audit:

```text
core
runtime-language-switcher
runtime-404
filter-meta-dates
filter-remove-softbreaks
filter-include-files
filter-lilypond
filter-obsidian-image-dimensions
asset-toc-generator
asset-cookie-settings
asset-twitter-video
asset-groovespace
social-cards
cloudflare-router
github-actions
custom-assets
sidebar-hook
```

This list is provisional. The audit may merge, split, rename, or reject candidates.

## Audit Method

For each scriptlet or support file:

1. Find all references from `_quarto.yml`, metadata files, QMD files, masters, assets, docs, scripts, and generated outputs.
2. Identify direct runtime dependencies.
3. Identify generated outputs or cache directories.
4. Identify the problem the scriptlet solves.
5. Decide whether the behavior is generic or site-specific.
6. Assign a plugin candidate or reject migration.
7. Decide default status:
   - default-on core;
   - default-on only when another feature implies it;
   - opt-in;
   - do not migrate.
8. Record verification checks.

## Dependency Table Schema

The audit output should use this table shape:

| File | Referenced from | Requires | Produces or mutates | Solves | Generic? | Plugin candidate | Default? | Migrate? | Reason |
|---|---|---|---|---|---|---|---|---|---|

Column definitions:

- `File`: scriptlet or support file being classified.
- `Referenced from`: source files or config entries that load it.
- `Requires`: runtime tools, browser APIs, CSS classes, DOM structure, environment variables, other files, or Quarto features.
- `Produces or mutates`: generated outputs, DOM changes, rendered metadata, screenshots, cache outputs, or side effects.
- `Solves`: practical problem addressed.
- `Generic?`: yes, no, or mixed.
- `Plugin candidate`: proposed plugin ID.
- `Default?`: core, auto, opt-in, or no.
- `Migrate?`: yes, no, later, or unknown.
- `Reason`: evidence-based explanation.

## Read-Only Audit Scope

Initial audit should inspect:

```text
~/rhythmdo-com/_quarto.yml
~/rhythmdo-com/_metadata-*.yml
~/rhythmdo-com/.quarto-filters/
~/rhythmdo-com/assets/
~/rhythmdo-com/.quarto-theme/
~/rhythmdo-com/.project-lilypond/
~/rhythmdo-com/.project-lib/
~/rhythmdo-com/.project-templates/
~/rhythmdo-com/**/*.qmd
~/rhythmdo-com/**/master-*.md
~/rhythmdo-com/**/master-*.qmd
~/rhythmpress/src/rhythmpress/scripts/
~/rhythmpress/docs/
~/rhythmpress/examples/
```

Generated output directories should be searched only to identify generated artifacts and runtime effects, not to derive canonical source.

## Non-Goals

This audit does not:

- implement plugin commands;
- move files;
- delete files;
- refactor CSS, JavaScript, or filters;
- decide final UI/theme design;
- make optional packs default-on without evidence.

## Expected Output

The next pass should produce:

- a scriptlet inventory;
- a dependency table;
- plugin candidate list with default status;
- migration recommendations;
- unresolved questions for scriptlets whose dependencies cannot be proven from static inspection.
