# Rhythmpress Project Plugin Feature Packs

Created: 20260506-142202
Updated: 20260507-172326

Status: draft design specification.

## Purpose

Define how `rhythmpress project create` should represent optional scriptlets, filters, assets, CSS, and deployment support as deterministic feature packs.

This document consumes the evidence in [Scriptlet Dependency Map](spec-rhythmpress-project-scriptlet-dependency-map.md).

Feature packs should be implemented as plugin packages. The canonical plugin-system storage, ordering, and wiring contract is specified in [Rhythmpress Plugin System Spec](spec-rhythmpress-plugin-system.md). The package artifact details are specified in [Plugin Package Format](spec-rhythmpress-project-plugin-package-format.md).

## Core Rule

`rhythmpress project create` creates a small source skeleton first. It must install only:

- core project files;
- feature packs explicitly requested by CLI/config;
- feature packs implied by core parameters, such as multilingual language-switcher support when more than one language is configured.

It must not copy `rhythmdo-com`'s accumulated `.quarto-filters/`, `assets/`, `.quarto-theme/`, `.project-lilypond/`, `.project-lib/`, `.project-translation/`, or `.project-templates/` directories wholesale.

## Feature Pack Definition

A feature pack is a deterministic bundle of source-layer project behavior.

Feature packs may provide:

- package-local files referenced by generated Quarto wiring;
- global Quarto contributions equivalent to `_quarto.yml` entries;
- language metadata contributions equivalent to `_metadata-<lang>.yml` entries;
- optional deployed files with explicit `from` / `to` rules;
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

Feature packs are authored and distributed as plugin packages. A feature pack may start life as a built-in package shipped with Rhythmpress, but it must still obey the package manifest, reference-in-place wiring, optional deploy ownership, and verification rules.

## Feature-Pack Manifest Shape

Feature pack manifests should be representable as package `plugin.yml` data. The example below is a feature-pack-focused subset of the full package schema.

```yml
id: filter-lilypond
default: false
description: Render LilyPond notation during Quarto render.
depends-on:
  - core
quarto:
  global:
    format.html.filters:
      - filters/lilypond.lua
    resources:
      - lilypond/*.ly
deploy:
  files: []
gitignore:
  - /lilypond-out/
external-tools:
  - lilypond
generated-exclusions:
  - lilypond-out/
verification:
  - package-file-exists: filters/lilypond.lua
  - generated-config-contains: format.html.filters .rhythmpress-plugins/packages/filter-lilypond/filters/lilypond.lua
```

Manifest rules:

- `id` is stable and appears in `plugin.yml` and `.rhythmpress-plugins/packages.yml` when active.
- `depends-on` is explicit.
- `quarto` contributions are authored package inputs, not generated files.
- Quarto and metadata contributions are deterministic and generated from package order.
- `deploy.files` is optional and must be used only when a file must land in a project path.
- External tools and external network scripts are declared.
- Generated outputs are excluded from ownership.
- Package-level rules for archive form, package locations, install, uninstall, update, and security live in the package-format specification and the canonical plugin-system spec.

## Contribution Semantics

Feature packs contribute structured config, not raw strings, where possible.

Patch behavior:

- maps deep-merge;
- lists append in `.rhythmpress-plugins/packages.yml` order;
- scalar conflicts fail unless the key is explicitly listed as last-wins;
- generated render/profile files are never patched;
- raw HTML header blocks are grouped by feature owner;
- failed validation blocks the whole create operation before writing files.

The first implementation may centralize generated wiring in Python, but the data model must stay inspectable so later project lifecycle commands can compare active package state against generated config and optional deployed files.

## User-Facing Desired State

`_quarto.yml` remains the user-facing project skeleton surface. Active package order is managed by `.rhythmpress-plugins/packages.yml`, not by arbitrary map order inside `_quarto.yml`.

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

| Feature Pack | Trigger | Default | Package Files | Quarto Wiring | Generated Exclusions | External Dependencies | Notes |
|---|---|---|---|---|---|---|---|
| `core` | always | on | `_quarto.yml`, `_metadata-<lang>.yml`, `_rhythmpress.conf`, starter masters, sidebar inputs, root pages | base Quarto website config; `rhythmpress.project` skeleton | `_quarto-*`, `_sidebar-*.generated.*`, `.site*`, `.quarto` | Quarto, yq, Git for full lifecycle, rsync for assemble | Minimal healthy project skeleton. |
| `404` | `--with-404` / default core-site | on | root `404.qmd`, language `404.qmd` | render includes root QMD | none | Quarto | Recommended default but not lifecycle-minimum. |
| `language-switcher` | `--with-language-switcher`, auto for multi-lang | auto | none for generated JS; optional source header slot | navbar slot and script include | `lang-switcher*.generated.mjs` | Rhythmpress `render-lang-switcher-js`; browser DOM | Source contract only; JS generated by build. |
| `toc-helper` | always unless explicitly disabled later | on | cleaned `assets/rhythmpress-toc.mjs` or equivalent; starter page `#toc` target | header include for local module | none | browser DOM | Based on `toc-ul.mjs`, because a visible TOC is one of the first useful checks in a new project. |
| `filter-meta-dates` | `--with-meta-dates` | off | `.quarto-filters/meta-dates.lua` | `format.html.filters` append | none | Pandoc Lua | Uses explicit `cdate` and `mdate`; separate from Git-date preprocessing. |
| `filter-remove-softbreaks` | `--with-remove-softbreaks` | off | `.quarto-filters/remove-softbreaks.lua` | `format.html.filters` append | none | Pandoc Lua | Risky for manually wrapped English prose. |
| `filter-include-files` | `--with-include-files` | off | `.quarto-filters/include-files.lua` | `format.html.filters` append | none | Pandoc 2.12+ Lua modules | No active dependency found in current authored source. |
| `filter-lilypond` | `--with-lilypond` | off | `.quarto-filters/lilypond.lua`, minimal `.project-lilypond/` preamble | filter append, `metadata.lilypond-preamble`, `resources` | `lilypond-out/` | `lilypond`, `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR` | Heavy but reusable; Rhythmdo shared notation library is not generic. |
| `filter-obsidian-image-dimensions` | future flag | off | cleaned `.quarto-filters/` filter only | filter append | none | Pandoc Lua | Current file is disabled and debug-printing; defer. |
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

SCSS should be used only where the Quarto/Bootstrap theme compiler is the reason for the file to exist:

- Sass variables and Bootstrap/Quarto variable overrides;
- true theme defaults;
- mixins, functions, or other Sass features if introduced later;
- dark/light theme entry files consumed by Quarto's `theme:` setting.

Plain selector CSS should generally live under `assets/` instead:

- logo replacement and other site branding;
- navbar/sidebar DOM patches;
- content or feature CSS;
- browser workarounds;
- font delivery via `@font-face` and language font-family rules when they do not need Bootstrap Sass variables.

The default project skeleton should use system font stacks. Rhythmdo's current public web-font imports are site-specific and must not become generic defaults. If a project self-hosts fonts, package font files under `assets/fonts/` and load them from a focused asset CSS file instead of hiding them inside a broad theme SCSS file.

Required first split candidates:

- `filter-lilypond`: LilyPond image sizing and dark-mode SVG handling.
- `asset-twitter-video`: tweet caption styling after generic rename.
- `asset-groovespace`: perspective and division table CSS.
- `theme-custom`: theme variables, fonts, logo behavior, and Quarto layout overrides.

## Wiring, Deploy, And Ownership Rules

Feature pack wiring follows the canonical plugin-system rules:

- reference package files in place by default;
- generate Quarto wiring from active package order;
- deploy files only when `deploy.files` explicitly asks for it;
- record ownership for deployed files and generated wiring;
- refuse unmanaged deploy collisions;
- refuse changed managed deployed files unless a future update command implements merge behavior;
- never delete generated artifacts;
- never add generated artifacts to managed files or package source.

Feature packs are not copied directly from source directories into the project tree. The package directory under `.rhythmpress-plugins/packages/<plugin-id>/` remains the source of truth; `.rhythmpress-plugins/packages.yml` records active order; generated wiring records how Quarto consumes package-local files. Optional deployed files record hashes and ownership separately.

Example manifest entry:

```json
{
  "path": "assets/player.js",
  "kind": "deployed",
  "feature": "asset-twitter-video",
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
