# Troubleshooting

This is a short, practical list of the most common failures and how to fix them. If you want the exact CLI syntax for a command, see `docs/commands.md`.

## 0) Fast triage checklist (do this first)

When something feels “impossible,” check these in order:

1) You are in the **Quarto project root** (the directory that contains `_quarto.yml`).
2) Your venv is active and `rhythmpress` resolves to that venv:
   - `which rhythmpress`
3) `RHYTHMPRESS_ROOT` is set:
   - `echo "$RHYTHMPRESS_ROOT"`
4) If the directory has multiple masters (`master-en.*`, `master-ja.*`), you set:
   - `echo "$LANG_ID"`
5) The master file you are preprocessing has at least one Git commit.

If any of these fail, fix them first before chasing deeper errors.

---

## 1) `rhythmpress: command not found`

Likely causes:
- Your venv is not activated.
- Rhythmpress is not installed into the active venv.
- You are in a different terminal session than the one you installed into.

Fix:
```sh
. .venv/bin/activate
python -m pip install -U pip
pip install -e /path/to/rhythmpress
rhythmpress list
````

---

## 2) `RHYTHMPRESS_ROOT not set` (usually during sidebar/TOC steps)

Likely causes:

* You didn’t run `eval "$(rhythmpress eval)"`.
* You ran it in a different shell session than the command failing.
* You ran it from a directory that is not the project root.

Fix (from project root):

```sh
cd /path/to/project-root
eval "$(rhythmpress eval)"
# or your alias:
rhythmpress_activate
```

Note: if a script tells you to run `eval "$(rhythmpress env)"`, read it as `eval "$(rhythmpress eval)"` (stale hint text).

---

## 3) “Ran from the wrong directory” symptoms (paths look wrong / files not found)

Typical symptoms:

* Outputs appear in unexpected locations.
* `render-sidebar` can’t find its `.conf` or included YAML fragments.
* `render-toc` can’t resolve QMD paths.

Fix:

* Always run from the project root (where `_quarto.yml` exists), or use `--chdir` where supported.
* Activate project env from the root so `RHYTHMPRESS_ROOT` points to the correct place.

---

## 4) `Ambiguous masters` / `LANG_ID not set`

Typical symptom:

* `rhythmpress preproc <dir>` fails because the directory contains more than one `master-<lang>.*`.

Why:

* `preproc` needs to know which language to pick when multiple masters exist.

Fix:

```sh
LANG_ID=en rhythmpress preproc path/to/article-dir
LANG_ID=ja rhythmpress preproc path/to/article-dir
```

Related note (common confusion):

* `rhythmpress build` behaves differently: if `LANG_ID` is **not** set and multiple masters exist, build usually processes **all** languages by design.

---

## 5) “Why did it build twice?” / “It feels like duplicate work”

Most common reason:

* You have both `master-en.*` and `master-ja.*`, and `build` is correctly building **both** languages when `LANG_ID` is not set.

How to confirm:

* Look for logs like “multiple masters … LANG_ID not set → building all”.

Fix:

```sh
LANG_ID=en rhythmpress build --skip-clean
# or
LANG_ID=ja rhythmpress build --skip-clean
```

If you are using `auto-rebuild`, also remember it triggers `build --skip-clean` on each master edit; if you save two files (or an editor saves via temp files), you may see multiple triggers.

---

## 6) Git date extraction fails (`cdate`/`mdate` errors, or `git` errors)

Typical symptoms:

* Preprocessing fails with an error around `git log` or date extraction.
* Brand-new masters fail to preprocess.

Why:

* Current policy injects `cdate` and `mdate` from Git history. No commit → no history.

Fix (local dev):

```sh
git add path/to/master-xx.qmd
git commit -m "Add master"
rhythmpress preproc path/to/article-dir
```

Fix (CI):

* Avoid ultra-shallow checkouts that break `git log --follow`.
* Ensure the relevant files exist in history for the commit being built.

---

## 7) `yq` is missing or wrong implementation (sidebar merge fails)

Typical symptoms:

* `render-sidebar` fails with `yq: command not found`.
* Or: `yq ea ...` syntax errors.

Why:

* Rhythmpress expects **Mike Farah yq v4**. Other “yq” tools are incompatible.

Fix:

* Install Mike Farah `yq` v4 and verify:

  * `yq --version` shows v4.

Then rerun:

```sh
rhythmpress_activate
rhythmpress render-sidebar _sidebar-ja.generated.conf
```

---

## 8) `auto-rebuild` fails (watcher errors)

Typical symptoms:

* `ModuleNotFoundError: watchfiles`
* Watcher starts but never triggers.

Fix:

```sh
pip install watchfiles
rhythmpress auto-rebuild
```

If it triggers too often:

* Your editor may write temporary swap/backup files or “format on save” may touch many masters.
* Prefer watching masters only (default) and avoid tooling that rewrites multiple files per save.

---

## 9) Split mode generates nothing (or missing section pages)

Typical symptoms:

* No `<slug>/<lang>/index.qmd` files appear.
* Only a minimal language index is generated.

Likely causes:

* Your master has no H2 headings (`## ...`), and split mode splits on H2.

Fix:

* Add at least one `##` section heading.
* Or switch to copy mode:

  * `rhythmpress-preproc: copy`

---

## 10) Split mode slug collisions (sections overwrite each other)

Typical symptoms:

* A section page “disappears” or gets overwritten.
* Two different `##` headings map to the same output directory.

Fix:

* Assign explicit IDs to headings:

  * `## My Title {#unique-id}`

Do this especially for:

* repeated headings like “Overview”
* headings that normalize similarly
* headings with Ruby markup where readings might be ignored for slugging

---

## 11) `preproc-clean` refuses to run

Typical symptoms:

* It prints safeguards and refuses to delete.
* It runs but does not delete anything.

Likely causes:

* Missing `.article_dir` sentinel in the target directory.
* You did not pass `--apply` (dry-run mode).
* Target path is refused (symlink, `/`, `$HOME`, `.git`, etc.).

Fix:

```sh
# create sentinel if you intentionally want this directory to be cleanable
touch path/to/article-dir/.article_dir

# then actually clean
rhythmpress preproc-clean path/to/article-dir --apply --force
```

---

## 12) Sitemap generation fails (`output dir not found`, empty sitemap, wrong URLs)

Typical symptoms:

* `rhythmpress sitemap` fails because it cannot find the Quarto output directory.
* URLs are `https://example.com/...` unexpectedly.

Why:

* `sitemap` expects the rendered HTML to already exist.

Fix:

```sh
quarto render
rhythmpress sitemap
```

If URLs are wrong:

* Set `SITE_URL` or configure `website.site-url` in `_quarto.yml`:

```sh
SITE_URL="https://your-domain.example" rhythmpress sitemap
```

If output dir is custom:

```sh
QUARTO_PROJECT_OUTPUT_DIR="your-output-dir" rhythmpress sitemap
```

---

## 13) Sidebar TOC include shows but looks “wrong”

Typical symptoms:

* The included TOC header is in Japanese (`**目次**`) even on English pages.
* Links appear but labels are odd.

Why:

* `render-sidebar` currently writes a fixed `**目次**` label.
* TOC label/title resolution depends on file front matter titles / H1 / path fallback.

Fix:

* Treat this as a customization point:

  * Adjust the script behavior, or
  * Use the post-merge hook to rewrite labels, or
  * Ensure each generated/target page has a good `title:` in front matter.

---

## 14) Still stuck?

When asking for help, include:

* the exact command you ran
* the first ~30 lines around the error
* whether `LANG_ID` is set
* `pwd`, `echo "$RHYTHMPRESS_ROOT"`, and `ls` of the directory you are operating on

See also:

* `docs/commands.md` (exact command behavior)
* `docs/configuration.md` (vars, hooks, config formats)
* `docs/concepts.md` (mental model + artifacts)


