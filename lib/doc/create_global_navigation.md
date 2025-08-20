[ChatGPT](https://chatgpt.com/share/68a60069-b42c-8013-ad58-90f2058a5568)

Here’s the **finalized, minimal spec** for the Rhythmpedia dispatcher, aligned with your corrections (lang\_id mandatory, conf-first, simple output).

# Scope

Assemble a single, ready-to-include Markdown navigation from multiple article directories by delegating per-article TOC generation to `create_toc_v1()` or `create_toc_v5()` based on the master file’s front matter.

# Function

create\_global\_navigation(input\_conf, lang\_id, \*, strict=True, logger=None) -> str

# Inputs

* input\_conf: path to a conf file that lists directories. Order is preserved; this order defines output order.
* lang\_id (required): language selector used to choose the master file (`master-{lang_id}.qmd` or `.md`).
* strict (bool, default True): raises errors instead of warnings for defined failure cases.
* logger: callable or None. If None, log to stderr.

# Conf file format

* One directory name per line.
* Lines may include inline comments; everything from the first “#” to EOL is ignored.
* Blank / whitespace-only lines are ignored.
* Each entry must be a directory name **without any slashes** (no path separators).
* Symlinked directories are allowed and used as-is (no path resolution).
* Duplicates are permitted and processed in listed order.

# Master detection (per directory)

* Required candidates, in order:

  1. master-{lang\_id}.qmd
  2. master-{lang\_id}.md
* If neither exists:

  * warn+skip (or error if strict=True).
* If both exist for the same lang, prefer `.qmd`.
* Do **not** pass a language to `create_toc_v1/v5`; the effective language is implicit from the chosen filename’s suffix.

# Mode selection (per directory)

* Read YAML front matter from the chosen master using the existing front-matter reader.
* Key: `rhythmpedia-preproc`

  * Missing → default “copy”
  * Value “copy” → call `create_toc_v1(master_path)`
  * Value “split” → call `create_toc_v5(master_path)`
  * Unknown value → warn+skip (error if strict=True)

# Output contract

* Dispatcher does **not** transform v1/v5 results.
* Output is a **single Markdown string** formed by concatenating each article’s returned Markdown, in conf order, separated by a single blank line.
* No extra wrappers, headings, or metadata are injected by the dispatcher.

# Errors & strict mode

* Per-directory warn+skip (or error if strict=True) when:

  * Directory does not exist or is not a directory.
  * Master file not found for the given lang\_id.
  * Unknown `rhythmpedia-preproc` value.
* Conf-level validation:

  * Lines with path separators are rejected.
  * Lines ending with “.yml” / “.yaml” are rejected (case-insensitive).
* Process continues for other directories unless strict=True and a fatal error is encountered; return non-zero at CLI level when any error occurs in strict mode.

# Logging

* One concise status line per directory:
  DIR → MODE(copy|split) → v1|v5 → OK|SKIP|ERROR \[reason]
* Final summary:
  total=N, ok=K, skipped=S, errors=E

# Minimal algorithm

1. Read input\_conf; strip inline comments; drop blank lines; validate entries (no slashes).
2. Iterate directories in order:

   * Validate dir.
   * Pick master-{lang\_id}.qmd|.md (prefer .qmd).
   * Read front matter; get `rhythmpedia-preproc` (default “copy”).
   * Map to v1/v5; call with the master path.
   * Append the returned Markdown.
   * Log status.
3. Join article markdown blocks with a single blank line.
4. Emit summary and return the Markdown string.

# CLI (dedicated, not embedded elsewhere)

* Command: rhythmpedia render-toc --conf \_rhythmpedia.conf --lang LANG \[--strict] \[--output FILE]

  * \--conf: required path to conf file.
  * \--lang: required language id (e.g., ja).
  * \--strict: toggles strict mode (default on).
  * \--output: if set, write Markdown there; else print to stdout.
* Exit code: 0 on success; non-zero if any error under strict mode (or if nothing produced).

# Non-goals

* No mutation of source files.
* No inference of language when lang\_id is omitted (lang\_id is always mandatory).
* No JSON or structured wrapper output from the dispatcher.
* No slug generation, no formatting transforms—those belong outside the dispatcher.

---

## Related next steps you may want

* Tiny renderer helpers (optional): utilities that, when needed elsewhere, can add headings per article or convert the aggregated Markdown into Quarto sidebar YAML—kept **separate** from the dispatcher.
* Unit tests: cover “missing master”, “unknown preproc”, “both qmd/md exist”, “symlinked dir”, and “duplicates in conf”.

## Background (why this is lean)

* Mandatory `lang_id` and conf-first input remove ambiguity.
* Front-matter-driven mode keeps the dispatcher stateless and future-proof.
* Pure Markdown passthrough prevents bloat and fragile transformations.


