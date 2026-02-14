# Workflows

This document is about *how you actually use Rhythmpress day-to-day* (not the full spec). For terminology and definitions, see `docs/concepts.md`. For exact flags and exit behaviors, see `docs/commands.md`.

Most workflows assume you are at the **Quarto project root** (the directory that contains `_quarto.yml` and typically `.venv/`).

---

## 0) First: activate the project environment (recommended)

Some commands (especially sidebar generation) require `RHYTHMPRESS_ROOT` to be set.

If you use the alias you mentioned, that’s perfect:

```sh
rhythmpress_activate
# (your alias)
# alias rhythmpress_activate='. .venv/bin/activate; eval "$(rhythmpress eval)"'
````

If you don’t use the alias, the equivalent is:

```sh
. .venv/bin/activate
eval "$(rhythmpress eval)"
```

Notes:

* `rhythmpress eval` sets `RHYTHMPRESS_ROOT` to the current directory and also adjusts your prompt and PATH.
* If you forget this step, `render-sidebar` (and anything that depends on it) will fail with “RHYTHMPRESS_ROOT is not set”.

---

## 1) Create a new page directory → write master → preprocess

The typical first workflow is:

1. Create a page directory scaffold:

```sh
rhythmpress create-page my-topic
# creates:
#   my-topic/.article_dir
#   my-topic/.gitignore
#   my-topic/master-ja.qmd   (default language is ja)
```

If you want the first master in English:

```sh
rhythmpress create-page my-topic --lang en
# creates master-en.qmd instead
```

2. Edit the master:

```sh
$EDITOR my-topic/master-ja.qmd
```

3. Important: Git dates are required
   Preprocessing injects `cdate` and `mdate` using Git history. If the master has **no commits yet**, preprocessing will fail.

So for a brand-new master, do an initial commit at least once:

```sh
git add my-topic/master-ja.qmd
git commit -m "Add my-topic master (ja)"
```

4. Preprocess just that directory:

```sh
rhythmpress preproc my-topic
```

What you get (in the common “copy” mode):

* `my-topic/ja/index.qmd`
* `my-topic/_sidebar-ja.yml`

---

## 2) Fast edit loop for one page

When you are actively writing one page, keep it simple:

* Edit the master
* Run preproc for that directory again

```sh
rhythmpress preproc my-topic
```

Because preprocessing tries hard to be idempotent (only touching outputs when content changes), it stays friendly with `quarto preview`.

Tip: if you only changed a title/date/front matter and want to ensure outputs are updated, just rerun `preproc` again—no special “force” flag exists for `preproc`.

---

## 3) Preview the site while you work

### Option A: run Quarto directly

```sh
quarto preview
```

(Quarto watches project files and serves a local preview.)

### Option B: use Rhythmpress helpers

These helpers activate the venv and start preview:

```sh
rhythmpress start
```

If you want to wipe `.site/` and `.quarto/` before preview:

```sh
rhythmpress clean-start
```

---

## 4) Recommended “real project” workflow: build multiple directories

Once you have more than a handful of pages, you normally keep a build definition file.

1. Create or edit `_rhythmpress.conf` at the project root:

```txt
# one directory per line
hypergroove/benefits-of-hypergroove-theory
hypergroove/the-four-principles-of-groove
hypergroove/tatenori-theory   # inline comments like this are allowed if preceded by " # "
```

2. Run the batch builder:

```sh
rhythmpress build
```

What `rhythmpress build` does (default behavior):

* Runs `preproc-clean <dir> --apply --force` for each listed directory
* Runs `preproc <dir>` for each listed directory
* Generates aggregated sidebar confs (`sidebar-confs`)
* Renders sidebars (`render-sidebar`) per language it finds

This is *destructive* by design: it cleans generated subdirectories inside each article directory.

---

## 5) Safe cleaning vs “skip-clean” during writing

### When you want a clean rebuild (default)

```sh
rhythmpress build
```

This uses `preproc-clean` internally and will delete generated directories inside article directories. Attachments are protected if they live in `attachments*/` directories.

### When you want speed (common during writing)

Use:

```sh
rhythmpress build --skip-clean
```

This keeps existing generated folders and just regenerates what changed.

### Clean only (no preprocessing, no sidebars)

Sometimes you just want to wipe generated dirs across all targets:

```sh
rhythmpress build --clean-only
```

---

## 6) Two-terminal dev loop (auto rebuild + preview)

This is the “edit masters → auto rebuild outputs → preview updates” loop.

Terminal A (preview):

```sh
rhythmpress_activate
quarto preview
```

Terminal B (watch masters and rebuild):

```sh
rhythmpress_activate
rhythmpress auto-rebuild
```

What the watcher does:

* It only reacts to changes to `master-*.qmd` / `master-*.md`
* It ignores `.git/`, `.venv/`, `_site/`, `.quarto/`, etc.
* When triggered, it runs:

```sh
rhythmpress build --skip-clean
```

So it’s fast and safe for iterative writing.

---

## 7) Multilingual workflows

### A) One article directory, one language

If the directory only has `master-en.qmd`, you can just run:

```sh
rhythmpress preproc my-topic
```

### B) One article directory, multiple masters (e.g., `master-en.qmd` + `master-ja.qmd`)

In this case, `preproc` requires you to choose a language via `LANG_ID`:

```sh
LANG_ID=en rhythmpress preproc my-topic
LANG_ID=ja rhythmpress preproc my-topic
```

If you forget, `preproc` will error with “Ambiguous… Set $LANG_ID.”

### C) Project-wide build across languages (recommended)

`rhythmpress build` has special logic:

* If multiple `master-<lang>.*` exist in a directory and `LANG_ID` is not set, it builds **all** detected languages for that directory.
* If `LANG_ID` is set, it builds only that language and validates it exists (when masters exist).

So:

Build everything in all languages:

```sh
unset LANG_ID
rhythmpress build
```

Build only English across the project:

```sh
export LANG_ID=en
rhythmpress build
```

### D) Add a new language later

Typical pattern:

1. Add `master-<newlang>.qmd` to relevant directories (or start with just one directory)
2. Commit the new master at least once (Git dates!)
3. Run build (or per-dir preproc with `LANG_ID=<newlang>`)

---

## 8) Sidebar workflows

### A) Normal case: just use `build`

`rhythmpress build` already:

* Aggregates per-directory `_sidebar-<lang>.yml`
* Produces root `_sidebar-<lang>.generated.conf`
* Renders `_sidebar-<lang>.generated.yml` and `_sidebar-<lang>.generated.md`

So most of the time you do nothing special.

### B) If you only changed sidebar YAMLs and want to rerender quickly

You can manually rerun:

```sh
rhythmpress sidebar-confs --defs _rhythmpress.conf
rhythmpress render-sidebar _sidebar-ja.generated.conf
rhythmpress render-sidebar _sidebar-en.generated.conf
```

(Replace languages as needed.)

Reminder: `render-sidebar` requires `RHYTHMPRESS_ROOT`, so ensure you activated the project environment.

---

## 9) CI build workflow (minimal, reliable)

A common CI sequence is:

1. Checkout repo (must include `.git` history enough for Git dates)
2. Set up Python + install Rhythmpress + dependencies
3. Ensure `yq` (Mike Farah v4) is installed (for sidebar merging)
4. Activate environment variables for the job shell
5. Run Rhythmpress build
6. Run Quarto render
7. Generate sitemap (optional)

Skeleton:

```sh
. .venv/bin/activate
eval "$(rhythmpress eval)"

rhythmpress build
quarto render
rhythmpress sitemap
```

Notes:

* If CI uses a shallow clone with missing history, Git date extraction may break. Use a checkout strategy that preserves file history enough for `git log --follow` to work.
* If you don’t need sidebars in CI for some reason, you can run:
  `rhythmpress build --no-sidebar`
  (but most sites do want them.)

---

## 10) Workflow “sanity checks” when something feels off

If outputs look stale or missing:

* Confirm you ran in the Quarto project root.
* Confirm you activated the project environment (so `RHYTHMPRESS_ROOT` is set).
* Confirm the master file has at least one Git commit.
* Confirm the directory has `.article_dir` (required for cleaning).
* Confirm `LANG_ID` is set when multiple masters exist and you’re using `preproc` directly.

For concrete error → fix mappings, see `docs/troubleshooting.md`.

```
::contentReference[oaicite:0]{index=0}
```


