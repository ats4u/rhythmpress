# Rhythmdo Reference Directory Reorganization Progress

Created: `20260507-023946`

Moved to Rhythmpress docs: `20260507-025100`

## Purpose

Track `rhythmdo-com` as a reference project while designing Rhythmpress project templating, directory policy, and plugin/package ownership.

This is not the canonical Rhythmpress policy by itself. It is the concrete migration tracker used to extract that policy from an existing complex site.

Clarify which `rhythmdo-com` top-level directories are public web assets, content, generated output, Quarto-local infrastructure, or Rhythmdo-local infrastructure.

The main goal is to make local-only implementation directories visually distinct by prefixing them with `.` and using a meaningful ownership prefix.

## Final Purpose

This cleanup is not only a Rhythmdo directory rename. It is a reference-project cleanup for Rhythmpress project creation and the future Rhythmpress plugin/package system.

The final target is to make CSS, JavaScript, filters, templates, LilyPond sources, helper scripts, and config patches modular, dependency-aware, and auditable.

This refactoring should help answer these implementation questions for Rhythmpress:

- which files belong in a minimal `rhythmpress project create` skeleton;
- which files should be optional plugin/package material;
- which files are public web assets versus local-only implementation files;
- which config snippets each plugin needs to patch into `_quarto.yml`;
- which generated files must never be treated as source or plugin-owned files.

## Naming Policy

- `.quarto-*`: Quarto-specific local infrastructure.
- `.project-*`: project-specific local/private infrastructure.
- `assets/`: public web assets.
- `attachments*/`: content-facing assets.
- plain content directories: rendered or author-facing site content.

Avoid project-branded hidden prefixes such as `.rhythmdo-*` or `.rhythmdo-com-*` for future Rhythmpress-generated projects. Prefer the static `.project-*` prefix so tooling and documentation can predict project-local infrastructure paths.

Future Rhythmpress-generated projects should follow the same boundary idea with Rhythmpress-owned names:

- `.rhythmpress-*`: Rhythmpress-managed local infrastructure.
- `.project-*`: project-specific local infrastructure.
- `assets/`: public plugin/runtime assets.

## Plugin-System Implications

The directory cleanup should expose future plugin boundaries. Candidate plugin/package units include:

- `toc-helper`
- `theme`
- `lilypond`
- `obsidian-images`
- `cookie-settings`
- `language-switcher`
- `social-cards`
- `cloudflare-router`

Each future plugin/package should declare:

- files it materializes;
- public assets it exposes;
- local-only infrastructure it owns;
- config patches it applies;
- dependencies on other plugins/packages;
- activation and deactivation behavior;
- generated files it must never own;
- verification steps.

The important policy is that CSS, JavaScript, filters, and config snippets should not be scattered as anonymous project files. They should be grouped into explicit, inspectable feature units.

## Directory Classification

| Directory | Current role | Public-facing? | Reorganization status |
| --- | --- | --- | --- |
| `assets/` | Public CSS/JS/runtime assets | yes | keep |
| `attachments/` | Public/content asset files | yes | keep |
| `attachments-src/` | Source/content-facing assets | partly | keep for now |
| `.quarto-filters/` | Quarto Lua filters, formerly `filters/` | no | renamed and verified |
| `.quarto-theme/` | Quarto theme SCSS, formerly `.assets/` | no | renamed and verified |
| `.project-lib/` | Rhythmdo local Python/tools/templates, formerly `lib/` | no | renamed and verified |
| `.project-templates/` | Preserved Obsidian authoring templates, formerly `templates/` | no | renamed and verified |
| `.project-translation/` | Translation working chunks/state, formerly `lib-translation/` | no | renamed and verified |
| `bin/` | Former local helper command wrappers | no | empty after helper move; no dedicated rename planned unless new commands are added |
| `.project-lilypond/` | LilyPond shared source files, formerly `common-ly/` | no, but rendered as resources | renamed and verified |
| `.quarto/` | Quarto generated state | no | keep ignored |
| `.site/`, `.site-*` | Rendered output | generated public output | keep ignored |
| `.venv/` | Python virtual environment | no | keep ignored |
| `.obsidian/` | Obsidian vault config | no | keep ignored |

## Planned Passes

### Pass 1: Quarto Local Infrastructure

- `filters/` -> `.quarto-filters/`
- `.assets/` -> `.quarto-theme/`

Expected source updates:

- `_quarto.yml`
- `_metadata-en.yml`
- `_metadata-ja.yml`
- `README.md`
- comments inside moved filter files if they mention old paths

Expected generated updates after `rhythmpress build`:

- `_quarto-en.yml`
- `_quarto-ja.yml`

Status: completed and verified at `20260507-041101`.

Verification notes:

- `rhythmpress build` completed successfully after the rename.
- The user ran `rhythmpress run-all` successfully in the normal local shell.
- `.site/`, `.site-en/`, and `.site-ja/` existed after the full run.
- Rendered output had no old `.assets/` references.
- Rendered output had no old bare `filters/` references.
- `_quarto-en.yml` and `_quarto-ja.yml` resolved the new `.quarto-filters/` and `.quarto-theme/` paths.
- Git status showed only the expected directory renames and source reference updates.

### Pass 2: Rhythmdo Local Library And Authoring Templates

- `lib/` -> `.project-lib/`
- `templates/` -> `.project-templates/`

Expected updates:

- `.project-lib/offbeat-count-join-en`
- `.obsidian/daily-notes.json`
- `.obsidian/zk-prefixer.json`
- `.obsidian/plugins/templater-obsidian/data.json`
- `.obsidian/plugins/periodic-notes/data.json`
- executable Python chunks importing `lib.groovespace`
- any remaining references found by `rg`

Notes:

- `lib/templates/toc.markdown` is retained for now, but the canonical active Rhythmpress package template is `rhythmpress/src/rhythmpress/templates/toc.markdown`.
- `bin/offbeat-count-join-en` was moved to `lib/offbeat-count-join-en` in `rhythmdo-com` commit `960c04d` at `20260507-041427`.
- `lib/offbeat-count-join-en` rebuilds `offbeat-count/master-en.md` from `lib-translation/en/` chunks and currently depends on `lib/offbeat-count-translation.py`.
- Top-level `templates/` was checked at `20260507-042130`. It is preserved Obsidian authoring material, not active Quarto or Rhythmpress runtime infrastructure.
- Active top-level `templates/` references were found only in Obsidian configuration: `.obsidian/daily-notes.json`, `.obsidian/zk-prefixer.json`, `.obsidian/plugins/templater-obsidian/data.json`, and `.obsidian/plugins/periodic-notes/data.json`.
- Top-level `templates/` is separate from `lib/templates/toc.markdown`; do not use the Obsidian finding to infer TOC template ownership.

Status: completed and verified at `20260507-043104`.

Verification notes:

- `lib/` was renamed to `.project-lib/`.
- `templates/` was renamed to `.project-templates/`.
- `.project-lib/offbeat-count-join-en` now points to `.project-lib/offbeat-count-translation.py`.
- Obsidian JSON config references were updated to `.project-templates/` for internal consistency.
- `.obsidian/` is a nested Git repository and is not tracked by the root `rhythmdo-com` repository; its config changes need separate handling if they should be committed.
- Executable Markdown Python chunks were updated from `from lib.groovespace import *` to import `groovespace` from `.project-lib/`.
- `bash -n .project-lib/offbeat-count-join-en` passed.
- Direct Python import verification loaded `.project-lib/groovespace.py`.
- The stale-reference scan found no remaining old path-style `lib/`, path-style `templates/`, `lib/templates`, or `from lib.groovespace` references outside excluded generated/site/plugin-bundle areas.
- `rhythmpress build` completed successfully after the rename.

### Pass 3: Translation Workspace

- `lib-translation/` -> `.project-translation/`

Expected updates:

- translation helper scripts
- skill/workflow documentation if present
- any hardcoded paths in progress notes

Status: completed and verified at `20260507-050221`.

Verification notes:

- `lib-translation/` was renamed to `.project-translation/`.
- `.project-lib/offbeat-count-join-en` now points to `.project-translation/`.
- The stale-reference scan found no remaining `lib-translation` references outside excluded generated/site/Obsidian areas.
- `bash -n .project-lib/offbeat-count-join-en` passed.
- `rhythmpress build` completed successfully after the rename.

### Pass 4: LilyPond Shared Sources

- `common-ly/` -> `.project-lilypond/`

This was high risk because `common-ly/` was heavily referenced from:

- `_quarto.yml` resources
- `metadata.lilypond-preamble`
- LilyPond `\include` statements
- `offbeat-count/master-*.md`
- `.project-translation/` chunks

Status: completed and verified at `20260507-051009`.

Verification notes:

- `common-ly/` was renamed to `.project-lilypond/`.
- `_quarto.yml` resources now list `.project-lilypond/*.ly` and `.project-lilypond/shared/*.ly`.
- `metadata.lilypond-preamble` now points to `.project-lilypond/lilypond-preamble.ly`.
- LilyPond `\include` paths inside shared `.ly` files now point to `.project-lilypond/`.
- `offbeat-count/master-en.md`, `offbeat-count/master-ja.md`, and affected `.project-translation/` chunks now reference `.project-lilypond/shared/*.ly`.
- The stale-reference scan found no remaining `common-ly` or `.project-common-ly` references in `rhythmdo-com` outside excluded generated/site/Obsidian areas.
- `bash -n .project-lib/offbeat-count-join-en` passed.
- `rhythmpress build` completed successfully after the rename.

## Verification Commands

After each pass:

```sh
git -C /Users/ats/rhythmdo-com status --short
rg -n "filters/|\\.assets/|lib/|templates/|lib-translation/|bin/|common-ly/|\\.project-common-ly/" /Users/ats/rhythmdo-com \
  --glob '!*.html' \
  --glob '!.site*/**' \
  --glob '!.quarto/**' \
  --glob '!.venv/**' \
  --glob '!.git/**' \
  --glob '!**/.obsidian/**'
```

For Quarto path changes:

```sh
PATH="/Users/ats/rhythmdo-com/.venv/bin:$PATH" RHYTHMPRESS_ROOT=/Users/ats/rhythmdo-com /Users/ats/rhythmdo-com/.venv/bin/rhythmpress build
```

Full render currently needs care because local sandboxed Quarto render failed with:

```text
sysctl: sysctl fmt -1 1024 1: Operation not permitted
quarto script failed: unrecognized architecture
```

Use unsandboxed/local shell execution if full Quarto render verification is required.

## Current Status

- Worktree was clean before creating this tracker.
- Pass 1, Quarto local infrastructure, has been applied and verified.
- `bin/offbeat-count-join-en` was moved into `lib/` in `rhythmdo-com` commit `960c04d`; `bin/` no longer needs its own rename pass unless new helper commands are added.
- Top-level `templates/` has been confirmed as preserved Obsidian authoring material, not active build/runtime infrastructure.
- Pass 2, Rhythmdo local library and authoring templates, has been applied and verified.
- Pass 3, translation workspace, has been applied and verified.
- Pass 4, LilyPond shared sources, has been applied and verified with `.project-lilypond/`.
- Recommended next action: commit the root `rhythmdo-com` Pass 4 rename, then commit this Rhythmpress tracker/spec update.
- The directory rename work is also being used to identify future Rhythmpress plugin/package boundaries.
