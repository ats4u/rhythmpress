# Command reference

Rhythmpress ships as a single command, `rhythmpress`, which dispatches to subcommands implemented as local scripts.

Two important usability details:

1) **Command name normalization**  
`rhythmpress` accepts `kebab-case`, `snake_case`, and even accidental spaces. These all resolve to the same thing:

- `rhythmpress preproc-clean`
- `rhythmpress preproc_clean`
- `rhythmpress "preproc clean"`

2) **No implicit `cd`**  
The dispatcher does **not** change directories for you. Run commands from the project root unless the command explicitly supports `--chdir`.

If you want a quick list of what is available in your installed version:

```bash
rhythmpress list
````

---

## Common exit behavior

Most commands follow this rough pattern (but don’t treat it as a strict contract unless explicitly documented by that command):

* `0` success
* `1` runtime error
* `2` usage / validation error
* `127` missing external tool (common when a shell script expects a tool like `yq`)

---

## `rhythmpress list`

Print the available local subcommands installed with the package.

```bash
rhythmpress list
```

---

## `rhythmpress eval`

Emit shell code that activates the project environment variables (and prompt decoration). This is meant to be used with `eval`.

Typical usage (POSIX shells like bash/zsh):

```bash
eval "$(rhythmpress eval)"
```

Options:

* `-s` output Bourne/POSIX shell code (default)
* `-c` output `csh/tcsh` code
* `-k` output deactivation code (instead of activation)
* `-f` force re-activation (ignore idempotency guard)

Examples:

```bash
# activate (sh)
eval "$(rhythmpress eval)"

# deactivate (sh)
eval "$(rhythmpress eval -k)"

# force re-apply (sh)
eval "$(rhythmpress eval -f)"

# csh/tcsh style
eval `rhythmpress eval -c`
```

What it sets (at minimum):

* `RHYTHMPRESS_ROOT` = current working directory at the time you run it
* `RHYTHMPRESS_TITLE` (if found from `_quarto.yml`)
* prepends `$RHYTHMPRESS_ROOT/bin` to `PATH` (only once)
* defines `rhythmpress_deactivate()` (sh only)

Note: some older scripts/messages may say `rhythmpress env`; in this codebase the command is `rhythmpress eval`.

---

## `rhythmpress create-page`

Create an article directory scaffold:

* `<dir>/.article_dir` (clean sentinel)
* `<dir>/.gitignore`
* `<dir>/master-<lang>.qmd` (default lang: `ja`)

Usage:

```bash
rhythmpress create-page <directory-name> [--lang ja]
```

Example:

```bash
rhythmpress create-page hypergroove/the-four-principles-of-groove --lang en
```

Exit behavior:

* `0` success
* `1` runtime failure
* `2` usage error

---

## `rhythmpress preproc`

Front-matter-driven dispatcher that chooses a preprocessing handler and runs it.

It will read a master file under the target directory:

* If `$LANG_ID` is set: `master-$LANG_ID.qmd` (or `.md`)
* Else: auto-detect `master-*.qmd/.md`

  * If more than one exists, it fails with **Ambiguous** and tells you to set `LANG_ID`.

Language id notes:

* Hyphenated IDs in filenames are supported (for example `master-zh-cn.qmd`).
* If a directory has both `master-en.qmd` and `master-zh-cn.qmd`, this is still ambiguous for `preproc` without `LANG_ID`.

It reads these front matter keys (from the chosen master file):

* `rhythmpress-preproc` (default: `copy`)
* `rhythmpress-preproc-args` (list of strings; extra args to pass to the handler)

Then it delegates to:

```text
rhythmpress preproc_<handler> <fm-args...> <dirname> <extra CLI args...>
```

Usage:

```bash
rhythmpress preproc [DIR] [-v|--verbose] [-- <extra args for the handler>]
```

Examples:

```bash
# preprocess the current directory
rhythmpress preproc

# preprocess a specific article directory
rhythmpress preproc hypergroove/tatenori-theory

# pass through handler flags (example: disable TOC include)
rhythmpress preproc hypergroove/tatenori-theory --no-toc

# verbose delegation logging
rhythmpress preproc -v hypergroove/tatenori-theory
```

Exit behavior:

* returns the delegated handler’s exit code
* `2` on “no master found” / ambiguity / invalid dir

---

## `rhythmpress preproc-copy`

Copy-based preprocessing (per language master):

* `master-<lang>.qmd` → `<lang>/index.qmd`
* generates `_sidebar-<lang>.yml` (a minimal sidebar snippet for this article)
* injects git-derived `cdate` and `mdate` into the generated `index.qmd`
* optionally appends a TOC include: `{{< include /_sidebar-<lang>.generated.md >}}`

Usage:

```bash
rhythmpress preproc-copy [DIR...]
```

Options:

* `--no-toc` do not append the `/_sidebar-<lang>.generated.md` include

Examples:

```bash
rhythmpress preproc-copy hypergroove/tatenori-theory
rhythmpress preproc-copy --no-toc hypergroove/tatenori-theory
```

---

## `rhythmpress preproc-split`

Split-based preprocessing (per language master):

* splits a `master-<lang>.qmd` into per-section pages (creates `<slug>/<lang>/index.qmd`)
* generates `_sidebar-<lang>.yml` for the article based on discovered slugs
* creates/updates a language index page under `<lang>/index.qmd` (depending on split logic)
* optionally appends the TOC include to generated pages

Usage:

```bash
rhythmpress preproc-split [DIR...]
```

Options:

* `--no-toc` do not append the `/_sidebar-<lang>.generated.md` include

Example:

```bash
rhythmpress preproc-split hypergroove/the-four-principles-of-groove
```

---

## `rhythmpress preproc-clean`

Safely clean an article directory (destructive). It is guarded by multiple safeguards and requires an explicit sentinel file.

Key safeguards:

* refuses `/`, `$HOME`, VCS metadata paths (`.git`, etc.), symlinks
* must be inside a “project root” (a directory containing `.git` or `_quarto.yml`)
* the target directory must contain the sentinel file (default `.article_dir`)
* requires `--apply` to actually delete anything

Usage:

```bash
rhythmpress preproc-clean [DIR...] [--apply] [--force] [--sentinel NAME] [--purge-sidebars|--no-purge-sidebars] [--lang LANG]
```

Options:

* `--apply` actually perform deletions (otherwise dry-run)
* `--force` skip interactive confirmation (“Type EXACTLY: DELETE”)
* `--sentinel <name>` sentinel filename (default: `.article_dir`)
* `--purge-sidebars / --no-purge-sidebars` delete sidebar artifacts in the target dir (default: **purge enabled**)
* `--lang <lang>` limit sidebar purge to a specific language id

Examples:

```bash
# dry-run
rhythmpress preproc-clean hypergroove/tatenori-theory

# real clean (non-interactive)
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force

# keep sidebars
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force --no-purge-sidebars

# purge only ja sidebars
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force --lang ja
```

Exit behavior:

* `0` success (including dry-run success)
* `2` safeguard refusal / validation failure

---

## `rhythmpress build`

Batch build runner that processes multiple article directories listed in a definition file (default `_rhythmpress.conf`).

Default steps:

1. `rhythmpress preproc_clean <dir> --apply --force`
2. `rhythmpress preproc <dir>`
3. Sidebar aggregation and rendering:

   * `rhythmpress sidebar_confs --defs <defs>`
   * `rhythmpress sidebar_langs --defs <defs>`
   * `rhythmpress render_sidebar _sidebar-<lang>.generated.conf` (for each detected language)

Language handling for preprocessing inside `build`:

* If `LANG_ID` is set: build only that language (and validate it exists if masters exist)
* Else if multiple `master-<lang>.*` exist: build **all** languages (and log this decision)
* Else if exactly one exists: build that one
* Else: legacy path (no `LANG_ID`)

Usage:

```bash
rhythmpress build [--defs FILE] [--sidebar CONF] [--no-sidebar] [--apply-flags ...] [--skip-clean] [--clean-only] [--keep-going|-k] [--chdir DIR] [-v|--verbose] [--dry-run]
```

Notable options:

* `--defs <file>` definition file path (use `-` for stdin)
* `--sidebar <conf>` sidebar conf used only as a fallback when language discovery fails (default `_sidebar-ja.conf`)
* `--no-sidebar` skip sidebar generation entirely
* `--apply-flags ...` flags passed to `preproc_clean` (default `--apply --force`)
* `--skip-clean` skip `preproc_clean`
* `--clean-only` run only `preproc_clean` for each target, then stop
* `--keep-going` continue after errors
* `--chdir <dir>` change working directory before running
* `--dry-run` print what would run

Examples:

```bash
# standard build
rhythmpress build

# dry-run
rhythmpress build --dry-run

# run from another directory
rhythmpress build --chdir /path/to/project

# only clean all targets (no preproc, no sidebar)
rhythmpress build --clean-only

# skip clean (common in a dev loop)
rhythmpress build --skip-clean

# continue even if one directory fails
rhythmpress build --keep-going
```

Exit behavior:

* returns the first failing step’s exit code unless `--keep-going` is set
* `2` for defs/dir validation failures

---

## `rhythmpress sidebar-confs`

Scan directories listed in a defs file for per-article sidebars named `_sidebar-<lang>.yml`, group them per language, and emit root-level generated conf files:

* `./_sidebar-<lang>.generated.conf`

Each generated conf contains:

1. `_sidebar-<lang>.before.yml`
2. one line per discovered per-dir sidebar path
3. `_sidebar-<lang>.after.yml`

Usage:

```bash
rhythmpress sidebar-confs [--defs FILE] [--chdir DIR] [-v|--verbose] [--dry-run]
```

Example:

```bash
rhythmpress sidebar-confs --defs _rhythmpress.conf
```

Exit behavior:

* `0` even if no sidebars were found (it simply writes nothing)
* `2` on missing defs file / invalid `--chdir`

---

## `rhythmpress sidebar-langs`

Scan directories listed in a defs file and print discovered language IDs (one per line), based on `_sidebar-<lang>.yml` filenames.

Usage:

```bash
rhythmpress sidebar-langs [--defs FILE] [--chdir DIR] [-v|--verbose]
```

Example:

```bash
rhythmpress sidebar-langs --defs _rhythmpress.conf
```

Exit behavior:

* `0` even if no languages were found (empty output can be meaningful)
* `2` on missing defs / invalid `--chdir`

---

## `rhythmpress render-sidebar`

Merge a sidebar conf (a list of YAML files) into a single generated sidebar YAML and a Markdown TOC include.

This is a **bash script** and requires external tools.

Requirements:

* `yq` v4 (Mike Farah) must be on `PATH`
* `RHYTHMPRESS_ROOT` must be set (typically via `eval "$(rhythmpress eval)"`)
* `python3` (for optional hook)

Usage:

```bash
rhythmpress render-sidebar [path/to/_sidebar-<lang>.conf]
```

Behavior:

* Conf path resolution:

  * If an absolute path is given, it uses it as-is.
  * Else it reads from: `$RHYTHMPRESS_ROOT/<conf>`
* Language id:

  * inferred from `_sidebar-<lang>.conf` filename, default `ja`
* Outputs written next to the conf:

  * `_sidebar-<lang>.generated.yml`
  * `_quarto-<lang>.yml` (generated by merging `_quarto.yml`, `_metadata-<lang>.yml`, and the merged sidebar YAML)
  * `_sidebar-<lang>.generated.md`
* Generated `_quarto-<lang>.yml` profile behavior:

  * canonical merge rules live in `docs/configuration.md`, section `3.3 Merge semantics`
  * merge order is: base `_quarto.yml`, language metadata, merged sidebar, then profile-only Rhythmpress overrides
  * `project.output-dir` is `.site-<lang>` (for example `.site-en`, `.site-ja`)
  * Rhythmpress appends these profile render entries:
    `index.md`, `**/<lang>/**/*.qmd`, `!**/master*.md`, `!**/master*.qmd`, `!drafts/**`
  * list-valued config is merged by concatenation, so existing base `_quarto.yml` `project.render` entries remain in the generated profile; later scalar values override earlier ones
  * only root `index.md` is force-added by Rhythmpress; root `index.qmd` is not automatically added
  * non-Rhythmpress custom `project.post-render` commands are preserved, while Rhythmpress-managed entries are normalized to:
    `rhythmpress post-render-patch --output-dir .site-<lang> --lang-id <lang>`
    `rhythmpress sitemap`
  * for merged multi-profile deploys, run `rhythmpress finalize --output-dir .site` after assembly so final artifacts are derived from the merged output
  * if you need the full static asset tree in every profile/merged output, include `assets/**` in base `_quarto.yml` `project.resources`
  * generated top-level `lang` is normalized to BCP47-style tags (for example `en-US`, `ja-JP`) to avoid malformed html `lang`/`xml:lang` values in Quarto website output
* Optional post-merge hook:

  * If present, runs:

    * `_rhythmpress.hook-after._sidebar-<lang>.generated.yml.py <generated-yml> <lang> <conf-basename>`
  * Hook failures are ignored (non-fatal)
* TOC generation:

  * writes `**<resolved label>**` header
  * resolves the label in this order:

    * merged metadata override at `rhythmpress.toc-label`
    * built-in default for the target language ID
    * legacy fallback `目次`
  * appends output of `rhythmpress render_toc <conf-basename>`
  * affects only `_sidebar-<lang>.generated.md`, not Quarto's own page-TOC UI
* Quarto profile generation is idempotent:

  * `_quarto-<lang>.yml` is overwritten only when merged content actually changes

Example:

```bash
eval "$(rhythmpress eval)"
rhythmpress render-sidebar _sidebar-ja.generated.conf
```

Exit behavior:

* `127` if `yq` is missing
* `1` if `RHYTHMPRESS_ROOT` is not set or conf missing
* otherwise: script exits on first failing command (`set -euo pipefail`), except hook failures are ignored

---

## `rhythmpress render-toc`

Read a sidebar conf file (list of YAMLs), concatenate `website.sidebar.contents` arrays, and render a nested Markdown list to stdout. Title resolution for leaves is:

1. file front matter `title` (string), else
2. first ATX H1 (`# ...`), else
3. path-based fallback (“humanized”)

Usage:

```bash
rhythmpress render-toc <conf> [--root DIR] [--langs ja,en] [--prefer-title qmd|yaml] [--cache PATH|-] [--strict] [--prune-empty]
```

Notes:

* Root resolution:

  * `--root` wins, otherwise it **requires** `$RHYTHMPRESS_ROOT`
* `--cache`:

  * default is `-` (disable cache)
  * any other value is treated as a JSON cache path relative to the root

Examples:

```bash
# with project env
eval "$(rhythmpress eval)"
rhythmpress render-toc _sidebar-ja.generated.conf > /tmp/toc.md

# override root
rhythmpress render-toc _sidebar-ja.generated.conf --root /path/to/project

# strict mode (missing files → non-zero exit after emitting TOC)
rhythmpress render-toc _sidebar-ja.generated.conf --strict
```

Exit behavior:

* `0` success
* `2` if root cannot be resolved (missing `--root` and `RHYTHMPRESS_ROOT` unset)
* `1` in `--strict` mode if missing files were detected

---

## `rhythmpress render-nav`

Generate a language-specific global navigation Markdown from a defs file, using `create_global_navigation()` in the library.

Usage:

```bash
rhythmpress render-nav --lang <lang> [--defs FILE] [--out PATH|-] [--stdout] [--strict] [--dry-run] [--chdir DIR] [-v|-vv] [-q]
```

Notes:

* Default output is stdout (`--out -`), unless you pass a real `--out` path.
* Default is **non-strict**; `--strict` makes missing/invalid inputs fail.
* `--no-strict` exists but is deprecated (non-strict is already the default).

Examples:

```bash
# print to stdout
rhythmpress render-nav --lang ja --defs _rhythmpress.conf

# write to a file
rhythmpress render-nav --lang ja --defs _rhythmpress.conf --out ./_sidebar-ja.generated.md

# strict
rhythmpress render-nav --lang en --strict
```

Exit behavior (documented in the script):

* `0` success
* `1` runtime/usage error
* `2` write error

---

## `rhythmpress auto-rebuild`

Watch for changes to the following files and rebuild on change:

* `master-*.qmd` / `master-*.md`
* `_quarto.yml`
* `_quarto-*.yml`
* `_metadata-*.yml`
* `_sidebar-*.conf` (excluding generated `_sidebar-*.generated.conf`)

* ignores noisy dirs like `.git`, `.venv`, `_site`, `.quarto`, etc.
* triggers on master files and selected root config files listed above
* debounced (1000ms)
* rebuild action is: `rhythmpress build --skip-clean`

Usage:

```bash
rhythmpress auto-rebuild
```

Typical dev loop (two terminals):

```bash
# terminal A
eval "$(rhythmpress eval)"
rhythmpress auto-rebuild

# terminal B
quarto preview
```

---

## `rhythmpress preview`, `rhythmpress preview-all`, `rhythmpress start`, and `rhythmpress clean-start`

* `preview`: thin wrapper for `quarto preview` with `RHYTHMPRESS_ROOT` and `QUARTO_PROJECT_DIR` set to current directory
  * when called with no arguments, it fails fast and asks for explicit options
  * override for intentional bare preview: `--allow-empty-preview` (alias: `--no-warn`)
  * exports `RHYTHMPRESS_PREVIEW=1` during preview command execution
* `preview-all`: serves assembled output (`.site`) as static files:
  `python3 -m http.server 5150 --directory .site`
  * supports `--output-dir <dir>` to change served directory
  * supports `--port <n>` to change port
  * extra args are passed through to `python3 -m http.server` (for example `--bind 127.0.0.1`)
* `start`: tmux process manager (two panes):
  * pane 1: `rhythmpress auto-rebuild`
  * pane 2: `rhythmpress preview [args]`
  * outside tmux: creates/attaches a managed tmux session
  * inside tmux: splits the current window and starts both panes there
  * panes are configured with `remain-on-exit` so output stays visible after process exit
  * requires explicit preview args (for example `--profile en`)
* `clean-start`: removes `./.site`, `./.site-*`, and `./.quarto`, then delegates to `start`
* `start` options:
  * `--session NAME` (default: `rhythmpress-dev`)
  * `--detach` (start session without attaching)
  * `--kill-existing` (replace existing session of same name)
* extra args are passed to `rhythmpress preview` in the preview pane (for example `--profile en`)

Usage:

```bash
rhythmpress start
rhythmpress clean-start
rhythmpress preview --profile en
rhythmpress preview --profile ja
rhythmpress preview --allow-empty-preview
rhythmpress preview-all
rhythmpress preview-all --port 5150
rhythmpress start --profile en
rhythmpress start --session rp-en --detach --kill-existing --profile en
rhythmpress clean-start --profile en
```

(For `start`/`clean-start`, tmux is required.)

---

## `rhythmpress render`

Thin wrapper around `quarto render`.

* forwards all arguments to `quarto render`
* sets `RHYTHMPRESS_ROOT` and `QUARTO_PROJECT_DIR` to the current working directory
* safety guard: exits with an error when called with no arguments
* `--clean`: removes resolved output directory before render
  * resolution order: `--output-dir`, then `--profile` -> `.site-<profile>`, then `_quarto-<lang>.yml` from `--config`

Usage:

```bash
rhythmpress render --profile en
rhythmpress render --clean --profile en
rhythmpress render --config _quarto-en.yml
```

---

## `rhythmpress render-all`

Render all detected profiles by scanning `_quarto-*.yml` in the current directory.

* derives profile id from each filename (`_quarto-en.yml` -> `en`)
* runs `rhythmpress render --clean --profile <id>` for each profile
* forwards any extra args to each render invocation

Usage:

```bash
rhythmpress render-all
rhythmpress render-all --no-execute
```

---

## `rhythmpress run-all`

Run the standard multilingual compile pipeline in one command:

1. `rhythmpress build`
2. `rhythmpress render-all`
3. `rhythmpress assemble`

By default, it stops at the first failing step.

Usage:

```bash
rhythmpress run-all
rhythmpress run-all --skip-build
rhythmpress run-all --skip-render
rhythmpress run-all --skip-assemble
```

Per-step argument passthrough:

```bash
rhythmpress run-all --build-arg --skip-clean
rhythmpress run-all --render-arg --no-execute
rhythmpress run-all --assemble-arg --out --assemble-arg .site-merged
```

---

## `rhythmpress lang-ids`

Detect language IDs from profile/metadata files in the current directory and print one ID per line.

* scans `_quarto-*.yml` / `_quarto-*.yaml`
* scans `_metadata-*.yml` / `_metadata-*.yaml`
* prints unique IDs in sorted order

Usage:

```bash
rhythmpress lang-ids
```

---

## `rhythmpress render-lang-switcher-js`

Generate a standalone runtime language-switcher JavaScript file.

* default output: `./lang-switcher.generated.mjs`
* writes only when content changed (idempotent)
* supports strict/non-strict runtime config handling
* supports `--mode`:
  * `all`: combined data bootstrap + UI mount (default)
  * `data`: global JSON bootstrap only (`globalThis.RHYTHMPRESS_LANG_SWITCHER`)
  * `ui`: UI mount only (reads `globalThis.RHYTHMPRESS_LANG_SWITCHER`)
* display labels (flag/name/code) and profile `lang` normalization both use the same internal language registry so mappings stay consistent across commands

Usage:

```bash
rhythmpress render-lang-switcher-js
rhythmpress render-lang-switcher-js --conf _rhythmpress.conf --current-lang en
rhythmpress render-lang-switcher-js --out lang-switcher.generated.mjs
rhythmpress render-lang-switcher-js --strict
rhythmpress render-lang-switcher-js --mode data --out lang-switcher-data.generated.mjs
rhythmpress render-lang-switcher-js --mode ui --out lang-switcher-ui.generated.mjs
```

Then include it from your pages/template:

```html
<script type="module" src="/lang-switcher.generated.mjs"></script>
```

When split (`--mode data` + `--mode ui`), include data first:

```html
<script type="module" src="/lang-switcher-data.generated.mjs"></script>
<script type="module" src="/lang-switcher-ui.generated.mjs"></script>
```

---

## `rhythmpress render-worker-router`

Generate Cloudflare Worker router files from project language metadata.

* generates worker script:
  * default: `./cloudflare-language-router.generated.mjs`
* generates wrangler vars/config template:
  * default: `./wrangler.language-router.generated.toml`
* language IDs:
  * default: auto-detected from `_quarto-*` / `_metadata-*`
  * override: `--lang-ids en,ja,fr`
* default language:
  * default: `_rhythmpress.conf` `default_lang` if present, else first detected language
  * override: `--default-lang <id>`
* route mapping:
  * reads optional `lang_path.<lang>=...` from `_rhythmpress.conf`
  * emits `LANG_ROUTE_MAP` in wrangler template when available
* writes only when content changed (idempotent)

Usage:

```bash
rhythmpress render-worker-router
rhythmpress render-worker-router --conf _rhythmpress.conf
rhythmpress render-worker-router --lang-ids en,ja --default-lang en
rhythmpress render-worker-router --worker-out worker.mjs --wrangler-out wrangler.toml
rhythmpress render-worker-router --no-wrangler
```

---

## `rhythmpress assemble`

Merge rendered profile output directories into a single deploy tree.

* default source directories: auto-detected `.site-*`
* default output directory: `.site`
* merges with `rsync` in source order
* does not run final artifact steps; use `rhythmpress finalize` after assembly

Usage:

```bash
rhythmpress assemble
rhythmpress assemble --out .site-merged
rhythmpress assemble .site-en .site-ja
rhythmpress assemble --no-sitemap  # compatibility no-op; final artifacts now belong to finalize
```

---

## `rhythmpress finalize`

Run final artifact generators against one rendered output directory.

* runs `rhythmpress sitemap` unless `--skip-sitemap` is passed
* runs `rhythmpress render-social-cards` unless `--skip-social-cards` is passed
* forwards `--site-url` through to both artifact generators

Usage:

```bash
rhythmpress finalize --output-dir .site
rhythmpress finalize --output-dir .site --skip-social-cards
rhythmpress finalize --output-dir .site --site-url https://example.com/
```

---

## `rhythmpress render-social-cards`

Render social-card PNGs from already-rendered HTML pages and inject Open Graph / Twitter metadata.

* default output directory: `QUARTO_PROJECT_OUTPUT_DIR`, else `_quarto.yml` `project.output-dir`, else `_site`
* default render mode: `mobile-page`
* default mobile viewport: `800x600`
* default output image size: `1200x630`
* default browser: `RHYTHMPRESS_SOCIAL_BROWSER`, else a known system Chrome/Chromium path

Behavior highlights:

* scans rendered `*.html` files and skips non-content outputs such as `404.html` and `site_libs`
* opens each rendered page in Chrome/Chromium through Playwright
* extracts rendered title/opening text for social metadata
* screenshots the real mobile page by default, with screenshot-only CSS hiding Quarto/Rhythmpress chrome
* serves mobile-page captures from temporary `127.0.0.1` HTTP so root-absolute assets resolve like deployed pages
* writes images under `attachments/social/...`
* refreshes a managed metadata block in each page `<head>`

Useful options:

```bash
rhythmpress render-social-cards --output-dir .site
rhythmpress render-social-cards --output-dir .site --max-pages 1
rhythmpress render-social-cards --output-dir .site --render-mode template
rhythmpress render-social-cards --output-dir .site --hide-selector '.project-banner'
rhythmpress render-social-cards --output-dir .site --hide-selector '#id1, #id2, .class1, .class2'
rhythmpress render-social-cards --output-dir .site --crop-selector '#title-block-header' --crop-selector 'main.content'
rhythmpress render-social-cards --output-dir .site --css 'main { margin-top: 0 !important; }'
rhythmpress render-social-cards --output-dir .site --enable-javascript --wait-ms 3000
```

`--hide-selector` accepts CSS selectors. Repeat the flag or use commas for multiple selectors. Whitespace is not a separator because it is valid CSS descendant-selector syntax.
`--crop-selector` is ordered fallback: repeat the flag to try selectors in order. Commas inside one crop selector remain normal CSS selector-group syntax.
`--css` injects raw screenshot-only CSS after generated hide rules. Repeat it for multiple override blocks.
`--enable-javascript` allows page scripts for dynamic embeds. Use `--wait-ms` to give third-party widgets time to paint before capture.

Persistent defaults may be stored in `_quarto.yml` under `rhythmpress.social-cards`.
`render-social-cards`, `finalize`, and `run-all` all use those settings because the generator
loads them directly. CLI scalar options override config scalars; `hide-selector` and `css`
append after config values; CLI `crop-selector` values replace config crop selectors.

---

## `rhythmpress sitemap`

Generate `sitemap.xml` inside the Quarto output directory by scanning rendered HTML.

No CLI arguments. Configure via environment variables or `_quarto.yml`:

* Output directory:

  * `QUARTO_PROJECT_OUTPUT_DIR` env, else `_quarto.yml` `project.output-dir`, else `_site`
* Site URL:

  * `SITE_URL` env, else `_quarto.yml` `website.site-url`, else `https://example.com/`

Behavior highlights:

* skips certain files (e.g., `404.html`, `search.html`)
* skips filenames starting with `master-`
* reads `<head>` for:

  * canonical URL (`<link rel="canonical" ...>`)
  * robots noindex (`<meta name="robots" ...>`)
  * modified/published time via meta (`mdate` / `article:modified_time`, `cdate` / `article:published_time`)
* writes: `<output-dir>/sitemap.xml`

Usage:

```bash
# after you have rendered the site
quarto render
rhythmpress sitemap
```

Example with env overrides:

```bash
SITE_URL="https://rhythmdo.com" QUARTO_PROJECT_OUTPUT_DIR="_site" rhythmpress sitemap
```

Exit behavior:

* exits non-zero if the output directory does not exist (you must render first, or set the output dir correctly)


## Command Examples

This project’s “happy path” is a two-terminal dev loop:

Terminal A: `quarto preview`  
Terminal B: `rhythmpress auto-rebuild` (rebuilds whenever you edit `master-*.qmd/.md`)

Everything below is written to match that workflow, and the default multi-directory build driven by `_rhythmpress.conf`.

---

### Recommended activation (your actual workflow)

Rhythmpress expects a few environment variables (most importantly `RHYTHMPRESS_ROOT`). In practice, you already have a clean one-liner that does the right thing:

```bash
alias rhythmpress_activate='. .venv/bin/activate; eval "$(rhythmpress eval)"'
````

So, the default assumption in examples is:

```bash
cd /path/to/your/quarto-project
rhythmpress_activate
```

Note: some scripts still print a stale hint like `eval "$(rhythmpress env)"`. There is **no** `env` subcommand in this codebase; use `eval "$(rhythmpress eval)"` (or your alias) instead.

---

### Command name normalization

The dispatcher accepts `kebab-case`, `snake_case`, and even accidental spaces. These are equivalent:

* `rhythmpress preproc-clean`
* `rhythmpress preproc_clean`
* `rhythmpress "preproc clean"`

In examples, I mostly use kebab-case because it’s easier to read.

---

### 0) Quick “what do I have installed?” (`rhythmpress list`)

Print the available local subcommands installed with the package:

```bash
rhythmpress list
```

---

### 1) Project environment activation (`rhythmpress eval`)

Emit shell code that sets `RHYTHMPRESS_ROOT`, amends `PATH`, and adjusts your prompt (interactive shells).

Typical usage:

```bash
eval "$(rhythmpress eval)"
```

Examples (matching your style):

```bash
# activate
rhythmpress_activate

# deactivate only the Rhythmpress bits (keeps your venv active)
rhythmpress_deactivate
```

Less common flags:

```bash
# force re-apply even if already active for the same root
eval "$(rhythmpress eval -f)"

# csh/tcsh
eval `rhythmpress eval -c`
```

---

### 2) Quickstart scaffolding (`rhythmpress create-page`)

Create a new article directory scaffold:

* `<dir>/.article_dir` (the clean sentinel)
* `<dir>/.gitignore`
* `<dir>/master-<lang>.qmd` (default `ja`)

Example:

```bash
rhythmpress create-page hypergroove/the-four-principles-of-groove --lang en
```

Follow-up (typical): set `rhythmpress-preproc:` in the master’s YAML front matter (see `docs/concepts.md`), then run a build.

---

### 3) The main build (multi-directory) (`rhythmpress build`)

This is the “real project” command. It reads `_rhythmpress.conf` (one directory per line), then for each directory:

1. `rhythmpress preproc-clean <dir> --apply --force`
2. `rhythmpress preproc <dir>` (dispatches to copy/split based on front matter)
   Then it generates and renders sidebars per language.

The default command (most common):

```bash
rhythmpress build
```

Typical “I’m debugging” variants:

```bash
# show what would run
rhythmpress build --dry-run

# print each command before running it
rhythmpress build -v

# continue even if one directory fails
rhythmpress build --keep-going
```

When you’re iterating fast (usually in the watcher loop), skip cleaning:

```bash
rhythmpress build --skip-clean
```

If you only want to clean generated artifacts across all targets (and stop):

```bash
rhythmpress build --clean-only
```

If you want to build from outside the project root:

```bash
rhythmpress build --chdir /path/to/project
```

#### Language behavior inside `build`

This matters a lot when a directory has both `master-en.*` and `master-ja.*`:

* If `LANG_ID` is set → build only that language (and it must exist).
* If `LANG_ID` is not set and multiple masters exist → build **all** languages (you’ll see an `[INFO] ... building all` log line).
* If exactly one master exists → it builds that one.
* If no `master-<lang>.*` exists → legacy behavior (usually a failure later).

Examples:

```bash
# build everything (all languages where applicable)
rhythmpress build

# build only English across the whole project
LANG_ID=en rhythmpress build

# build only Japanese across the whole project
LANG_ID=ja rhythmpress build
```

---

### 4) Dev loop: auto rebuild (`rhythmpress auto-rebuild`)

This watches master files and selected project config files (`_quarto*`, `_metadata-*`, `_sidebar-*.conf`) and triggers:

```bash
rhythmpress build --skip-clean
```

Recommended two-terminal loop:

```bash
# Terminal A
rhythmpress_activate
quarto preview

# Terminal B
rhythmpress_activate
rhythmpress auto-rebuild
```

This is the workflow Rhythmpress is optimized for.

---

### 5) Single-directory work (manual) (`preproc-clean`, `preproc`, `preproc-copy`, `preproc-split`)

When you’re focusing on one directory and don’t want the full `_rhythmpress.conf` build.

#### 5.1 Clean one directory safely (`rhythmpress preproc-clean`)

Dry run first (always):

```bash
rhythmpress preproc-clean hypergroove/tatenori-theory
```

Then actually delete generated artifacts:

```bash
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force
```

If you want to keep sidebars in that directory:

```bash
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force --no-purge-sidebars
```

If you only want to purge sidebar files for one language:

```bash
rhythmpress preproc-clean hypergroove/tatenori-theory --apply --force --lang ja
```

Guard rails you should know:

* It refuses `/`, `$HOME`, symlinks, and VCS metadata paths.
* It refuses to operate outside a project root (must find `.git` or `_quarto.yml`).
* It requires the sentinel file `.article_dir` inside the target directory.

#### 5.2 Dispatch preproc based on master front matter (`rhythmpress preproc`)

This reads `master-<lang>.*` and looks for:

* `rhythmpress-preproc: copy` (default) or `split`
* `rhythmpress-preproc-args: [...]` (optional)

Example:

```bash
# preprocess one directory (auto-selects master by LANG_ID or auto-detect)
rhythmpress preproc hypergroove/tatenori-theory
```

If the directory has both `master-en.*` and `master-ja.*`, you must set `LANG_ID` (unless `build` is doing the per-lang loop for you):

```bash
LANG_ID=en rhythmpress preproc hypergroove/tatenori-theory
LANG_ID=ja rhythmpress preproc hypergroove/tatenori-theory
```

Verbose delegation tracing:

```bash
rhythmpress preproc -v hypergroove/tatenori-theory
```

#### 5.3 Run a preproc handler directly (`preproc-copy`, `preproc-split`)

Direct call is useful when you’re testing the handler itself.

```bash
# copy mode
rhythmpress preproc-copy hypergroove/tatenori-theory

# split mode
rhythmpress preproc-split hypergroove/the-four-principles-of-groove
```

Skip appending the generated TOC include:

```bash
rhythmpress preproc-copy --no-toc hypergroove/tatenori-theory
rhythmpress preproc-split --no-toc hypergroove/the-four-principles-of-groove
```

---

### 6) Sidebar pipeline (what `build` does for you)

Normally you do not need these manually, but they’re useful to understand/debug.

#### 6.1 Aggregate per-dir sidebars into per-language confs (`rhythmpress sidebar-confs`)

```bash
rhythmpress sidebar-confs --defs _rhythmpress.conf
```

This writes files like:

* `_sidebar-ja.generated.conf`
* `_sidebar-en.generated.conf`

#### 6.2 Discover language ids present (`rhythmpress sidebar-langs`)

```bash
rhythmpress sidebar-langs --defs _rhythmpress.conf
```

#### 6.3 Merge YAMLs and generate Markdown TOC include (`rhythmpress render-sidebar`)

This requires:

* `RHYTHMPRESS_ROOT` set (use `rhythmpress_activate`)
* `yq` v4 installed

Example:

```bash
rhythmpress_activate
rhythmpress render-sidebar _sidebar-ja.generated.conf
rhythmpress render-sidebar _sidebar-en.generated.conf
```

Outputs next to the conf:

* `_sidebar-ja.generated.yml`
* `_sidebar-ja.generated.md`

If you see an error message telling you to run `eval "$(rhythmpress env)"`, read it as `eval "$(rhythmpress eval)"` (the script message is stale).

#### 6.4 Generate TOC to stdout (`rhythmpress render-toc`)

This reads a sidebar conf and prints a Markdown list to stdout:

```bash
rhythmpress_activate
rhythmpress render-toc _sidebar-ja.generated.conf > /tmp/toc-ja.md
```

Useful flags:

```bash
# strict: missing files become an error (after printing)
rhythmpress render-toc _sidebar-ja.generated.conf --strict

# prune empty sections
rhythmpress render-toc _sidebar-ja.generated.conf --prune-empty
```

Same stale-hint note applies: if you see `rhythmpress env` in an error hint, use `rhythmpress eval`.

---

### 7) Global navigation generator (`rhythmpress render-nav`)

This generates a language-specific navigation Markdown from `_rhythmpress.conf` and prints to stdout by default:

```bash
rhythmpress render-nav --lang ja --defs _rhythmpress.conf
rhythmpress render-nav --lang en --defs _rhythmpress.conf
```

Write to a file explicitly:

```bash
rhythmpress render-nav --lang ja --defs _rhythmpress.conf --out ./_sidebar-ja.generated.md
```

Strict mode (fail on missing dirs/masters):

```bash
rhythmpress render-nav --lang en --strict
```

---

### 8) Quarto preview helpers (`rhythmpress start`, `rhythmpress clean-start`)

These are convenience wrappers that:

* `. .venv/bin/activate`
* run `RHYTHMPRESS_ROOT="$(pwd)" QUARTO_PROJECT_DIR="$(pwd)" quarto preview`
* pass additional args through to `quarto preview` (for example `--profile dev`)

Use them if you want a “just do it” shortcut:

```bash
rhythmpress start
rhythmpress start --profile dev
```

Reset Quarto caches first:

```bash
rhythmpress clean-start
rhythmpress clean-start --profile dev
```

(They assume `.venv/` exists in the project root.)

---

### 9) Sitemap generator (`rhythmpress sitemap`)

Run this after rendering the site:

```bash
quarto render
rhythmpress sitemap
```

It writes `sitemap.xml` into the Quarto output directory.

You can override site settings via env vars:

```bash
SITE_URL="https://rhythmdo.com" QUARTO_PROJECT_OUTPUT_DIR="_site" rhythmpress sitemap
```

---

### Practical “most-used” cheat sheet (your workflow)

If you only remember this pipeline:

```bash
# 1) activate
cd /path/to/project
rhythmpress_activate

# 2) run full compile pipeline (build -> render-all -> assemble -> finalize)
rhythmpress run-all
```

For a single-language run:

```bash
rhythmpress build
rhythmpress render --profile en
```
