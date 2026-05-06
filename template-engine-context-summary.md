# Template Engine Context Summary

Created: 20260505-160003

## Purpose Of This File

This file is a handoff summary for continuing the Rhythmpress template engine work in a fresh or forked conversation.

The conversation started as an attempt to compare `rhythmdo-com` and `thetokyojazz.com`, then shifted into a broader and more important goal: designing and implementing a reusable project generator for Rhythmpress.

The new goal is not a one-off migration. The new goal is to build a templating program that can create an empty, fully functioning Rhythmpress project.

## Current Goal

Build a Rhythmpress command, likely named:

```sh
rhythmpress create-project
```

Candidate usage:

```sh
rhythmpress create-project my-site \
  --title "My Site" \
  --site-url "https://example.com/" \
  --langs en,ja \
  --default-lang en \
  --with-lilypond \
  --with-github-actions
```

The generated project should be able to run the normal Rhythmpress lifecycle:

```sh
rhythmpress build
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize --output-dir .site --skip-social-cards
```

## Original Problem

The initial idea was to apply the framework of `rhythmdo-com` to `thetokyojazz.com`, including LilyPond support.

At first this looked like a migration problem:

- compare both repos
- copy filters and assets
- rewrite `_quarto.yml`
- add LilyPond support
- adapt GitHub Actions

That approach turned out to be too shallow, because `rhythmdo-com` is not just a Quarto site with some reusable folders. It is a Rhythmpress website, and Rhythmpress is a generation lifecycle.

## Why The Goal Changed

`rhythmdo-com` should not be treated as a directory tree to copy directly into `thetokyojazz.com`.

Instead, `rhythmdo-com` should be treated as a reference implementation of a Rhythmpress project.

The more useful deliverable is a reusable generator that creates clean Rhythmpress project skeletons. Once that exists, `thetokyojazz.com` can be rebuilt by generating a clean project structure and then adding site-specific content.

This avoids turning Rhythmdo-specific content, generated artifacts, branding, and ad-hoc history into a permanent template.

## Rhythmpress Lifecycle Model

Rhythmpress is a preprocessor and build orchestrator on top of Quarto.

It has four major layers.

### 1. Authored Source Layer

These are files humans or a template engine should create and maintain:

- `_quarto.yml`
- `_rhythmpress.conf`
- `_metadata-<lang>.yml`
- `_sidebar-<lang>.before.yml`
- `_sidebar-<lang>.after.yml`
- `index.qmd`
- article directories
- article `.article_dir` sentinels
- article `.gitignore` files
- article `master-<lang>.md` or `master-<lang>.qmd`
- optional sidebar hooks
- optional filters/assets/support files

### 2. Rhythmpress Preprocess Layer

`rhythmpress build` reads `_rhythmpress.conf`, then processes each article directory.

Important behavior:

- `preproc-clean` deletes generated article outputs, guarded by `.article_dir`.
- `preproc` dispatches by front matter.
- `rhythmpress-preproc: copy` generates one page per master.
- `rhythmpress-preproc: split` splits H2 sections into separate pages.
- `rhythmpress-preproc-sidebar: false` suppresses sidebar contribution.
- generated pages receive `cdate` and `mdate` from Git history.
- per-article `_sidebar-<lang>.yml` files are emitted when sidebars are enabled.

### 3. Navigation And Profile Generation Layer

Rhythmpress then builds navigation/profile artifacts:

- `sidebar-confs` creates `_sidebar-<lang>.generated.conf`.
- `render-sidebar` merges sidebar YAML fragments using `yq`.
- optional hook scripts may patch `_sidebar-<lang>.generated.yml`.
- `quarto-profile` generates `_quarto-<lang>.yml`.
- `render-toc` creates `_sidebar-<lang>.generated.md`.
- `render-lang-switcher-js` creates `lang-switcher.generated.mjs`.

These files are generated outputs, not canonical template source.

### 4. Render, Assemble, Finalize Layer

The production lifecycle is:

```sh
rhythmpress build
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize
```

Meaning:

- `build` prepares generated Quarto inputs.
- `render-all` renders all `_quarto-<lang>.yml` profiles into `.site-<lang>`.
- `assemble` merges `.site-*` into `.site`.
- `finalize` runs final artifact steps such as sitemap and social-card metadata.

## Key Source Vs Generated Distinction

The template engine should create source-layer files.

It should not use generated files as canonical templates unless there is a specific reason.

Generated files include:

- `_quarto-<lang>.yml`
- `_sidebar-<lang>.generated.conf`
- `_sidebar-<lang>.generated.yml`
- `_sidebar-<lang>.generated.md`
- `lang-switcher.generated.mjs`
- generated article pages such as `<article>/<lang>/index.qmd`
- split generated pages such as `<article>/<slug>/<lang>/index.qmd`
- `.site`
- `.site-*`
- `.quarto`

Source-layer files include:

- `_quarto.yml`
- `_rhythmpress.conf`
- `_metadata-<lang>.yml`
- `_sidebar-<lang>.before.yml`
- `_sidebar-<lang>.after.yml`
- `index.qmd`
- article `master-<lang>.qmd`
- article `.article_dir`
- article `.gitignore`

## Current Tracker Files

Two tracker files already exist:

- `docs/progress-tracker-for-template-engine.md`
- `docs/findings-of-templating.md`

The progress tracker contains the current goal, definition of done, open decisions, verification commands, and expanded multi-pass analysis plan.

The findings file contains initial findings about Rhythmpress lifecycle, source/generated layers, support layer, and filter behavior.

Before doing more work, read both files.

## Important Findings Already Recorded

- Rhythmpress is a lifecycle/generation framework, not a static file bundle.
- `rhythmdo-com` is a reference implementation, not a direct copy source.
- The template engine should emit source-layer files and then rely on Rhythmpress to regenerate outputs.
- `include-files.lua` is loaded in `rhythmdo-com`, but no current authored source usage was found.
- `remove-softbreaks.lua` is loaded and active. It removes Pandoc soft breaks, which supports Japanese source wrapping but can join words in space-delimited prose if manually wrapped.
- `lilypond.lua` is active and depends on project-root resolution through `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR`.
- A new generated project may have a Git-date problem because Rhythmpress currently injects `cdate` and `mdate` from Git history. A brand-new uncommitted starter master may fail preprocessing.

## Expanded Analysis Plan

The organizing question is:

> What is the smallest source tree that satisfies the Rhythmpress lifecycle, and what parameters are required to generate it safely?

The planned analysis passes are:

1. File provenance graph
2. Command dependency graph
3. Empty-project build problem
4. Minimal skeleton reduction
5. Feature pack boundaries
6. Parameter model
7. Idempotency and overwrite policy
8. Golden fixture verification

Each pass should produce durable notes in `docs/findings-of-templating.md`.

## Why A Fresh Or Forked Conversation Is Recommended

The current discussion contained exploratory detours:

- one-off `thetokyojazz.com` migration
- piecemeal `rsync` idea
- direct copy/subtract idea
- filter usage investigation
- broader template engine reframing

A fresh or forked conversation is recommended because the current goal is now precise:

> Build `rhythmpress create-project`.

The important state has been written to files, so the new conversation does not need to rely on hidden chat context.

## Recommended Startup Prompt For A New Conversation

Use this prompt:

```text
We are building a Rhythmpress template engine: `rhythmpress create-project`.

Read:
- /Users/ats/rhythmpress/template-engine-context-summary.md
- /Users/ats/rhythmpress/docs/progress-tracker-for-template-engine.md
- /Users/ats/rhythmpress/docs/findings-of-templating.md
- /Users/ats/rhythmpress/README.md
- /Users/ats/rhythmpress/docs/*.md

Goal:
Analyze rhythmdo-com in multiple passes and update findings-of-templating.md after each pass.

Do not modify code yet.
Follow discuss-first approval policy before edits.

Start with the File Provenance Graph pass.
```

## Approval Policy Reminder

The user requires discuss-first behavior.

Before editing files, provide:

1. files to edit
2. exact planned edits
3. commands to run

Wait for the exact token:

```text
APPROVE
```

Do not treat any other response as approval.
