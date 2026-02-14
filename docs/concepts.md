# Concepts

This document defines the core concepts Rhythmpress uses. The goal is to give you a stable mental model so you can predict where files will be generated, how language selection works, and how sidebars/navigation are assembled.

## Scope

Rhythmpress is a Quarto-oriented *preprocessor and build orchestrator*. You author “master” documents, Rhythmpress generates Quarto-ready page trees and navigation artifacts, and then Quarto renders the site.

Rhythmpress does **not** replace Quarto. It prepares inputs and glue files so Quarto projects scale cleanly across many article directories and (optionally) multiple languages.

## Core terminology

Project root  
The directory that represents a single Quarto project. In practice, it is the directory that contains `_quarto.yml`. Many Rhythmpress paths are resolved relative to the project root.

Article directory  
A directory that contains one or more master files (e.g. `master-en.qmd`, `master-ja.qmd`) and is treated as a “unit” by `preproc`, `preproc-clean`, and `build`.  
An article directory SHOULD contain `.article_dir` as a safety sentinel; cleaning refuses to run without it.

Master file  
The single source document Rhythmpress reads to generate output pages. Master files MUST follow this naming pattern:

- `master-<lang>.qmd` or `master-<lang>.md`

If both `.qmd` and `.md` exist for the same language, `.qmd` is preferred.

Language ID (LANG_ID)  
`<lang>` in `master-<lang>.*` is the language ID (e.g. `en`, `ja`).  
`LANG_ID` is also an environment variable that constrains processing to a single language when multiple masters exist.

Preprocessing (preproc)  
The transformation step that reads a master file and emits generated `.qmd` pages and optional per-article sidebar fragments. Preproc is controlled by a mode (copy or split).

Preproc mode: copy  
“Copy” means: one master becomes one generated page per language.

Preproc mode: split  
“Split” means: one master becomes multiple generated pages per language, typically one page per section heading.

Generated page  
A `.qmd` file produced by Rhythmpress (not directly authored). It is expected to be overwritten whenever you rerun preprocessing.

Slug  
A filesystem-safe identifier used to name output directories for split sections. Slugs are derived from section titles unless an explicit header ID is provided.

Sidebar fragment  
A YAML file (usually `_sidebar-<lang>.yml`) that represents one article’s contribution to the overall Quarto sidebar. Rhythmpress can generate these per article, then merge them at the project root.

Generated sidebar YAML / MD  
Project-root artifacts created by merging many fragments (via `yq`) and optionally rendering a Markdown TOC from the merged sidebar.

TOC (Table of Contents)  
In Rhythmpress projects, “TOC” can mean two different things:

- Master-heading TOC: derived from headings in a master file (used for split index pages and per-article navigation).
- Sidebar TOC: derived from Quarto sidebar YAML (used to render `_sidebar-<lang>.generated.md`).

These are related but not identical.

## Content model

### Copy mode mental model

Copy mode is the simplest layout.

Input (authored):
- `<ARTICLE_DIR>/master-<lang>.qmd`

Output (generated):
- `<ARTICLE_DIR>/<lang>/index.qmd`

Conceptually, copy mode makes your master “look like a normal Quarto page,” placed under a language directory. This is a good fit for short or narrative articles.

### Split mode mental model

Split mode turns one master into a small page tree.

Input (authored):
- `<ARTICLE_DIR>/master-<lang>.qmd`

Output (generated):
- `<ARTICLE_DIR>/<lang>/index.qmd` (language index / entry page)
- `<ARTICLE_DIR>/<slug>/<lang>/index.qmd` (one per section)

The section boundaries are driven primarily by H2 headings (`## ...`). If your master contains no H2 headings, split mode will not produce meaningful section pages.

### Headings and splitting rules

- Split mode uses **H2 (`##`)** as the unit of splitting.
- Each H2 SHOULD be unique in its resulting slug to avoid collisions.
- You SHOULD prefer explicit header IDs for stability and uniqueness:

  `## My Section Title {#my-section}`

When explicit IDs exist, they take precedence over auto-slugging.

### Slug generation and collisions

Slug generation is designed to be predictable, not “magical.”

- If an H2 has an explicit `{#id}`, that ID is used as the slug.
- Otherwise, the visible title text is slugified.

There is typically **no collision resolution**. Two sections that produce the same slug will overwrite the same output path. You MUST prevent this by using explicit IDs when titles might repeat or normalize to the same slug.

### Ruby and title normalization

If you use Ruby markup in headings (e.g. `<ruby>...<rt>...</rt></ruby>`), Rhythmpress may normalize titles by stripping or ignoring the `<rt>` reading portion when constructing navigation/slug text.

Practical implication:
- Do not rely on `<rt>` content to differentiate sections.
- Use explicit `{#id}` when Ruby titles are involved.

## Language model

### One master vs. multiple masters per directory

An article directory MAY contain:
- exactly one master (single language), or
- multiple masters (one per language).

Behavioral expectation:
- If multiple `master-<lang>.*` files exist, you SHOULD set `LANG_ID=<lang>` when running commands that operate on a single directory, unless you explicitly want “build all languages.”

### Build-level language behavior

At the build/orchestrator level, the common policy is:

- If `LANG_ID` is set: process only that language.
- If `LANG_ID` is not set and multiple masters exist: process all detected languages.
- If only one master exists: process that one.

This policy is designed so that local development can focus on one language while CI (or full rebuilds) can build all languages by default.

## Sidebar and navigation model

Rhythmpress supports a “fragment + aggregation” navigation architecture.

### Per-article sidebar fragments

Each article directory MAY have a per-language sidebar fragment:

- `<ARTICLE_DIR>/_sidebar-<lang>.yml`

In many workflows, Rhythmpress generates this file during preprocessing (copy or split), reflecting the page(s) generated for that article.

You MAY disable per-article sidebar generation via the master front matter (see `docs/configuration.md`).

### Project-level sidebar aggregation

At the project root, Rhythmpress can assemble a list of sidebar fragments into a single generated sidebar via a `.conf` file and `yq` merge:

- `_sidebar-<lang>.generated.conf` (a list of YAML files to merge)
- `_sidebar-<lang>.generated.yml` (merged Quarto sidebar YAML)
- `_sidebar-<lang>.generated.md` (Markdown TOC rendered from the merged sidebar)

A typical aggregation pattern is:

1) include a “before” YAML (project-wide fixed entries)
2) include all per-article fragments discovered from `_rhythmpress.conf`
3) include an “after” YAML (project-wide fixed entries)

### Merge semantics

Merging is performed by `yq` (Mike Farah v4). The effective semantics are “deep merge with later files overriding earlier values” (last-wins). This makes ordering meaningful:

- Put base/global defaults in “before”
- Let per-article fragments override within their scope
- Put global appendages in “after”

### Optional post-merge hook

A project-root hook MAY be executed after the generated sidebar YAML is written. This is intended for “final edits” that are easier in Python than in YAML merge rules (e.g., rewriting labels, injecting additional entries, normalizing paths). Hook failures are typically treated as non-fatal.

## Generated artifacts map

This section describes “what appears where” at a conceptual level. For the full file list, see README section “Generated artifacts” as well as `docs/configuration.md` (because some outputs depend on configuration choices).

### Inside an article directory

Authored:
- `master-<lang>.qmd` / `master-<lang>.md`
- `attachments*/` (assets)

Scaffolded (one-time):
- `.article_dir` (required for safe clean)
- `.gitignore` (commonly ignores generated outputs)

Generated (regenerated often):
- `<lang>/index.qmd` (copy mode output, and also split index page)
- `<slug>/<lang>/index.qmd` (split mode section pages)
- `_sidebar-<lang>.yml` (per-article sidebar fragment, if enabled)

Cleaning behavior concept:
- `preproc-clean` deletes generated directories/files, but preserves `attachments*/`.
- Cleaning is intentionally guarded by `.article_dir`.

### At the project root

Authored:
- `_quarto.yml`
- `_rhythmpress.conf` (list of article directories to build)
- Optional `_sidebar-<lang>.before.yml` / `_sidebar-<lang>.after.yml`

Generated:
- `_sidebar-<lang>.generated.conf`
- `_sidebar-<lang>.generated.yml`
- `_sidebar-<lang>.generated.md`

### In Quarto output directories

Generated by Quarto:
- `.quarto/`, `.site/` (preview state)
- `_site/` or the configured Quarto output directory (rendered HTML)

Generated by Rhythmpress after rendering:
- `sitemap.xml` in the Quarto output directory (if you run `rhythmpress sitemap`)

## Invariants and assumptions

These are “design commitments” you can rely on.

Deterministic output locations  
Given the same master and the same mode, generated files are written to stable, predictable paths (`<lang>/index.qmd`, `<slug>/<lang>/index.qmd`, etc.).

Safety by sentinel  
Destructive cleaning is gated by the presence of `.article_dir`. This is intentional and SHOULD NOT be removed casually.

Git-backed dating (today’s policy)  
Generated pages typically receive created/modified dates derived from git history. Projects SHOULD be in git, and masters SHOULD be committed for best results.

Project-root oriented execution  
Many commands assume project-root-relative paths. You SHOULD run from the project root or ensure `RHYTHMPRESS_ROOT` is set correctly.

## Where to go next

- For “how do I do X?” workflows: see `docs/workflows.md`.
- For command flags and examples: see `docs/commands.md`.
- For configuration formats and supported front matter keys: see `docs/configuration.md`.
- For common failures and fixes: see `docs/troubleshooting.md`.

