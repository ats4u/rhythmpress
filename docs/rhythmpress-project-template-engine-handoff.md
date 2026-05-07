# Rhythmpress Project Template Engine Handoff

Created: 20260507-065012

Status: conversation renewal handoff.

## Purpose

This file is the recovery document for the Rhythmpress project template-engine work. It exists so a new conversation can resume from file state instead of relying on chat memory.

The working goal is to use `rhythmdo-com` as the evidence project, recover its implicit structure, and implement a clean Rhythmpress project skeleton/template engine without copying accumulated site-specific behavior wholesale.

Primary implementation target:

```sh
rhythmpress project create <project-dir>
```

The first implementation patch should create only the core skeleton. Plugin lifecycle commands and optional feature-pack install/deploy behavior are future work unless explicitly approved later.

## Canonical Specs

The durable specifications live in these files:

- [Project Lifecycle Template Engine](spec-rhythmpress-project-lifecycle-template-engine.md)
- [Rhythmpress Plugin System Spec](spec-rhythmpress-plugin-system.md)
- [Plugin Feature Packs](spec-rhythmpress-project-plugin-feature-packs.md)
- [Plugin Package Format](spec-rhythmpress-project-plugin-package-format.md)
- [Plugin And Scriptlet Audit](spec-rhythmpress-project-plugin-scriptlet-audit.md)
- [Scriptlet Dependency Map](spec-rhythmpress-project-scriptlet-dependency-map.md)
- [Rhythmdo Directory Reorganization Progress](rhythmdo-directory-reorganization-progress.md)
- [Template Engine Progress Tracker](progress-tracker-for-template-engine.md)

Specs for the `rhythmpress project *` command family must use the filename prefix `spec-rhythmpress-project-*`.

## Command Direction

Use the nested command family:

```sh
rhythmpress project create
rhythmpress project check
rhythmpress plugin install
rhythmpress plugin uninstall
rhythmpress plugin list
rhythmpress plugin inspect
```

Do not add legacy aliases such as `create-project` or `create-page`. There is no legacy compatibility requirement.

`create page` was discussed, then corrected away. Page/article creation is not the current first implementation target.

## Core Skeleton Contract

`rhythmpress project create` should create a minimal healthy Quarto/Rhythmpress source tree.

The skeleton should include:

- `_quarto.yml`
- `_metadata-<lang>.yml`
- `_rhythmpress.conf`
- starter article/page source files
- starter sidebar input files
- `.rhythmpress-template.json` as the internal ownership manifest
- public `assets/` only when a browser-facing default asset is installed

It must not create generated artifacts:

- `_quarto-<lang>.yml`
- `_sidebar-*.generated.*`
- `lang-switcher.generated.mjs`
- `.site`
- `.site-*`
- `.quarto`
- `lilypond-out/`
- rendered social-card images

`_rhythmpress.conf` remains an article-target list only. Do not add language, feature, or project metadata to it until existing command readers support that format.

## User-Facing Desired State

`_quarto.yml` must contain an explicit `rhythmpress.project` section so users can discover configurable defaults by reading the generated file.

Minimum intended shape:

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

`.rhythmpress-template.json` is internal project-generation ownership state. It records owned source files, hashes, package ownership where relevant, and whether a future command can safely repair or update files.

## Directory Policy

Project skeletons and optional deployed plugin files must make ownership visible from paths.

Directory classes:

| Path pattern | Ownership | Public-facing? |
| --- | --- | --- |
| `assets/` | Public browser/runtime assets | yes |
| `attachments*/` | Content-facing durable assets | yes or source-facing |
| `.quarto-*` | Quarto-local source infrastructure | no |
| `.rhythmpress-*` | Rhythmpress-managed local state | no |
| `.project-*` | Project-specific private support files | no |
| `.site`, `.site-*`, `.quarto` | Generated output/state | output only |

Use static `.project-*` names, not `.<project-name>-*`, because static names are predictable and auditable.

Current reference names from the Rhythmdo cleanup:

- `.quarto-filters/` for Pandoc Lua filters
- `.quarto-theme/` for Quarto SCSS/theme source
- `.project-lib/` for project-private helper scripts
- `.project-templates/` for project-private authoring templates
- `.project-translation/` for translation working state
- `.project-lilypond/` for LilyPond private source files

Private source directories must not leak into public HTML as preload links, image titles, fallback alt text, or public runtime dependencies. If source material must become public, it should be copied or rendered into an explicit public path such as `assets/`.

## Plugin And Package Plan

CSS, JavaScript, filters, helper scripts, templates, and config snippets should belong to explicit core or plugin packages. They must not be scattered as anonymous top-level files.

Future packages are deterministic, inspectable bundles:

- `plugin.yml` is the package source of truth.
- `.rhythmpress-plugins/packages/` stores installed package contents.
- `.rhythmpress-plugins/packages.yml` stores active package order and CSS/filter precedence.
- packages are referenced in place by generated Quarto wiring by default.
- `deploy.files` is the explicit escape hatch for files that must land in project paths.
- package archives may be tar-based, but the unpacked form must remain easy to edit and diff.
- packages declare Quarto wiring, optional deploy files, dependencies, external tools, external scripts, generated exclusions, and verification checks.

Deploy target classes should follow the directory policy:

- `assets/**`
- `.quarto-filters/**`
- `_extensions/**`
- `attachments*/**`
- `include/**`
- `templates/**`

`rhythmpress build` must not enable packages. If build-time plugin sync is introduced later, it may only regenerate wiring for packages already listed in `.rhythmpress-plugins/packages.yml`.

## Feature-Pack Decisions

Default or auto behavior:

- `core`: always.
- `404`: default-on for a useful web skeleton unless implementation scope narrows it.
- `language-switcher`: auto when multiple languages are configured; generated JS remains build output.
- `toc-helper`: default-on. Use the useful behavior of `toc-ul.mjs`, cleaned and renamed as a Rhythmpress-owned asset such as `assets/rhythmpress-toc.mjs`. Starter content should include a visible `#toc` target.

Optional generic behavior:

- `filter-meta-dates`
- `filter-remove-softbreaks`, with explicit warning because it can damage wrapped English prose
- `filter-include-files`, later only because no active Rhythmdo dependency was found
- `filter-lilypond`, heavy opt-in with minimal generic preamble
- `filter-obsidian-image-dimensions`, defer because current file was disabled/debug-printing
- `asset-twitter-video`, opt-in and renamed away from `ats4u`
- `asset-cookie-settings`, opt-in and provider-config-required
- `social-cards`, opt-in config only; rendering remains a separate command
- `github-actions`
- `cloudflare-router`
- `sidebar-hook`, opt-in because hooks mutate generated files

Do not migrate by default:

- `toc-generator.mjs` as-is, because it logs developer output to the console
- Groovespace
- Dojo CSS
- Rhythmdo branded theme/logo rules
- AdSense
- GitHub ribbon
- attribution footer
- personal Obsidian/project authoring templates
- Rhythmdo-specific LilyPond shared notation library

## CSS And JavaScript Boundary

CSS is the highest-risk migration surface.

Do not copy these into generic skeletons:

- `assets/styles.css` wholesale
- `.quarto-theme/websites/theme.scss` wholesale

Required split direction:

- LilyPond image sizing and dark-mode SVG behavior belongs to `filter-lilypond`.
- Twitter/X caption styling belongs to `asset-twitter-video`.
- Groovespace perspective/table CSS belongs to a Rhythmdo/domain-specific pack.
- Dojo CSS is content-specific, not a default.
- Rhythmdo logo replacement, fonts, and branding belong to a site-specific theme.
- Generic Quarto fixes may become a future theme utility only after they are separated from site branding.
- Cookiebot, AdSense, and Twitter widgets are external scripts and must declare provider IDs, network/privacy implications, and config requirements.

Global `include-in-header` loading should not become the default pattern for every feature. A future plugin should either inject only its declared snippets or clearly declare the global cost and dependency.

## Rhythmdo Cleanup State

Recent Rhythmdo reference-project cleanup established these names:

- `filters/` -> `.quarto-filters/`
- `.assets/` -> `.quarto-theme/`
- `lib/` -> `.project-lib/`
- `templates/` -> `.project-templates/`
- `lib-translation/` -> `.project-translation/`
- `common-ly/` -> `.project-lilypond/`
- `bin/offbeat-count-join-en` moved into `.project-lib/offbeat-count-join-en`

The cleanup purpose was not cosmetic. It made public assets, Quarto-local files, Rhythmpress-local state, and project-local private helpers distinguishable from their paths.

`assets/` remains public web/runtime assets.

`.project-lilypond/` is private source infrastructure. The current filter no longer emits public preload links to `.project-lilypond`. Remaining `.project-lilypond` strings in rendered HTML were found only in source comments and were accepted as non-serious.

## First Implementation Pass

Before editing code, do a read-only reconnaissance of `rhythmpress`:

- CLI entrypoints and command dispatch
- current command naming patterns
- existing project/page creation code, if any
- template file locations
- YAML/config write helpers
- test style and verification commands
- existing build/finalize assumptions that `project create` must satisfy

The output of that reconnaissance should be an implementation edit plan listing:

- exact files to edit
- exact behavior for `rhythmpress project create`
- tests to add or update
- verification commands
- unresolved risks

The first code patch should implement only core `rhythmpress project create`. Do not implement plugin install, uninstall, generated wiring sync, update, registry lookup, tar archive input, or CSS feature-pack migration in the first patch.

## Easy To Forget Constraints

- Keep behavior unchanged outside the new command unless explicitly approved.
- Do not create generated artifacts in a project skeleton.
- Do not put project metadata into `_rhythmpress.conf`.
- Do not copy Rhythmdo directories wholesale.
- Do not make site-specific IDs, remote scripts, ads, consent manager IDs, branding, or personal authoring templates default.
- Do not let private `.project-*` or `.quarto-*` paths become public runtime paths unless explicitly mirrored into `assets/`.
- Keep package ownership single-source: one file path, one owning package in the manifest.
- Use structured config patching rather than raw string rewriting where practical.
- Preserve explicit defaults in `_quarto.yml` so users can discover customization points.
- Keep optional packs designed through the package-format contract rather than ad hoc file copying.
