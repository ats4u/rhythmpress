# Rhythmpress Project Plugin Feature Packs

Created: 20260506-142202

Status: draft design specification.

## Purpose

Define how `rhythmpress project create` should represent optional scriptlets, filters, assets, CSS, and deployment support as deterministic feature packs.

This document consumes the evidence in [Scriptlet Dependency Map](spec-rhythmpress-project-scriptlet-dependency-map.md).

Feature packs should be implemented as plugin packages. The package artifact and lifecycle are specified in [Plugin Package Format](spec-rhythmpress-project-plugin-package-format.md).

## Core Rule

`rhythmpress project create` creates a small source skeleton first. It must install only:

- core project files;
- feature packs explicitly requested by CLI/config;
- feature packs implied by core parameters, such as multilingual language-switcher support when more than one language is configured.

It must not copy `rhythmdo-com`'s accumulated `filters/`, `assets/`, `.assets/`, `.project-lilypond/` formerly `common-ly/`, or `templates/` directories wholesale.

## Feature Pack Definition

A feature pack is a deterministic bundle of source-layer project behavior.

Feature packs may provide:

- source files;
- `_quarto.yml` patches;
- `_metadata-<lang>.yml` patches;
- `.gitignore` patterns;
- `.quartoignore` patterns;
- manifest entries;
- external dependency declarations;
- verification checks;
- generated-artifact exclusions.

Feature packs may not:

- execute arbitrary install scripts during `project create`;
- create rendered output;
- create generated Rhythmpress or Quarto artifacts;
- silently mutate user files outside the generated plan;
- embed site-specific IDs or branding without explicit user configuration.

Feature packs are authored and distributed as plugin packages. A feature pack may start life as a built-in package shipped with Rhythmpress, but it must still obey the package manifest, materialization, ownership, and verification rules.

## Feature-Pack Manifest Shape

Feature pack manifests should be representable as package `plugin.yml` data. The example below is a feature-pack-focused subset of the full package schema.

```yml
id: filter-lilypond
default: false
description: Render LilyPond notation during Quarto render.
depends-on:
  - core
source-files:
  - path: filters/lilypond.lua
    template: packs/filter-lilypond/filters/lilypond.lua
quarto-patch:
  format.html.filters:
    - filters/lilypond.lua
  resources:
    - .project-lilypond/*.ly
gitignore:
  - /lilypond-out/
external-tools:
  - lilypond
generated-exclusions:
  - lilypond-out/
verification:
  - file-exists: filters/lilypond.lua
  - config-list-contains: format.html.filters filters/lilypond.lua
```

Manifest rules:

- `id` is stable and appears in `.rhythmpress-template.json`.
- `depends-on` is explicit.
- `source-files` are authored template inputs, not generated files.
- `quarto-patch` and metadata patches are deterministic.
- External tools and external network scripts are declared.
- Generated outputs are excluded from ownership.
- Package-level rules for archive form, package locations, activation, deactivation, update, and security live in the package-format specification.

## Patch Semantics

Feature packs patch structured config, not raw strings, where possible.

Patch behavior:

- maps deep-merge with later explicit values winning;
- lists append only when the value is absent;
- generated render/profile files are never patched;
- raw HTML header blocks are grouped by feature owner;
- failed validation blocks the whole create operation before writing files.

The first implementation may centralize patches in Python, but the data model must stay inspectable so later project lifecycle commands can compare desired state against actual files.

## User-Facing Desired State

`_quarto.yml` is the user-facing desired-state surface.

Minimum shape:

```yml
rhythmpress:
  project:
    manifest: ".rhythmpress-template.json"
    languages:
      - "en"
    default-language: "en"
    starter-article: "about"
    starter-mode: "split"
    features:
      404: true
      language-switcher: "auto"
      toc-helper: true
      meta-dates: false
      remove-softbreaks: false
      include-files: false
      lilypond: false
      obsidian-image-dimensions: false
      twitter-video: false
      cookiebot: false
      adsense: false
      groovespace: false
      custom-theme: false
      social-cards: false
      github-actions: false
      cloudflare-router: false
      sidebar-hook: false
```

Values should be explicit so users can discover available customization by reading `_quarto.yml`.

## Feature Pack Table

| Feature Pack | Trigger | Default | Source Files | Config Patches | Generated Exclusions | External Dependencies | Notes |
|---|---|---|---|---|---|---|---|
| `core` | always | on | `_quarto.yml`, `_metadata-<lang>.yml`, `_rhythmpress.conf`, starter masters, sidebar inputs, root pages | base Quarto website config; `rhythmpress.project` skeleton | `_quarto-*`, `_sidebar-*.generated.*`, `.site*`, `.quarto` | Quarto, yq, Git for full lifecycle, rsync for assemble | Minimal healthy project skeleton. |
| `404` | `--with-404` / default core-site | on | root `404.qmd`, language `404.qmd` | render includes root QMD | none | Quarto | Recommended default but not lifecycle-minimum. |
| `language-switcher` | `--with-language-switcher`, auto for multi-lang | auto | none for generated JS; optional source header slot | navbar slot and script include | `lang-switcher*.generated.mjs` | Rhythmpress `render-lang-switcher-js`; browser DOM | Source contract only; JS generated by build. |
| `toc-helper` | always unless explicitly disabled later | on | cleaned `assets/rhythmpress-toc.mjs` or equivalent; starter page `#toc` target | header include for local module | none | browser DOM | Based on `toc-ul.mjs`, because a visible TOC is one of the first useful checks in a new project. |
| `filter-meta-dates` | `--with-meta-dates` | off | `filters/meta-dates.lua` | `format.html.filters` append | none | Pandoc Lua | Uses explicit `cdate` and `mdate`; separate from Git-date preprocessing. |
| `filter-remove-softbreaks` | `--with-remove-softbreaks` | off | `filters/remove-softbreaks.lua` | `format.html.filters` append | none | Pandoc Lua | Risky for manually wrapped English prose. |
| `filter-include-files` | `--with-include-files` | off | `filters/include-files.lua` | `format.html.filters` append | none | Pandoc 2.12+ Lua modules | No active dependency found in current authored source. |
| `filter-lilypond` | `--with-lilypond` | off | `filters/lilypond.lua`, minimal `.project-lilypond/` preamble | filter append, `metadata.lilypond-preamble`, `resources` | `lilypond-out/` | `lilypond`, `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR` | Heavy but reusable; Rhythmdo shared notation library is not generic. |
| `filter-obsidian-image-dimensions` | future flag | off | cleaned filter only | filter append | none | Pandoc Lua | Current file is disabled and debug-printing; defer. |
| `asset-twitter-video` | `--with-twitter-video` | off | renamed JS module and optional CSS fragment | header include for local module and external widgets script | none | Twitter widgets script; browser DOM | Must not retain `ats4u` naming in generic pack. |
| `asset-cookie-settings` | `--with-cookie-settings` plus provider config | off | CMP settings JS | footer/link/header provider block | none | Cookiebot or IAB TCF API | Requires provider ID; no default ID. |
| `asset-toc-generator` | future developer flag | off | cleaned console generator only if needed | none by default | none | browser DOM console | `toc-generator.mjs` is developer output and should not be installed as-is by default. |
| `asset-groovespace` | custom/domain flag | off | Groovespace JS/CSS and optional Python helper | header include | none | browser DOM; optional Python snippets | Domain/content-specific, not default. |
| `theme-custom` | `--with-theme` / future theme selection | off | SCSS/CSS fragments | metadata theme/css entries | none | Quarto SCSS; possible external fonts | Must split generic fixes from Rhythmdo branding. |
| `social-cards` | `--with-social-cards` | off | config only initially | `rhythmpress.social-cards` defaults | rendered social images | Playwright/browser only when running render command | `project create` must not render cards. |
| `github-actions` | `--with-github-actions` | off | workflow YAML | none | build artifacts | GitHub Actions runner tools | Deployment pack, not core. |
| `cloudflare-router` | `--with-cloudflare-router` | off | source config template only | router desired-state config | generated worker/wrangler outputs | Cloudflare Workers/Wrangler | Depends on language model. |
| `sidebar-hook` | `--with-sidebar-hook` | off | hook templates | none | generated sidebar YAML remains excluded | Python and PyYAML | Visible opt-in because hooks mutate generated YAML. |

## CLI Flag Direction

First implementation should keep optional packs out of the initial code patch unless explicitly approved later. The flag model should still reserve names:

```sh
rhythmpress project create my-site --with-lilypond
rhythmpress project create my-site --with-meta-dates
rhythmpress project create my-site --with-remove-softbreaks
rhythmpress project create my-site --with-twitter-video
rhythmpress project create my-site --with-social-cards
rhythmpress project create my-site --with-cloudflare-router
```

Language switcher behavior:

- single language: off unless explicitly enabled;
- multiple languages: auto-on unless explicitly disabled;
- generated JS is still produced by `rhythmpress build`, not `project create`.

TOC helper behavior:

- default projects install a cleaned visible TOC helper;
- the starter page includes a `#toc` target so the helper proves itself immediately;
- `toc-ul.mjs` is the source behavior to preserve;
- `toc-generator.mjs` is not installed as-is because it writes console Markdown/YAML instead of user-visible UI.

## CSS Ownership Contract

No feature pack may claim `assets/styles.css` wholesale.

Instead:

- each pack owns a small CSS file or SCSS fragment;
- `_metadata-<lang>.yml` or `_quarto.yml` references only selected CSS;
- site branding lives in `theme-custom` or user-owned files;
- project lifecycle commands must not overwrite user-owned CSS.

Required first split candidates:

- `filter-lilypond`: LilyPond image sizing and dark-mode SVG handling.
- `asset-twitter-video`: tweet caption styling after generic rename.
- `asset-groovespace`: perspective and division table CSS.
- `theme-custom`: theme variables, fonts, logo behavior, and Quarto layout overrides.

## Write And Ownership Rules

Feature pack writes follow the same safety rules as core project creation:

- write only planned source files;
- list every managed source file in `.rhythmpress-template.json`;
- store the owning feature pack for every managed path;
- refuse unmanaged collisions;
- refuse changed managed files unless a future update command implements merge behavior;
- never delete generated artifacts;
- never add generated artifacts to managed files.

Feature packs are not copied directly from source directories. They are materialized from a package write plan. The package remains the pre-materialization source of truth; `_quarto.yml` records desired enabled state; `.rhythmpress-template.json` records the materialized state and file hashes.

Example manifest entry:

```json
{
  "path": "filters/lilypond.lua",
  "kind": "source",
  "feature": "filter-lilypond",
  "sha256": "<hex>"
}
```

## Verification Rules

Each feature pack needs lightweight verification.

Examples:

- `file-exists`: source files exist.
- `config-list-contains`: `_quarto.yml` contains the filter/header/resource entry.
- `config-key-type`: provider IDs or booleans have expected types.
- `generated-absent`: generated outputs are not present after `project create`.
- `ignore-contains`: generated cache patterns are ignored.

Verification must not require rendering unless the user explicitly runs lifecycle proof commands.

## First Implementation Cut

The first code patch should implement only core `rhythmpress project create` unless a later approval expands scope.

However, the core skeleton should include the explicit `rhythmpress.project.features` map, with default values, so users can see available future behavior without reading internal docs. The default TOC helper is core behavior, not an optional feature-pack expansion.

Optional packs should be designed from this spec before implementation, not copied from `rhythmdo-com` directories.

When optional packs are implemented, they should be implemented through the package-format contract rather than ad hoc per-feature file copying.
