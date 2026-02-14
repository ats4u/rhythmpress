# Rhythmpress: A Quarto-based CMS Toolkit

## Documentation

- [README.md](README.md) — Main entry point (overview + quickstart + core conventions).
- [docs/concepts.md](docs/concepts.md) — Concepts and terminology (masters, article dirs, modes, languages, sidebars, artifacts).
- [docs/workflows.md](docs/workflows.md) — End-to-end workflows (local dev, multilingual, CI build patterns).
- [docs/commands.md](docs/commands.md) — Command reference (usage examples and behavioral notes).
- [docs/configuration.md](docs/configuration.md) — Configuration reference (`_rhythmpress.conf`, sidebar confs, front matter keys, env vars, hooks).
- [docs/troubleshooting.md](docs/troubleshooting.md) — Common failures and fixes (masters ambiguity, `RHYTHMPRESS_ROOT`, `yq`, git dates, CWD issues).
- [docs/development.md](docs/development.md) — Development notes (packaging, dependency pinning, release hygiene, macOS `._*` artifacts).
- [docs/tutorial-publish-github-cloudflare.md](docs/tutorial-publish-github-cloudflare.md) — Publish a Rhythmpress-built Quarto site on GitHub Pages, fronted by Cloudflare Proxy (DNS + CDN + SSL).


## 1. Introduction

Rhythmpress is an opinionated set of command-line tools that sits *on top of Quarto* to run a “directory-per-article” CMS workflow. Instead of writing every publishable page as a standalone `.qmd`, you write a single **master** file per article (optionally per language, e.g. `master-en.qmd`, `master-ja.qmd`), and Rhythmpress generates the Quarto-ready page tree, navigation artifacts, and supporting files that Quarto then renders.

<p align="center">
  <a href="https://rhythmdo.com">
    <img src="./docs/rhythmdo-com.png"
         alt="Example output built with Rhythmpress: rhythmdo.com (Japanese)"
         width="320">
  </a><br>
  <sub>Example output (Japanese): rhythmdo.com</sub>
</p>

This project was built for large, documentation-like sites where consistency matters: predictable URLs, repeatable builds, multilingual variants, and navigation that can be assembled from many article directories without hand-editing everything.

What Rhythmpress provides (in practical terms):

* **Preprocessing of master files** into Quarto pages using two core styles:

  * **copy**: master → `<lang>/index.qmd` (keep it as one page)
  * **split**: master → many pages by headings (section-per-page output)
* **Multilingual handling** via `master-<lang>.*` conventions and `LANG_ID`-driven builds.
* **Navigation helpers** to assemble site-level navigation from many article directories.
* **Build orchestration and rebuild ergonomics** (batch build, auto-rebuild/watch mode).
* Optional “project hygiene” tools such as generated sidebar config and sitemap generation, depending on how you wire it into your Quarto project.

Non-goal (important): Rhythmpress is **not** a renderer and it does not replace Quarto. Quarto remains the tool that turns `.qmd` into HTML/PDF; Rhythmpress is the layer that prepares and organizes the inputs so Quarto can render a large site reliably.


## 2. Overview

Rhythmpress is a “preprocessor + build orchestrator” for Quarto projects. You write content in **master** files, and Rhythmpress generates the Quarto-ready page tree and navigation artifacts. Then Quarto renders the site.

Think in three layers:

1. Authoring layer (what you edit)

* A Quarto project root (contains `_quarto.yml`).
* One or more “content directories” (e.g. `hypergroove/…`), each containing a **master** file:

  * `master-en.qmd`, `master-ja.qmd`, etc. (multilingual), or
  * a single `master-<lang>.*` if you only have one language in that directory.

2. Preprocessing layer (what Rhythmpress generates)
   Rhythmpress reads a master file and emits generated `.qmd` pages in predictable locations, using one of the preproc modes:

* **copy mode**

  * Input: `master-en.qmd`
  * Output: `en/index.qmd`
  * Use when you want one page per article.

* **split mode**

  * Input: `master-en.qmd`
  * Output: multiple pages like `<slug>/en/index.qmd` (one per section)
  * A “section” is typically driven by `##` (H2) headings.
  * Use when you want one section per page (documentation style).

Alongside pages, Rhythmpress may generate helper artifacts (TOCs, navigation fragments, merged sidebar config), depending on which commands you run in your pipeline.

3. Build layer (how everything gets executed)

* A build command (e.g. `rhythmpress build`) runs preprocessing for configured targets, then runs sidebar/nav generation steps (if included), and finally you run Quarto rendering (`quarto render` / `quarto preview`) on the prepared project.

Multilingual behavior in one sentence:

* If `LANG_ID` is set, build only that language; if it’s not set and multiple `master-<lang>.*` exist, build all detected languages.

Two operational rules to keep in your head:

* Run from the Quarto project root (or use the orchestrator commands that do so), because many paths are relative to the project structure.
* Cleaning is intentionally destructive and is guarded by a sentinel file; treat it like “rm -rf with a seatbelt.”


## 3. Requirements

Rhythmpress is designed to be used inside a Quarto project directory (a directory that contains `_quarto.yml`). Some commands are pure “preprocessing”, but the usual workflow assumes the full toolchain below.

Python

* Python **3.9+** (the package declares `requires-python = ">=3.9"`).
* Recommended: run inside a virtual environment (`.venv`).

Python packages

* **PyYAML** (`yaml`) is effectively required (used by multiple commands, e.g. sitemap generation and sidebar/TOC logic).
* **watchfiles** is required if you use `rhythmpress auto-rebuild`.
* **ruamel.yaml** is optional (if installed, `render_toc` can emit better warnings with line numbers; without it, it falls back to PyYAML/limited parsing).

External commands (OS-level)

* **Quarto CLI** (`quarto`) is required for rendering the site (Rhythmpress prepares files; Quarto renders them).
* **git** is required in typical builds because Rhythmpress reads git history to inject created/modified dates. If your content is not in a git repo (or not committed), some preprocessing paths can fail.
* **yq v4 (Mike Farah)** is required for `rhythmpress render_sidebar` (it uses `yq ea ...` to deep-merge YAML files).
* A POSIX shell environment (**bash**) is required for the `.sh` helper commands (`render_sidebar.sh`, `start.sh`, etc.). On Windows, you will realistically want WSL.

Environment expectations

* Some scripts expect `RHYTHMPRESS_ROOT` to be set (normally via `eval "$(rhythmpress eval)"`). Without it, sidebar generation will refuse to run.

Operational note

* `rhythmpress sitemap` expects that Quarto output already exists (it scans the rendered HTML output directory). Running it before `quarto render` will fail by design.



## 4. Install

Rhythmpress is a Python package that installs a single CLI entrypoint: `rhythmpress`.

Recommended setup (inside your Quarto project)

1. Create and activate a virtual environment at your Quarto project root:

```bash
cd /path/to/your-quarto-project
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
```

2. Install Rhythmpress.

If you are installing from a local checkout of the Rhythmpress repo:

```bash
pip install -e /path/to/rhythmpress
```

If you are installing from an sdist/wheel you built:

```bash
pip install /path/to/rhythmpress/dist/rhythmpress-*.whl
```

3. Install runtime Python dependencies (Rhythmpress does not declare them in `pyproject.toml` yet):

```bash
pip install PyYAML watchfiles
```

Optional (only if you use the sidebar TOC features that benefit from it):

```bash
pip install ruamel.yaml
```

4. Verify the installation:

```bash
rhythmpress list
```

You should see a list of local subcommands (e.g. `build`, `preproc`, `auto-rebuild`, `render-sidebar`, `sitemap`, etc.).

Optional: activate “project mode” for the current Quarto project
From the Quarto project root, you can set `RHYTHMPRESS_ROOT` and update your shell prompt via:

```bash
eval "$(rhythmpress eval)"
```

If you want to undo it in the current shell session:

```bash
rhythmpress_deactivate
```


## 5. Activate Project Environment

Rhythmpress expects to be run from a Quarto project root (the directory that contains `_quarto.yml`). In addition, some commands (notably sidebar generation) require a project root marker in the environment.

The recommended way to enter a Rhythmpress-ready shell is:

1. Activate your Python virtual environment.
2. Evaluate `rhythmpress eval` to set project-scoped environment variables.

From the Quarto project root:

```bash
. .venv/bin/activate
eval "$(rhythmpress eval)"
```

This typically sets `RHYTHMPRESS_ROOT` (used by several scripts) and may also adjust your prompt to make it visually clear you are operating inside a Rhythmpress project.

Convenient shell alias (recommended)
If you routinely work from the same project root and you want a single command, you can define an alias in your shell startup file (e.g. `~/.zshrc`, `~/.bashrc`):

```bash
alias rhythmpress_activate='. .venv/bin/activate; eval "$(rhythmpress eval)"'
```

Then, from your Quarto project root, run:

```bash
rhythmpress_activate
```

Notes

* The alias assumes your virtual environment lives at `./.venv/` relative to the project root. If you keep venvs elsewhere, adjust the path accordingly.
* `rhythmpress eval` must be executed with `eval` because it prints shell code that defines environment variables and helper functions for the current shell session.
* If you open a new terminal session, you must activate again; these settings are not persistent across shells unless you place them in your shell startup configuration.


## 6. Quickstart workflow

Rhythmpress’s core loop is:

1. write or edit `master-<lang>.qmd`
2. run `rhythmpress preproc …` (or `rhythmpress build`) to generate Quarto-ready `index.qmd` files
3. run `quarto preview` (or `rhythmpress start`) to view the site

### 6.1 Create your first page directory

From your Quarto project root (the directory that contains `_quarto.yml`):

```bash
rhythmpress create-page my-article --lang ja
```

This creates:

* `my-article/.article_dir` (sentinel file required for safe cleaning)
* `my-article/.gitignore` (ignores generated subdirectories by default)
* `my-article/master-ja.qmd` (starter master file)

Edit `my-article/master-ja.qmd` and write your content.

### 6.2 Choose the preprocessing mode (copy vs split)

By default, `rhythmpress preproc` uses **copy** mode.

If you want **split** mode (one page per `##` section), add this to the YAML front matter of `master-<lang>.qmd`:

```yaml
rhythmpress-preproc: split
```

You can also pass extra flags to the underlying preprocessor via:

```yaml
rhythmpress-preproc-args:
  - --no-toc
```

(That example disables appending the `{{< include /_sidebar-<lang>.generated.md >}}` block.)

### 6.3 Preprocess a single directory

Copy or split is chosen automatically from the master file’s front matter:

```bash
rhythmpress preproc my-article
```

Outputs (typical):

* copy mode: `my-article/ja/index.qmd`
* split mode: `my-article/<slug>/ja/index.qmd` for each section, plus `my-article/ja/index.qmd` as a section index

### 6.4 Build multiple directories (recommended for real projects)

Create a definition file at project root, `_rhythmpress.conf`, with one article directory per line:

```txt
my-article
another-article
# comments allowed
```

Then run:

```bash
rhythmpress build
```

What `build` does, in order:

1. `preproc_clean` for each directory (destructive; guarded by `.article_dir`)
2. `preproc` for each directory (language-aware: builds all masters if multiple exist)
3. sidebar aggregation and generation (unless you disable it)

During development, you often want to skip cleaning (faster, fewer surprises):

```bash
rhythmpress build --skip-clean
```

If you are not using sidebar/TOC generation yet:

```bash
rhythmpress build --no-sidebar
```

### 6.5 Preview the site

From the project root:

```bash
quarto preview
```

Or use the provided wrapper:

```bash
rhythmpress start
```

If you want a clean Quarto preview state (removes `./.site` and `./.quarto` first):

```bash
rhythmpress clean-start
```

### 6.6 Auto rebuild on master edits (two-terminal dev loop)

Terminal A (watches `master-*.qmd/md` edits and runs `build --skip-clean`):

```bash
rhythmpress auto-rebuild
```

Terminal B (runs Quarto preview):

```bash
quarto preview
```

### 6.7 Multilingual quick tip

To build only one language when multiple `master-<lang>.*` exist:

```bash
LANG_ID=en rhythmpress build --skip-clean
```

Or for a single directory:

```bash
LANG_ID=en rhythmpress preproc my-article
```



## 7. Core conventions

Rhythmpress will feel “simple” only if you follow a few strong conventions. Most of the sharp edges people hit come from breaking one of these.

### 7.1 Project root and where you run commands

Rhythmpress treats the **project root** as the directory that contains either:

* `.git/`, or
* `_quarto.yml`

Most commands assume you run them from the project root (or that `RHYTHMPRESS_ROOT` points to it). In practice:

* You SHOULD run `rhythmpress build`, `rhythmpress preproc`, etc. from the project root.
* You MUST have `RHYTHMPRESS_ROOT` set for sidebar-related commands (the recommended way is `eval "$(rhythmpress eval)"`).

### 7.2 “Article directory” is a real unit (and it’s guarded)

An “article directory” is a directory that contains one or more master files like:

* `master-ja.qmd`
* `master-en.qmd`

It should also contain an **empty sentinel file**:

* `.article_dir`

That sentinel is required because `rhythmpress preproc_clean` refuses to delete anything unless the sentinel exists. This is intentional: it prevents you from accidentally running a destructive clean on the wrong directory.

### 7.3 Master file naming and language selection

Master files MUST be named:

* `master-<lang>.qmd` or `master-<lang>.md`

Rules:

* If both exist for the same language, `.qmd` is preferred.
* If a directory contains multiple `master-<lang>.*`, you MUST specify the language with `LANG_ID=<lang>` when using `rhythmpress preproc`.
* `rhythmpress build` handles multi-language dirs automatically by running `preproc` once per language when multiple masters are present.

Practical implication: keep language IDs simple (letters/digits plus `_` / `-` / `.`) and consistent.

### 7.4 Required headings in split mode

If you use split mode (`rhythmpress-preproc: split`), Rhythmpress splits at **H2** (`##`) only.

So:

* Your master MUST contain at least one `## ...` heading, or split mode produces nothing.
* Each `##` becomes its own page at `<slug>/<lang>/index.qmd`.

### 7.5 Slugs and the “explicit ID wins” rule

For section pages, Rhythmpress generates slugs like this:

1. If the header has an explicit ID (`## Title {#my-id}`), that ID is used as the slug.
2. Otherwise it slugifies the visible title text.

Important edge case:

* There is **no de-duplication**. If two H2 headers produce the same slug, they will collide and overwrite the same output path.

So for real projects:

* You SHOULD assign explicit `{#ids}` to H2 headers you care about (especially in Japanese titles, ruby titles, or titles that may repeat).

Also note: if your title includes `<ruby>...<rt>...</rt></ruby>`, the slug logic prefers the ruby “base text” (it strips `<rt>`).

### 7.6 Git dates are not optional (today)

Both copy and split preprocessors inject:

* `cdate` and `mdate`

Those dates come from git history (`git log`). Current behavior is strict: if git date extraction fails, preprocessing fails.

So:

* You SHOULD keep your master files committed in a git repo if you want preprocessing to succeed reliably.
* If you are experimenting outside git, expect failures until you adjust that policy in code.

### 7.7 Attachments convention (protected from cleaning)

Cleaning (`preproc_clean`) removes subdirectories under an article directory, except:

* directories whose name starts with `attachments`

So:

* Put durable assets (images, audio, etc.) under `attachments/` or `attachments-*/`.
* Do NOT store important content in other subdirectories unless you also change the cleaning policy.

This is mirrored in the default `.gitignore` created by `create-page`, which ignores *most* subdirectories but keeps `attachments*/`.

### 7.8 Front matter keys Rhythmpress recognizes

In `master-<lang>.*` front matter:

* `rhythmpress-preproc: copy|split`
  Chooses the preprocessor (default is `copy`).
* `rhythmpress-preproc-args: [...]` or list form
  Extra args passed to the chosen preprocessor (e.g. `--no-toc` for split).
* `rhythmpress-preproc-sidebar: false`
  Suppresses generating the per-article `_sidebar-<lang>.yml` file (copy/split honor this).

### 7.9 Build definition file is “directories only”

`rhythmpress build` reads a definition file (default `_rhythmpress.conf`) which MUST contain:

* one directory per line
* `#` comments and blank lines are allowed
* inline comments are allowed only in the form ` ... # comment` (space before `#`)

Do not put YAML paths in this file. It is strictly a list of article directories.

### 7.10 Sidebar conventions (how navigation is assembled)

There are two layers:

1. Per-article sidebar fragments (optional)

* Each article dir MAY contain `_sidebar-<lang>.yml`.
* These are usually generated by preprocessing unless you disable it.

2. Project-level aggregation (done by `build`)

* `rhythmpress sidebar_confs` scans all dirs listed in `_rhythmpress.conf` and generates:

  * `_sidebar-<lang>.generated.conf`
* Each generated `.conf` includes:

  * `_sidebar-<lang>.before.yml`
  * all discovered per-dir `_sidebar-<lang>.yml`
  * `_sidebar-<lang>.after.yml`

Then `rhythmpress render_sidebar _sidebar-<lang>.generated.conf` produces:

* `_sidebar-<lang>.generated.yml` (merged YAML via `yq`, last-wins)
* `_sidebar-<lang>.generated.md` (Markdown TOC)

Two “hard-coded” behaviors worth knowing:

* The generated Markdown TOC file always begins with `**目次**` (Japanese header).
* `render_toc` resolves the `.conf` path relative to `RHYTHMPRESS_ROOT`, so sidebar conf files are expected to live at the project root in the default workflow.

### 7.11 Optional post-merge hook for sidebars

If this file exists at project root:

* `_rhythmpress.hook-after._sidebar-<lang>.generated.yml.py`

…it will be executed after YAML merge. It receives arguments:

1. generated YAML path
2. language ID
3. conf basename

Failures are ignored (non-fatal), so hooks are safe to experiment with.

If you want, I can write the next section (“8. Command reference”) in a way that matches these conventions and warns users exactly where things break when the conventions are violated.



## 8. Command list (short)

Rhythmpress is a single CLI (`rhythmpress`) that dispatches to subcommands. The “short list” below is meant as a map of what exists; detailed usage and flags should live in `docs/commands.md`.

Core workflow

* `rhythmpress create-page <name> [--lang <lang>]`
  Create a new article directory with `.article_dir`, `.gitignore`, and a starter `master-<lang>.qmd`.

* `rhythmpress preproc <dir> [--lang <lang>]`
  Preprocess one article directory (copy/split chosen from the master’s front matter).

* `rhythmpress build`
  Run the configured multi-directory pipeline (clean → preproc → sidebar generation).

* `rhythmpress auto-rebuild`
  Watch for changes and rerun the build pipeline automatically (development workflow).

Preview helpers

* `rhythmpress start`
  Start Quarto preview using the project’s standard build/preview flow (wrapper script).

* `rhythmpress clean-start`
  Clean Quarto preview state (`.quarto/`, `.site/`) and then start preview.

Preprocessors (direct calls; usually you don’t need these)

* `rhythmpress preproc-copy <dir> [--lang <lang>]`
  Force copy mode (master → `<lang>/index.qmd`).

* `rhythmpress preproc-split <dir> [--lang <lang>]`
  Force split mode (master → per-section page tree).

* `rhythmpress preproc-clean <dir>`
  Destructively remove generated content under the article directory (requires `.article_dir`).

Navigation / sidebar utilities

* `rhythmpress sidebar_confs <_rhythmpress.conf>`
  Generate `_sidebar-<lang>.generated.conf` files by scanning listed article dirs.

* `rhythmpress render-sidebar <_sidebar-<lang>.generated.conf>`
  Merge sidebar YAML via `yq` and emit `_sidebar-<lang>.generated.yml` and a Markdown TOC.

* `rhythmpress render-toc <sidebar.yml|.conf>`
  Render a Markdown TOC from a Quarto sidebar YAML (or a `.conf` that expands into YAML).

* `rhythmpress render-nav <dir>`
  Emit navigation Markdown for a directory (typically to stdout).

Site output utilities

* `rhythmpress sitemap`
  Generate `sitemap.xml` from the rendered Quarto HTML output directory.

Environment / introspection

* `rhythmpress eval`
  Print shell code to set `RHYTHMPRESS_ROOT` and helper functions in the current shell (use with `eval`).

* `rhythmpress list`
  List available rhythmpress subcommands discovered in the installation.

Notes

* Many subcommands have both `kebab-case` and `_underscore` aliases (the dispatcher normalizes names).
* For multilingual projects, `LANG_ID=<lang>` is the reliable way to restrict processing to a single language when multiple `master-<lang>.*` files exist in a directory.


## 9. Generated artifacts (what files appear and where)

Rhythmpress has a clear separation between (a) files you author, (b) files it scaffolds once, and (c) files it regenerates repeatedly. The lists below are written from the point of view of a typical Quarto project layout.

### 9.1 Inside an article directory

Assume an article directory like:

`<ARTICLE_DIR>/`
(e.g., `hypergroove/tatenori-theory/`)

Author-managed (you edit these)

* `master-<lang>.qmd` / `master-<lang>.md`
  The source “master” document. Example: `master-ja.qmd`, `master-en.qmd`.

* `attachments*/`
  Assets (images/audio/etc.). Cleaning intentionally skips directories whose names start with `attachments`.

Scaffolded (created by `rhythmpress create-page`, generally kept as-is)

* `.article_dir`
  A sentinel file that allows destructive cleaning. Without it, `preproc-clean` refuses to delete anything.

* `.gitignore`
  A project-local ignore file. In the default scaffold it ignores most generated subdirectories (`*/`) while keeping `attachments*/`, and it ignores `_sidebar-*` files in that directory.

Generated (these are overwritten/regenerated)
Copy mode (one page per language)

* `<lang>/index.qmd`
  Generated from `master-<lang>.*`, with injected `cdate`/`mdate` in YAML front matter.
  If TOC injection is enabled (default), it appends:
  `{{< include /_sidebar-<lang>.generated.md >}}`

* `_sidebar-<lang>.yml`
  A minimal per-article sidebar fragment pointing to `<ARTICLE_DIR>/<lang>/index.qmd`.
  This file is usually ignored by the default `.gitignore`.

Split mode (one section per page)

* `<slug>/<lang>/index.qmd`
  One file per `##` (H2) section. Each section page gets its own front matter (`title`, `cdate`, `mdate`, plus copied keys from the master).

* `<lang>/index.qmd`
  A language index page containing the generated TOC for the master, with a simple page `title:`.

* `_sidebar-<lang>.yml`
  A per-article sidebar fragment that becomes a Quarto sidebar “section” with:

  * `section: "<master title>"`
  * `href: <ARTICLE_DIR>/<lang>/index.qmd`
  * `contents:` listing each `<ARTICLE_DIR>/<slug>/<lang>/index.qmd`

Suppression rule (applies to both copy/split)

* If the master front matter sets:
  `rhythmpress-preproc-sidebar: false`
  then `_sidebar-<lang>.yml` generation is suppressed.

Cleaning behavior (important)

* `rhythmpress preproc-clean <ARTICLE_DIR> --apply` removes most subdirectories under `<ARTICLE_DIR>/` **except** `attachments*/`.
* It also purges sidebar files in that directory by default: `_sidebar-*.yml` and `_sidebar-*.generated.*`. Those are expected to be regenerated later.

### 9.2 At the project root

Assume the Quarto project root contains `_quarto.yml`.

Author-managed

* `_rhythmpress.conf`
  Directory list used by `rhythmpress build` (one article directory per line).

* `_sidebar-<lang>.before.yml`, `_sidebar-<lang>.after.yml`
  Optional “bookends” included in the aggregated sidebar config. These are referenced by generated `.conf` files.

* Optional hook script:
  `_rhythmpress.hook-after._sidebar-<lang>.generated.yml.py`
  If present, it runs after `_sidebar-<lang>.generated.yml` is written (failures are ignored).

Generated (by the build pipeline)

* `_sidebar-<lang>.generated.conf`
  Produced by `rhythmpress sidebar_confs`. It contains a list of YAML sidebar fragments to merge:

  1. `_sidebar-<lang>.before.yml`
  2. all discovered per-article `_sidebar-<lang>.yml` paths
  3. `_sidebar-<lang>.after.yml`

* `_sidebar-<lang>.generated.yml`
  Produced by `rhythmpress render-sidebar` (via `yq`). This is the merged Quarto sidebar YAML.

* `_sidebar-<lang>.generated.md`
  Also produced by `rhythmpress render-sidebar`. It begins with a hard-coded header `**目次**` and appends the TOC rendered from the sidebar YAML.

Optional (only if you run it)

* A global navigation Markdown output from `rhythmpress render-nav`
  By default it prints to stdout; it only writes a file if you pass `--out <path>`.

### 9.3 Quarto output directories (not Rhythmpress, but always present in practice)

Generated by Quarto / preview tooling

* `.quarto/` and `.site/`
  Preview state directories (removed by `rhythmpress clean-start`).

* `_site/` (or your configured `project.output-dir`)
  Rendered site output.

Generated by Rhythmpress into Quarto output

* `<output-dir>/sitemap.xml` (default: `_site/sitemap.xml`)
  Created by `rhythmpress sitemap` after `quarto render` has produced HTML files.

If you want, the next section that naturally follows is “10. Safety and limitations” (where we explicitly warn about slug collisions, git-date strictness, running from project root, and the destructive clean rules).



## 10. Safety and limitations (high-visibility)

Rhythmpress is intentionally opinionated and, in a few places, intentionally strict. These constraints keep large Quarto sites predictable, but you should understand them up front.

Destructive cleaning is real

* `rhythmpress preproc-clean` deletes generated directories under an article directory. Treat it like `rm -rf` with guardrails.
* Cleaning is allowed only when the article directory contains the sentinel file `.article_dir`.
* Cleaning preserves only directories whose names start with `attachments` (e.g. `attachments/`, `attachments-images/`). Put durable assets there.

You SHOULD start by using `rhythmpress build --skip-clean` during active writing, and only run cleaning when you truly need a fresh regeneration.

Run commands from the project root
Many paths are resolved relative to the Quarto project root (the directory containing `_quarto.yml`). Some tools also rely on `RHYTHMPRESS_ROOT`.

* You SHOULD run Rhythmpress from the project root.
* You SHOULD activate the environment with `eval "$(rhythmpress eval)"` (or your alias) before using sidebar-related commands.
* If you run commands from elsewhere, you may generate files in unexpected places or see confusing “file not found” failures.

Git history is assumed (date extraction)
Rhythmpress injects `cdate` / `mdate` (created/modified) into generated pages by reading `git log`.

* Your project MUST be in a git repository for typical builds.
* Your master files SHOULD be committed; untracked or newly created files may cause date extraction to fail.
* If you want to author outside git, you should expect preprocessing failures unless you modify the date policy in code.

Split mode has slug collision risk
In split mode, each `##` (H2) heading becomes a page directory `<slug>/...`.

* If two headings produce the same slug, the generated output collides and one section overwrites the other.
* You SHOULD give important headings explicit IDs: `## Title {#unique-id}` to stabilize URLs and avoid collisions.
* Ruby titles (`<ruby>...`) are normalized; do not rely on `<rt>` content for uniqueness.

Front matter parsing is intentionally limited
`rhythmpress preproc` does not fully parse YAML for dispatch decisions. It uses line-based parsing for:

* `rhythmpress-preproc: ...`
* `rhythmpress-preproc-args: ...`

So:

* You SHOULD keep these keys simple (single-line scalars or simple lists).
* Avoid complex YAML constructs (multiline strings, anchors, exotic indentation) for these specific keys.

Two different “TOC” concepts exist
Rhythmpress can generate:

* a TOC derived from master headings (used in split mode and language index pages), and
* a TOC derived from Quarto sidebar YAML (via `render-sidebar` / `render-toc`).

They solve different problems. You SHOULD decide which navigation style you rely on and keep your pipeline consistent.

Sidebar generation depends on external tooling
`rhythmpress render-sidebar` requires:

* `yq` v4 (Mike Farah), because it uses `yq ea ...` merge behavior.

Without it, the sidebar pipeline will fail. Install `yq` explicitly and ensure it is the correct implementation/version.

“env” vs “eval” wording
Some older messages or examples may refer to `rhythmpress env`. In this codebase, the correct command is:

* `rhythmpress eval`

Always use:

```bash
eval "$(rhythmpress eval)"
```

Hard-coded Japanese TOC label
The generated Markdown TOC file starts with a fixed header:

* `**目次**`

If you need an English label (or per-language label), you will want to adjust that behavior in code or apply a post-processing hook.

If you want, I can turn this into an even more “high-visibility” block by rewriting it into a short “Read this first” section with the 5–6 most failure-prone rules, and push the rest into `docs/troubleshooting.md`.



## 11. Troubleshooting (short) + link

If something fails, it is almost always one of the cases below.

`rhythmpress: command not found`

* Cause: the package is not installed in the active environment, or your shell is not using that environment.
* Fix: activate your venv (`. .venv/bin/activate`) and reinstall (`pip install -e ...`), then retry.

`eval "$(rhythmpress eval)"` prints output but nothing changes

* Cause: you ran `rhythmpress eval` without `eval`, or you ran it in a non-POSIX-compatible context.
* Fix: run exactly `eval "$(rhythmpress eval)"` in the same shell session.

`render-sidebar` fails with `yq: command not found` or merge errors

* Cause: `yq` is missing or it is not the Mike Farah v4 implementation (the syntax differs across “yq” tools).
* Fix: install Mike Farah `yq` v4 and ensure `yq --version` reports v4.

Sidebar/TOC commands complain about `RHYTHMPRESS_ROOT`

* Cause: environment not activated for the project, or you are running from the wrong directory.
* Fix: from the Quarto project root, run `eval "$(rhythmpress eval)"` (or your alias), then retry.

Preprocessing fails around dates (`cdate`/`mdate`) or `git` errors

* Cause: Rhythmpress reads git history to inject created/modified dates; untracked files or non-git directories can break this.
* Fix: ensure the project is a git repo and commit the relevant master files before running preproc/build.

`preproc-clean` refuses to run

* Cause: the article directory does not contain the sentinel `.article_dir`.
* Fix: create it (or use `rhythmpress create-page` which scaffolds it), then retry. This is a safety feature.

“Why did it build twice?” / unexpected extra preproc runs

* Cause: the directory contains multiple masters (`master-en.*` and `master-ja.*`) and the build is correctly building all languages when `LANG_ID` is not set.
* Fix: set `LANG_ID=<lang>` to restrict the build to one language.

Files generated in unexpected locations / “file not found” despite the file existing

* Cause: running commands outside the Quarto project root so relative paths resolve incorrectly.
* Fix: `cd` to the project root (where `_quarto.yml` exists) and rerun.

For a fuller list (including common stack traces and how to interpret them), see `docs/troubleshooting.md`.


## 12. License / Contributing

License
Rhythmpress is licensed under the **MIT License** (as declared in `pyproject.toml`). If you plan to distribute this project publicly, you SHOULD add a top-level `LICENSE` file to make the license explicit for downstream users and packagers.

Contributing
External contributions are welcome, especially for:

* clearer documentation and examples
* dependency declaration improvements (runtime deps currently aren’t listed in `pyproject.toml`)
* safer/more explicit behavior around git-date extraction and split slug collisions
* portability improvements (macOS/Linux), and better error messages

Suggested workflow:

1. Fork the repository and create a feature branch.
2. Keep changes focused (one topic per PR).
3. Update documentation when behavior changes (README and/or `docs/*`).
4. Test the common flows locally:

   * `rhythmpress build` (with and without `LANG_ID`)
   * `rhythmpress preproc` on both copy and split masters
   * `rhythmpress render-sidebar` (requires `yq` v4)
   * `rhythmpress auto-rebuild` (requires `watchfiles`)
5. Avoid committing macOS metadata files (`._*`). If you develop on macOS, you SHOULD ensure your tarballs/commits do not include AppleDouble artifacts.

If you’re adding a new command, the convention is to add a script named `rhythmpress_<command>.py` (or `.sh`) under `src/rhythmpress/scripts/` so the CLI dispatcher can discover it automatically.



<!--
# from anywhere in Rhythmpress
from rhythmpress.quarto_vars import get_variables

vars_all = get_variables(lang="ja")

print(vars_all.get("RUBY-MOP"))

# with extra overrides
vars_en = get_variables(lang="en", extra={"site_url": "https://example.com"})
-->
