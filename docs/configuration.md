# Configuration

This document lists every user-facing “knob” Rhythmpress currently exposes: the definition file (`_rhythmpress.conf`), sidebar-related config files, supported front matter keys, environment variables, and hook points.

---

## 1) Project activation (required for most workflows)

Rhythmpress expects a project root context (mainly `RHYTHMPRESS_ROOT` and `PATH` updates) so it can resolve relative paths reliably.

The canonical activation is:

```sh
eval "$(rhythmpress eval)"
````

If you also activate a Python virtual environment, a practical pattern (as you described) is:

```sh
alias rhythmpress_activate='. .venv/bin/activate; eval "$(rhythmpress eval)"'
```

What `rhythmpress eval` does:

* Sets `RHYTHMPRESS_ROOT` to the current directory.
* Optionally sets `RHYTHMPRESS_TITLE` from `_quarto.yml` (reads `project.title` first, then `title`).
* Prepends `$RHYTHMPRESS_ROOT/bin` to `PATH` (idempotently).
* Adjusts shell prompt (interactive shells).
* Defines `rhythmpress_deactivate` to undo the project-only changes.

Notes:

* Many scripts *require* `RHYTHMPRESS_ROOT` (especially sidebar generation).
* Run `eval "$(rhythmpress eval -k)"` to emit deactivation code (or use `rhythmpress_deactivate` if defined).

---

## 2) Target definition file: `_rhythmpress.conf`

This file tells Rhythmpress which top-level content directories are “build targets” (e.g. `hypergroove`, `phonorhythmo`, etc.). Multiple commands read this file (not just `build`).

### 2.1 Format

`_rhythmpress.conf` is a plain text list:

* One directory per line.
* Blank lines are ignored.
* Lines starting with `#` are ignored.
* Inline comments are supported only when written as `#` (a space before `#`), to avoid clobbering strings that may legitimately contain `#`.

Example:

```txt
# Build targets
hypergroove
phonorhythmo  # experimental
rhythmdo-core
```

### 2.2 Where it is used

* `rhythmpress build --defs _rhythmpress.conf`
* `rhythmpress sidebar_confs --defs _rhythmpress.conf`
* `rhythmpress sidebar_langs --defs _rhythmpress.conf`
* `rhythmpress render_nav --defs _rhythmpress.conf ...`

### 2.3 Alternate input

Some commands accept `--defs -` to read the same format from stdin:

```sh
printf '%s\n' hypergroove phonorhythmo | rhythmpress build --defs -
```

---

## 3) Sidebar configuration

Rhythmpress treats sidebars as a merge of multiple YAML fragments, then generates:

1. a merged Quarto sidebar YAML (`_sidebar-<lang>.generated.yml`), and
2. a readable Markdown TOC (`_sidebar-<lang>.generated.md`) derived from that sidebar structure.

### 3.1 The pieces (what you edit vs what is generated)

User-maintained (optional but typical):

* `_sidebar-<lang>.before.yml`
  “Prefix” fragment to be merged first (global items you always want at the top).

* `_sidebar-<lang>.after.yml`
  “Suffix” fragment merged last (global items you always want at the bottom).

Generated (do not hand-edit; they may be overwritten):

* Per target dir (inside each build target like `hypergroove/`):

  * `_sidebar-<lang>.yml` (emitted by preprocessors when sidebar generation is enabled)

* At project root:

  * `_sidebar-<lang>.generated.conf` (list of YAML fragments to merge)
  * `_sidebar-<lang>.generated.yml` (merged YAML via `yq`)
  * `_sidebar-<lang>.generated.md` (Markdown TOC derived from the merged YAML)

### 3.2 The “conf” format for sidebar merging

Files like `_sidebar-ja.generated.conf` are *lists of YAML file paths*, one per line (comments allowed). They are consumed by `rhythmpress_render_sidebar.sh`.

Important behavior:

* The script changes directory to the directory containing the conf file.

  * Therefore, relative paths in the conf file are interpreted relative to the conf file’s directory.
  * In the default pipeline, the generated conf lives in the project root, so paths are typically root-relative.

Example `_sidebar-ja.generated.conf`:

```txt
# Global
_sidebar-ja.before.yml

# From each build target dir (generated)
hypergroove/_sidebar-ja.yml
phonorhythmo/_sidebar-ja.yml

# Global
_sidebar-ja.after.yml
```

### 3.3 Merge semantics (yq)

`rhythmpress_render_sidebar.sh` merges all listed YAML fragments using `yq` v4 (Mike Farah):

* Deep merge
* “Last wins” when keys overlap

This produces `_sidebar-<lang>.generated.yml`.

### 3.4 Required YAML shape (what Rhythmpress reads)

For TOC generation, Rhythmpress expects sidebar YAMLs to contain:

* `website.sidebar.contents` as the primary list to traverse

Typical shape:

```yml
website:
  sidebar:
    contents:
      - href: /hypergroove/ja/
        text: Hypergroove
      - section: Concepts
        contents:
          - /hypergroove/tatenori-theory/ja/index.qmd
          - /hypergroove/the-four-principles-of-groove/ja/index.qmd
```

Supported entry styles (practical summary):

* String leaves: a path to a QMD/MD file (used to derive title).
* Object leaves:

  * `{ href: "...", text: "..." }` (text is used if a title cannot be derived from the file)
* Section objects:

  * `{ section: "...", contents: [ ... ] }`

The Markdown TOC generator resolves titles for file leaves by:

1. file front matter `title` (string), else
2. first ATX H1 (`# ...`), else
3. path fallback.

---

## 4) Supported front matter keys (masters)

Rhythmpress reads a small set of keys from *master files* (`master-<lang>.qmd` / `.md`) to control preprocessing.

### 4.1 `rhythmpress-preproc`

Controls which preprocessor runs when you call:

```sh
rhythmpress preproc <dir>
```

Supported values (current codebase):

* `copy` (default)
* `split`

Example:

```yml
---
title: My Section
rhythmpress-preproc: split
---
```

### 4.2 `rhythmpress-preproc-args`

Extra args forwarded to the underlying preprocessor.

Two supported styles:

Inline list:

```yml
rhythmpress-preproc-args: ["--no-toc"]
```

Block list:

```yml
rhythmpress-preproc-args:
  - --no-toc
```

### 4.3 `rhythmpress-preproc-sidebar`

This is read by the preprocessors (`copy` / `split`) to decide whether to generate sidebar YAML for that target.

Example:

```yml
rhythmpress-preproc-sidebar: true
```

If false, you still get page outputs, but sidebar YAML emission is suppressed for that directory.

### 4.4 Notes on parsing limitations (important edge case)

The `rhythmpress preproc` dispatcher uses a lightweight front matter reader specifically for the keys above. In practice:

* Keep `rhythmpress-preproc` and `rhythmpress-preproc-args` as simple scalars/lists.
* Avoid clever YAML constructs for those two keys (anchors, multiline objects, etc.).
* Other front matter keys are handled elsewhere (often via PyYAML), but the dispatcher’s routing depends on these exact keys being readable.

---

## 5) Environment variables

### 5.1 Core variables

* `RHYTHMPRESS_ROOT`
  Project root. Required by sidebar generation and TOC rendering when paths must be resolved to the project.

* `RHYTHMPRESS_TITLE`
  Optional. Used mainly for prompt decoration; usually derived from `_quarto.yml`.

* `LANG_ID`
  Controls language selection in several places.

  * `rhythmpress preproc` uses it to pick `master-<LANG_ID>.qmd/md`.
  * `rhythmpress build` uses it as an override; if unset and multiple `master-<lang>` exist, it builds all languages.

### 5.2 Sitemap-related variables (used by `rhythmpress sitemap`)

* `QUARTO_PROJECT_OUTPUT_DIR`
  Overrides `_quarto.yml` `project.output-dir` when locating the rendered site directory.

* `SITE_URL`
  Overrides `_quarto.yml` `website.site-url` when writing absolute URLs.

---

## 6) Variable interpolation (`{{< var ... >}}`) used in titles/TOC

Rhythmpress interpolates Quarto-style variable placeholders inside certain strings (notably titles used for TOC generation):

* `{{< var foo.bar >}}`
* `{{< var env:HOME >}}`

Resolution sources (merge order):

1. `_quarto.yml` (project/website vars that Rhythmpress extracts)
2. `_variables.yml` / `_variables.yaml` / `_variables.json` (if present)
3. `_variables-<lang>.yml|yaml|json` (if present and language is known)
4. Environment variables that start with `RHYTHMPRESS_`

   * Exposed as lowercase keys without the prefix
     Example: `RHYTHMPRESS_PRODUCT_NAME=Rhythmpress` → `{{< var product_name >}}`

`env:NAME` reads directly from the process environment (not from the merged variable map).

Operational note (edge case):

* Interpolation is most reliable when you run commands from the project root (or with `RHYTHMPRESS_ROOT` set), because variable loading detects the project root by searching for `_quarto.yml`.

---

## 7) Hooks

### 7.1 Post-merge sidebar hook

After `_sidebar-<lang>.generated.yml` is produced, `rhythmpress_render_sidebar.sh` will run an optional Python hook if it exists:

Filename pattern:

* `_rhythmpress.hook-after._sidebar-<lang>.generated.yml.py`

Invocation:

```txt
python3 <hook_file> <generated_yml> <lang_id> <conf_basename>
```

Important behavior:

* The hook runs in the directory that contains the sidebar conf.
* Hook failures are ignored (`|| true`), so it will not fail your build by default.
* Use this for final normalization (e.g., rewriting/patching YAML to match a project-specific Quarto layout).

---

## 8) Safety-related “configuration” (cleaning)

Some operations are intentionally guarded.

### 8.1 `.article_dir` sentinel for clean

`rhythmpress preproc_clean` refuses to delete directories unless a sentinel file exists:

* Default sentinel: `.article_dir`
* You can override via `--sentinel <name>`

This guard is designed to prevent catastrophic deletes (e.g., running clean in the wrong directory).

It also supports sidebar purge behavior:

* By default it will delete sidebar files in the target dir (`--purge-sidebars` is enabled by default).
* You can keep them with `--no-purge-sidebars`.
* You can limit purge to one language with `--lang <lang>`.

(Full CLI details belong in `docs/commands.md`, but these flags effectively behave like “configuration” for safe operation.)


