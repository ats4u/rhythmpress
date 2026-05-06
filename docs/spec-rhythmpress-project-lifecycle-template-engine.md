# Project Lifecycle Template Engine Specification

Created: 20260506-123604

Status: draft implementation specification.

## Purpose

Implement a project lifecycle command family for Rhythmpress project skeleton generation and future language management.

Related specifications:

- [Scriptlet Dependency Map](spec-rhythmpress-project-scriptlet-dependency-map.md)
- [Plugin Feature Packs](spec-rhythmpress-project-plugin-feature-packs.md)
- [Plugin Package Format](spec-rhythmpress-project-plugin-package-format.md)

Primary command for the first implementation:

```sh
rhythmpress project create my-site --title "My Site" --site-url "https://example.com/" --langs en,ja --default-lang en
```

The command creates source-layer project files. It does not render the site and does not create generated Rhythmpress, Quarto, or final artifact files.

## Command Taxonomy

Planned project lifecycle commands:

```sh
rhythmpress project create <project-dir> [options]
rhythmpress project add-language <lang> [options]
rhythmpress project remove-language <lang> [options]
rhythmpress project activate-plugin <package-or-feature> [options]
rhythmpress project deactivate-plugin <package-or-feature> [options]
rhythmpress project sync-plugins [options]
rhythmpress project check [options]
```

Existing page scaffold command remains separate:

```sh
rhythmpress create-page <page-dir> --lang en
```

Commands not planned:

```sh
rhythmpress create-project
rhythmpress create page
```

Rationale:

- Project creation, language lifecycle, project manifest inspection, and future project update behavior belong to one project-level command family.
- Page creation is already covered by `rhythmpress create-page`.
- `project create` should not absorb page creation behavior beyond creating the initial starter article required by a new project.

## First Implementation Scope

Implement only:

```sh
rhythmpress project create
```

The first patch must include:

- CLI argument parsing under `src/rhythmpress/scripts/rhythmpress_project.py`.
- Library implementation in a project lifecycle module, for example `src/rhythmpress/project_lifecycle.py`.
- Parameter normalization and validation.
- Deterministic source file planning.
- `--dry-run` reporting.
- Safe apply behavior.
- Constrained `--force` behavior.
- `.rhythmpress-template.json` manifest writing.
- Verification script for the core creation behavior.

Future commands are specified here, but not implemented in the first patch:

- `project add-language`
- `project remove-language`
- `project activate-plugin`
- `project deactivate-plugin`
- `project sync-plugins`
- `project check`

## Non-Goals

The first implementation must not:

- Create `_quarto-<lang>.yml`.
- Create `_sidebar-<lang>.generated.conf`.
- Create `_sidebar-<lang>.generated.yml`.
- Create `_sidebar-<lang>.generated.md`.
- Create `lang-switcher.generated.mjs`.
- Create generated article pages such as `<article>/<lang>/index.qmd`.
- Create `.site`, `.site-*`, `.quarto`, or rendered output.
- Run `rhythmpress build`, `render-all`, `assemble`, or `finalize`.
- Create Git commits.
- Implement Git-date fallback behavior.
- Implement LilyPond, GitHub Actions, social cards, Cloudflare router, assets, or sidebar hook packs.
- Replace or remove `rhythmpress create-page`.

## Runtime Prerequisites

Project creation itself should need only the Python package runtime.

Full lifecycle verification requires:

- `rhythmpress` command installed or otherwise executable in the test environment.
- Runtime Python used by `rhythmpress` has PyYAML available.
- Git available for current strict `cdate` and `mdate` behavior.
- `yq` v4 available for `render-sidebar`.
- Quarto CLI available for `render-all`.
- `rsync` available for `assemble`.
- `RHYTHMPRESS_ROOT` set before sidebar rendering, normally through:

```sh
eval "$(rhythmpress eval)"
```

Local verification in a source checkout should not assume `rhythmpress` is already on `PATH`. If the package is not installed, use an editable install or invoke the dispatcher module with the same Python environment that has package dependencies installed. The verification script should fail with a clear message if PyYAML or the command runtime is missing.

## Project Create CLI

Required:

```sh
rhythmpress project create <project-dir> --title <title>
```

Recommended for production projects:

```sh
--site-url https://example.com/
```

Core options:

| Option | Default | Notes |
|---|---|---|
| `<project-dir>` | required | Target project directory. Missing or empty by default. |
| `--title` | required | Project/site title. |
| `--site-url` | unset | Absolute URL recommended. Normalize trailing slash. |
| `--langs` | `en` | Comma-separated language IDs. |
| `--default-lang` | first language | Must be included in `--langs`. |
| `--author` | empty | Stored in language metadata when provided. |
| `--description` | generic starter text | Stored in language metadata. |
| `--copyright` | empty | Stored in language metadata when provided. |
| `--starter-article` | `about` | Starter article directory. |
| `--starter-title` | `About` | Starter master title. |
| `--starter-mode` | `split` | `copy` or `split`. |
| `--output-dir` | `.site` | Base Quarto output dir. |
| `--with-404` / `--no-404` | with 404 | 404 source pages are recommended but not lifecycle-minimum. |
| `--with-language-switcher` / `--no-language-switcher` | auto | Auto means enabled for more than one language. |
| `--dry-run` | false | Print planned actions and write nothing. |
| `--force` | false | Allow constrained writes in non-empty target dirs. |

## Validation Rules

Target directory:

- Missing target is valid.
- Existing empty target directory is valid.
- Existing non-empty target directory is refused unless `--force` is set.
- Existing file at the target path is blocked.
- Symlink target is blocked.

Language IDs:

- Normalize by stripping whitespace, replacing `_` with `-`, and lowercasing.
- Reject empty values.
- Reject duplicates after normalization.
- Reject path separators.
- Reject whitespace.
- Reject leading dots.
- Reject shell-special path characters.
- IDs must be safe in:
  - `master-<lang>.qmd`
  - `_metadata-<lang>.yml`
  - `_sidebar-<lang>.before.yml`
  - `<lang>/index.qmd`
  - generated `_quarto-<lang>.yml` later
- Use `to_bcp47_lang_tag()` when a Quarto BCP 47 language tag is needed.

Default language:

- Normalize the same way as `--langs`.
- Must be included in the normalized language list.

Starter article:

- Relative path only.
- No absolute path.
- No `..`.
- No leading dot segment.
- No whitespace.
- No shell-special path characters.

Site URL:

- If provided, must be an absolute URL.
- Normalize to include a trailing slash.

Output directory:

- Relative path only.
- Must not be `.`.
- Must not contain parent traversal.

## Source Of Truth

Project lifecycle commands must treat these files as separate sources of truth:

| Layer | File or state | Purpose |
|---|---|---|
| Desired state | `_quarto.yml` `rhythmpress.project` | User-editable project configuration and feature intent. |
| Ownership state | `.rhythmpress-template.json` | Internal list of template-managed files and content hashes. |
| Materialized state | actual files on disk | What currently exists in the project. |
| Article targets | `_rhythmpress.conf` | Article directory list consumed by current build commands. |

Precedence:

- User intent comes from `_quarto.yml` `rhythmpress.project`.
- Safe overwrite decisions come from `.rhythmpress-template.json`.
- Build targets come from `_rhythmpress.conf`.
- `project check` compares desired state, ownership state, and materialized state; it should not silently rewrite files.

Important constraint:

- `_rhythmpress.conf` must remain an article-target list only for now.
- Do not add metadata lines such as `default_lang=en` to `_rhythmpress.conf`.
- Current `rhythmpress build`, `sidebar-confs`, and `sidebar-langs` treat non-comment lines as directories.

## Source Tree Created By Project Create

One-language core source tree:

```text
_quarto.yml
_rhythmpress.conf
_metadata-<lang>.yml
_sidebar-<lang>.before.yml
_sidebar-<lang>.after.yml
.gitignore
.quartoignore
.rhythmpress-template.json
index.qmd
<lang>/index.qmd
<starter-article>/.article_dir
<starter-article>/.gitignore
<starter-article>/master-<lang>.qmd
```

Multilingual expansion adds, for each additional language:

```text
_metadata-<lang>.yml
_sidebar-<lang>.before.yml
_sidebar-<lang>.after.yml
<lang>/index.qmd
<starter-article>/master-<lang>.qmd
```

Default 404 pack, when enabled:

```text
404.qmd
<lang>/404.qmd
```

Files that must be absent immediately after project creation:

```text
_quarto-<lang>.yml
_sidebar-<lang>.generated.conf
_sidebar-<lang>.generated.yml
_sidebar-<lang>.generated.md
lang-switcher.generated.mjs
.site
.site-<lang>
.quarto
<starter-article>/<lang>/index.qmd
<starter-article>/_sidebar-<lang>.yml
```

## Directory Ownership Policy

Project skeletons and plugin packages must make directory ownership visible from the path name.

Default directory classes:

| Path pattern | Ownership | Public-facing? | Policy |
| --- | --- | --- | --- |
| `assets/` | Public web/runtime assets | yes | Use for browser-loaded CSS, JavaScript, images, and other deployed assets. |
| `attachments*/` | Content-facing assets | yes or source-facing | Use for article/page media and durable content assets. |
| `.quarto-*` | Quarto-local infrastructure | no | Use for Quarto-specific source support such as filters, theme source, or Quarto helper inputs. |
| `.rhythmpress-*` | Rhythmpress-managed local infrastructure | no | Use for Rhythmpress-owned manifests, packages, caches, and implementation state. |
| `.project-*` | Project-specific local infrastructure | no | Use for site-specific private helpers that are not Rhythmpress core and are not public web paths. |
| `.site`, `.site-*`, `.quarto` | Generated output/state | output only | Never create as source template content and never package as source. |

`project create` should prefer predictable static prefixes over project-branded hidden prefixes. Use `.project-*`, not `.<project-name>-*`, for project-specific local infrastructure so tools can discover and reason about local-private directories without site-specific naming rules.

Examples:

```text
.quarto-filters/
.quarto-theme/
.rhythmpress-packages/
.project-lib/
.project-templates/
assets/
attachments/
```

The directory policy is also a plugin boundary policy. CSS, JavaScript, filters, templates, helper scripts, LilyPond sources, and config snippets must belong to explicit core/plugin packages or to explicit project-local directories. They must not be scattered as anonymous top-level files without ownership.

## File Responsibilities

`_quarto.yml`:

- Owns base Quarto project settings.
- Owns base website settings.
- Owns base output directory.
- Owns user-editable Rhythmpress project desired state under `rhythmpress.project`.
- Includes only source-level configuration.
- Does not include generated profile YAML.
- Must render root QMD pages such as `index.qmd` and `404.qmd`.
- Must exclude master files from direct Quarto rendering.

Minimum required shape:

```yml
project:
  title: "<title>"
  type: website
  output-dir: ".site"
  render:
    - "/*.qmd"
    - "!**/master*.md"
    - "!**/master*.qmd"
    - "!drafts/**"

website:
  site-url: "<site-url>"
  page-navigation: true

rhythmpress:
  project:
    manifest: ".rhythmpress-template.json"
    languages:
      - "<lang>"
    default-language: "<default-lang>"
    starter-article: "<starter-article>"
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

`rhythmpress.project` is the user-facing desired-state skeleton. It should contain explicit default values so users can discover what is configurable by reading `_quarto.yml`.

`.rhythmpress-template.json` remains the internal ownership manifest. It records what the generator wrote and whether managed files can be safely repaired; it should not be the primary user editing surface.

Feature-pack names and migration boundaries are defined in the plugin feature-pack specification. `project create` must install only core files plus selected feature packs. It must not copy `rhythmdo-com` `filters/`, `assets/`, `.assets/`, `.project-lilypond/` formerly `common-ly/`, `lib/`, `lib-translation/`, `bin/`, or `templates/` wholesale.

Feature packs should be materialized from plugin packages. `project create` may materialize built-in core/default packages for a new skeleton. Later plugin lifecycle commands own activation, deactivation, synchronization, and drift checks. `rhythmpress build` must not enable new packages by itself; if build-time plugin sync is introduced, it may only materialize packages already enabled in project desired state and must use the same conflict rules as `project sync-plugins`.

If the language switcher is enabled, `_quarto.yml` must also include the generated runtime JS reference. `project create` writes only the source reference; `rhythmpress build` later writes `lang-switcher.generated.mjs`.

Example:

```yml
website:
  navbar:
    right:
      - text: "<span id='rhythmpress-lang-switcher-slot'></span>"
        href: "#"
format:
  html:
    include-in-header:
      - text: |
          <script async type="module" src="/lang-switcher.generated.mjs"></script>
```

The default skeleton should also include a visible TOC helper. The helper should be based on the useful behavior of `toc-ul.mjs`, but cleaned and named as a Rhythmpress-owned asset, for example `assets/rhythmpress-toc.mjs`. Starter content should include a `#toc` target so new projects immediately show that the helper is working. `toc-generator.mjs` should not be installed as-is because it is console/developer output, not a visible starter-project feature.

`_rhythmpress.conf`:

- Owns the article target list.
- Minimum content is one line naming the starter article directory.
- Must not contain project metadata lines until existing command readers support them.

`_metadata-<lang>.yml`:

- Owns language-specific site metadata.
- Stores title, description, author, footer defaults, sidebar defaults, and presentation defaults.

Minimum required shape:

```yml
author: "<author>"
website:
  title: "<title>"
  description: "<description>"
  page-footer:
    center: "<copyright>"
  sidebar:
    style: docked
    collapse-level: 1
format:
  html:
    toc: true
```

The exact visual defaults can be adjusted during implementation, but the file must be a YAML mapping and must be valid input to `rhythmpress quarto-profile`.

`_sidebar-<lang>.before.yml`:

- Minimum content:

```yml
website:
  sidebar:
    contents: []
```

`_sidebar-<lang>.after.yml`:

- Minimum content:

```yml
{}
```

`index.qmd`:

- Root authored entry page.
- Calls the runtime root-entry helper with `_rhythmpress.conf` and default language.

`<lang>/index.qmd`:

- Authored language home page.
- Calls the global navigation helper with `_rhythmpress.conf` and current language.

`404.qmd`:

- Root authored runtime 404 entry page.
- Calls the runtime 404 helper.

`<lang>/404.qmd`:

- Language-specific authored 404 page.

`<starter-article>/master-<lang>.qmd`:

- Authored starter content.
- Includes `title`, explicit starter date metadata, and `rhythmpress-preproc`.
- Uses `split` by default to exercise section page generation and sidebar wiring.

`<starter-article>/.article_dir`:

- Empty sentinel required by `preproc-clean`.

`<starter-article>/.gitignore`:

- Tracks masters and sentinels while ignoring generated article output.

## QMD Template Contracts

Root `index.qmd` must be executable and must emit runtime routing HTML as ASIS output.

Minimum shape:

````qmd
---
title: "<title>"
format: html
execute:
  enabled: true
  echo: false
  output: true
  eval: true
  cache: false
title-block: false
---

```{python}
#| output: asis
from rhythmpress import rhythmpress

out = rhythmpress.create_runtime_root_entry(
    input_conf="./_rhythmpress.conf",
    current_lang="<default-lang>",
    strict=False,
)
print(out)
```
````

Language home page `<lang>/index.qmd` must be executable and must emit generated navigation as ASIS output.

Minimum shape:

````qmd
---
title: "<localized title>"
format: html
execute:
  enabled: true
  echo: false
  output: true
  eval: true
  cache: false
title-block: false
---

```{python}
#| output: asis
from rhythmpress import rhythmpress

out = rhythmpress.create_global_navigation(
    "../_rhythmpress.conf",
    "<lang>",
    strict=False,
)
print(out)
```
````

Root `404.qmd` must be executable and must emit runtime 404 routing HTML as ASIS output.

Minimum shape:

````qmd
---
title: "Page Not Found"
format: html
execute:
  enabled: true
  echo: false
  output: true
  eval: true
  cache: false
title-block: false
toc: false
metadata:
  robots: "noindex,nofollow"
---

The page was not found.

```{python}
#| output: asis
from rhythmpress import rhythmpress

out = rhythmpress.create_runtime_404_entry(
    input_conf="./_rhythmpress.conf",
    current_lang="<default-lang>",
    strict=False,
)
print(out)
```
````

Language 404 page `<lang>/404.qmd` is an authored page and does not need a runtime helper.

Minimum shape:

```qmd
---
title: "Page Not Found"
format: html
title-block: false
toc: false
metadata:
  robots: "noindex,nofollow"
---

The page was not found.
```

Starter master `<starter-article>/master-<lang>.qmd` must contain an H2 when `--starter-mode split` is used, because split mode produces section pages from H2 sections.

Minimum split-mode shape:

```qmd
---
title: "<starter-title>"
created: "<YYYYMMDD-HHMMSS>"
rhythmpress-preproc: split
rhythmpress-preproc-args: []
---

Introductory text for the generated project.

## First Page {#first-page}

Starter content.
```

Current preprocessing ignores `created` for `cdate` and `mdate`; the field exists for future fallback behavior.

## Root Ignore Policy

Root `.gitignore` must ignore generated and local artifacts without hiding authored sidebar source files.

Minimum patterns:

```gitignore
/.site
/.site-*/
/.quarto/
/_freeze/
/lang-switcher.generated.mjs
/_quarto-*.yml
/_sidebar-*.generated.conf
/_sidebar-*.generated.yml
/_sidebar-*.generated.md
.DS_Store
.venv/
__pycache__/
```

Article `.gitignore` minimum:

```gitignore
*
!*/
!.article_dir
!.gitignore
!master-*.qmd
!master-*.md
!attachments*/
!attachments*/**
!attachments-src*/
!attachments-src*/**
```

## Write Planning

Project creation must be planned before any write happens.

Planner actions:

- `create`: planned path does not exist.
- `keep`: existing file already matches planned content.
- `update-managed`: existing file is manifest-owned and unmodified since the last template write.
- `conflict`: existing file differs and cannot be safely overwritten.
- `blocked`: path is unsafe, wrong type, symlink, directory/file collision, or target policy violation.
- `skip`: planned feature or output is intentionally omitted.

Default behavior:

- Refuse non-empty target directories before writing.
- Create only planned source files.
- Never delete unknown files.
- Never write generated artifacts.

`--dry-run` behavior:

- Build the same plan as a real run.
- Print every planned action.
- Print summary counts.
- Create no directories.
- Write no files.
- Update no manifest.

Minimum dry-run output contract:

```text
[project create] target=<project-dir>
[create] _quarto.yml
[create] _rhythmpress.conf
[create] _metadata-en.yml
[skip] _quarto-en.yml (generated)
[summary] create=<n> keep=<n> update-managed=<n> conflict=<n> blocked=<n> skip=<n>
```

Tests may assert action labels, paths, and summary counts. Human-readable wording after the path is allowed to evolve.

`--force` behavior:

- Permit non-empty target directories.
- Create missing planned files.
- Keep identical files.
- Overwrite only manifest-owned files that are still unmodified.
- Refuse user-modified managed files.
- Refuse unmanaged conflicting files.
- Preserve unknown files.
- Never delete generated artifacts.

## Manifest

Project creation writes `.rhythmpress-template.json` after all source writes succeed.

The manifest records ownership state. User-editable project desired state lives in `_quarto.yml` under `rhythmpress.project`.

Manifest schema v1:

```json
{
  "schema": 1,
  "generator": "rhythmpress project create",
  "rhythmpress_version": "0.1.2",
  "created_at": "YYYYMMDD-HHMMSS",
  "parameters": {
    "title": "My Site",
    "site_url": "https://example.com/",
    "langs": ["en", "ja"],
    "default_lang": "en",
    "starter_article": "about",
    "starter_mode": "split"
  },
  "feature_packs": ["core", "404", "language-switcher"],
  "files": [
    {
      "path": "_quarto.yml",
      "kind": "source",
      "feature": "core",
      "sha256": "<hex>"
    }
  ]
}
```

Manifest rules:

- Manifest is source-management metadata, not a generated artifact.
- Manifest is internal generator state, not the main user customization surface.
- `_quarto.yml` `rhythmpress.project` is the user-editable desired-state surface.
- Generated artifacts must not be listed as managed files.
- Hashes are computed from exact bytes written.
- Manifest is written only after all planned files are successfully written.
- Future project lifecycle commands must use the manifest as the source of truth for managed files.

## Exit Codes

`rhythmpress project create` should return:

| Code | Meaning |
|---:|---|
| 0 | Success, including successful dry-run. |
| 1 | Runtime error or unexpected failure. |
| 2 | Usage, validation, conflict, or blocked-path failure. |
| 127 | Required external command missing, if a future project subcommand needs one. |

The first `project create` implementation should not require external commands beyond the Python runtime, so `127` is reserved for future lifecycle operations or verification helpers.

## Project Language Lifecycle

Future `project add-language <lang>`:

- Adds project-level language support.
- Creates `_metadata-<lang>.yml`.
- Creates `_sidebar-<lang>.before.yml`.
- Creates `_sidebar-<lang>.after.yml`.
- Creates `<lang>/index.qmd`.
- Creates `<lang>/404.qmd` when the 404 pack is active.
- Updates the manifest.
- Does not automatically create translated article masters for all existing articles.

Future article master creation for a new language must be explicit. It may later be supported by a separate option or by existing page-level workflow.

Future `project remove-language <lang>`:

- Defaults to dry-run behavior.
- Reports affected source files, generated artifacts, language directories, and article masters.
- Must treat translated masters as authored user content.
- Must not delete authored translations without a strong explicit confirmation policy.
- Must update the manifest only after safe writes/deletions succeed.

Future `project check`:

- Validates manifest integrity.
- Reports missing managed files.
- Reports modified managed files.
- Reports generated artifacts that are present but untracked by the manifest.
- Compares `_quarto.yml` `rhythmpress.project` desired state with materialized files and manifest state.
- Reports language config drift.

## Build-Time Generated Artifact Note

`project create` must not create `lang-switcher.generated.mjs`.

However, current `rhythmpress build` runs `render-lang-switcher-js` when `_rhythmpress.conf` exists. Therefore `lang-switcher.generated.mjs` is expected after build, including in a single-language project, unless the build command changes later.

## Git-Date Policy

Current Rhythmpress preprocessing requires Git history for `cdate` and `mdate`.

First implementation policy:

- `project create` does not create Git commits.
- Starter masters include explicit date metadata for future fallback use.
- Until fallback date behavior is implemented, a project may need:

```sh
git init
git add .
git commit -m "Initialize Rhythmpress project"
```

before `rhythmpress build` can preprocess starter masters.

Future fallback policy:

- Preserve strict Git dates for existing projects by default.
- Enable fallback only through narrow generated-project metadata or explicit project setting.
- Prefer Git dates when available.
- If Git dates are unavailable for generated starter masters, use starter front matter or generator timestamp.
- Emit a visible warning when fallback dates are used.
- After the first commit, Git dates should take over automatically.

## Implementation Layout

First patch files:

```text
src/rhythmpress/scripts/rhythmpress_project.py
src/rhythmpress/project_lifecycle.py
src/rhythmpress/scripts/verify_project_create.py
docs/commands.md
docs/progress-tracker-for-template-engine.md
```

Command script responsibilities:

- Parse grouped command syntax.
- Dispatch `project create`.
- Print usage for unknown project subcommands.
- Return appropriate exit codes.

Library responsibilities:

- Data model.
- Validation.
- Rendering.
- Write planning.
- Manifest handling.
- Apply behavior.
- Dry-run reporting data.

Do not put the main implementation in `rhythmpress.py`.

## Implementation Sequence

Build in this order:

1. Data model and render plan only.
   - Normalize inputs.
   - Build `ProjectSpec`.
   - Build `PlannedFile` entries.
   - Do not write files yet.
2. Dry-run output.
   - Add action classification.
   - Print planned actions and summary counts.
   - Verify dry-run creates no target directory.
3. Apply without `--force`.
   - Allow missing or empty target directories.
   - Write planned source files.
   - Refuse existing non-empty target directories.
4. Manifest write.
   - Hash written bytes.
   - Write `.rhythmpress-template.json` only after all source writes succeed.
5. `--force` and conflict checks.
   - Preserve unknown files.
   - Repair missing managed files.
   - Refuse changed managed files and unmanaged collisions.
6. Verification script.
   - Cover dry-run, source tree, generated-artifact exclusion, non-empty target refusal, conflict handling, and manifest contents.
7. Command reference docs.
   - Add `rhythmpress project create` to `docs/commands.md`.
8. Lifecycle fixture proof.
   - Separate from `project create` implementation.
   - Requires installed command runtime, Git commit, `yq`, Quarto, and `rsync`.

First patch cut line:

- Implement core `rhythmpress project create` only.
- Do not implement `project add-language`.
- Do not implement `project remove-language`.
- Do not implement `project check`.
- Do not implement `project activate-plugin`.
- Do not implement `project deactivate-plugin`.
- Do not implement `project sync-plugins`.
- Do not run lifecycle commands from inside `project create`.
- Do not implement Git-date fallback.
- Do not implement optional feature packs beyond source stubs already specified for default core behavior.
- Keep optional feature-pack design aligned with `docs/spec-rhythmpress-project-plugin-feature-packs.md` before implementing those packs.
- Keep plugin package implementation aligned with `docs/spec-rhythmpress-project-plugin-package-format.md`.
- Treat the default TOC helper as core starter behavior, not as an optional pack.

## First Patch Contract

Updated: 20260506-182447

The first implementation patch must stay limited to the minimum project generator needed to create a working source-layer starter project.

Implement in the first patch:

- Add `rhythmpress project create`.
- Generate starter project source files only.
- Generate `_quarto.yml` with a visible `rhythmpress:` skeleton that exposes default user-editable values.
- Generate language-aware source skeletons from `--langs` and `--default-lang`.
- Generate starter article masters and article sentinels.
- Generate core default TOC helper assets as starter behavior.
- Generate `.rhythmpress-template.json` ownership manifest after successful writes.
- Implement dry-run, default non-empty target refusal, `--force` repair behavior, and conflict checks for changed managed files.
- Add focused verification for dry-run, created source tree, generated-artifact exclusion, manifest contents, non-empty target refusal, and conflict handling.
- Update command reference documentation for the implemented command behavior.

Defer from the first patch:

- Plugin package manager commands and registry behavior.
- `rhythmpress project activate-plugin`.
- `rhythmpress project deactivate-plugin`.
- `rhythmpress project sync-plugins`.
- Build-time package activation or package sync.
- Tar archive package input.
- CSS feature-pack migration.
- Broad migration of current Rhythmdo CSS, JavaScript, filters, or site-specific configuration.
- Language add/remove commands.
- Lifecycle proof that depends on Quarto, `yq`, `rsync`, Git history, and the installed command runtime.

## Easy To Forget Implementation Constraints

Updated: 20260506-182041

- The first implementation patch is core `rhythmpress project create` only.
- The default TOC helper is core starter behavior because it is expected in a new project by default.
- Package activation, deactivation, sync, update, registry, and tar archive input are future work.
- `rhythmpress build` must not enable packages. It may only verify or sync already-enabled packages after that behavior is explicitly implemented.
- Do not copy `rhythmdo-com` directories wholesale. Treat `rhythmdo-com` as an audit source, not as a package source tree.
- Do not template generated artifacts such as `_quarto-<lang>.yml`, generated sidebars, generated language switchers, render outputs, cache directories, or social images.
- `_rhythmpress.conf` remains an article-target list only. Do not add language, feature, or project metadata to it.
- CSS, JavaScript, filters, and configuration must be owned by explicit core/plugin packages so dependency boundaries stay traceable.
- Each package-owned file must have one owner in the manifest. Shared behavior belongs in a core helper or common package, not duplicated package files.
- Keep CSS split by feature ownership. Do not reintroduce a global copy of the current Rhythmdo CSS bundle as the new default theme.

## Verification

Verification script must cover:

- `--dry-run` creates no target directory.
- One-language project creates expected source files.
- Multilingual project creates expected language source files.
- Generated artifacts are absent immediately after creation.
- Default create refuses a non-empty target.
- `--force` preserves unknown files.
- Changed managed files become conflicts.
- Manifest exists after creation.
- Manifest contains only source files.
- Manifest excludes generated artifacts.

Verification environment checks must report:

- whether `rhythmpress` is available on `PATH`;
- whether local module invocation is available;
- whether PyYAML is importable in the command runtime;
- whether `yq`, `quarto`, `rsync`, and Git are available for full lifecycle proof.

Manual lifecycle verification, after project creation and initial Git commit:

```sh
eval "$(rhythmpress eval)"
rhythmpress build --dry-run
rhythmpress build --skip-clean
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize --output-dir .site --site-url https://example.test/ --skip-social-cards
```

Do not use `rhythmpress finalize --skip-sitemap --skip-social-cards` as the minimal smoke test. Current `finalize` treats "all steps skipped" as a validation error.

Expected generated files after build:

```text
_quarto-<lang>.yml
_sidebar-<lang>.generated.conf
_sidebar-<lang>.generated.yml
_sidebar-<lang>.generated.md
<starter-article>/_sidebar-<lang>.yml
<starter-article>/<lang>/index.qmd
<starter-article>/<section-slug>/<lang>/index.qmd
```

## Implementation Traps

Do not forget these constraints:

- Root render rules:
  - `quarto-profile` adds `index.md` to generated profiles, not root `index.qmd`.
  - Base `_quarto.yml` must render root `/*.qmd` or root `index.qmd` and `404.qmd` may be missed.
- Runtime entry pages:
  - Root `index.qmd` and root `404.qmd` need executable Python chunks with `#| output: asis`.
  - Plain Markdown links are not equivalent to runtime helper output.
- `RHYTHMPRESS_ROOT`:
  - `render-sidebar` requires it.
  - Lifecycle verification must run `eval "$(rhythmpress eval)"` from the project root.
- `finalize`:
  - `finalize --skip-social-cards` still runs sitemap.
  - `finalize --skip-sitemap --skip-social-cards` exits with validation error because all steps are skipped.
  - Pass `--site-url` in lifecycle verification.
- Python environment:
  - The `rhythmpress` runtime Python must have PyYAML.
  - System `python3` and the installed `rhythmpress` command may not share the same environment.
- Sidebar discovery:
  - `sidebar-confs` discovers article `_sidebar-<lang>.yml` files only after preprocessing creates them.
  - The files must be absent after `project create` and present after `build`.
- Sidebar YAML validity:
  - `_sidebar-<lang>.before.yml` and `_sidebar-<lang>.after.yml` must be valid YAML mappings.
  - `quarto-profile` expects generated sidebar YAML to contain `website.sidebar`.
- Split mode:
  - Split preprocessing creates section pages only from H2 headings.
  - Starter masters using `split` must include at least one H2.
- Git dates:
  - Current preprocessing fails for untracked or uncommitted masters.
  - `created` front matter is not currently enough for `cdate` and `mdate`.
- Ignore files:
  - Do not use broad root `_sidebar-*.yml` ignore patterns that hide authored `_sidebar-<lang>.before.yml` and `.after.yml`.
  - Article `.gitignore` must keep `.article_dir`, `.gitignore`, and `master-*` visible.
- `_rhythmpress.conf`:
  - Current readers treat non-comment lines as article directories.
  - Do not put metadata such as `default_lang=en` there.
- Language switcher:
  - `project create` must not write `lang-switcher.generated.mjs`.
  - Current `rhythmpress build` will generate it when `_rhythmpress.conf` exists.
- `--force`:
  - Must not mean "replace the directory."
  - It can repair only missing or unchanged manifest-owned files.
  - It must preserve unknown files and refuse user-modified managed files.
- Manifest timing:
  - Write `.rhythmpress-template.json` only after all source writes succeed.
  - Do not leave a manifest that claims ownership of files that failed to write.
- Desired state vs ownership state:
  - `_quarto.yml` `rhythmpress.project` is user-editable desired state.
  - `.rhythmpress-template.json` is internal ownership state.
  - Do not make the manifest the only place where user-visible defaults appear.

## Acceptance Criteria

The first implementation is acceptable when:

- `rhythmpress project create --help` works.
- `rhythmpress project create` creates the core source skeleton.
- `rhythmpress list` includes `project`.
- Dry-run mode performs no writes.
- Generated artifacts are not created by project creation.
- Manifest ownership is written and used by `--force`.
- Verification script passes.
- Documentation records the strict Git-date limitation.
