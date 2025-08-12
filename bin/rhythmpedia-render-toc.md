Got it. Here’s the **final, consolidated full specification** you asked for—clean, self-contained, and ready to implement.

# Sidebar → Markdown TOC Generator (Full Spec, v2.1 Final)

## 1) Purpose

Generate a **Markdown table of contents** (nested lists) from one or more Quarto sidebar YAML files, preserving hierarchy and authorial order, and linking to **directory URLs** (never explicit filenames).
**Leaf titles** are resolved from their **QMD/MD source**; inline HTML is preserved. For object-form leaves, `{text}` is only a **fallback** when the file title cannot be obtained.

## 2) Inputs

### 2.1 `_sidebar.conf`

* One relative path per line to a sidebar YAML file, in **merge order**.
* Blank lines and `#` comments are ignored.
* Paths are resolved **relative to project root** (see §4).

### 2.2 Sidebar YAMLs

Read only `website.sidebar.contents`. Supported item shapes:

1. **String path**

   * **Directory** (preferred): `article/ja/`
   * **File**: `article/page.qmd` or `article/page.md`

2. **Section object**

   ```yaml
   - section: "Title (may include <ruby>…</ruby>)"
     contents:
       - …
   ```

3. **Object-form leaf**

   ```yaml
   - href: article/ja/          # or article/page.qmd|.md
     text: "Optional label"     # used only if file title can't be obtained
   ```

   * Path key search order: `href` → `path` → `file` → first string value in the object.
   * Additional keys are ignored.

## 3) Output

* A **Markdown** nested list written to **stdout** (commonly redirected to `_toc.md`).
* **Sections** render as plain bullets.
* **Leaves** render as Markdown links with **directory-style** hrefs.

Example:

```md
- 多層弱拍基軸律動
  - [Benefits of Multi-layered…](/beat-orientation/benefits-of…/ja/)
  - [Mechanism of Tatenori](/beat-orientation/mechanism-of-tatenori/ja/)
```

## 4) Working Directory & Path Resolution

* **Project root** = parent of the script directory (`bin/..`), derived from `__file__` and following symlinks.
* All paths in `_sidebar.conf` and YAML are interpreted **relative to project root**.

### 4.1 Interpreting items

* **Directory items** (path ends with `/` **or** is an actual directory on disk):

  * Source file to read title from: `<dir>/index.qmd`, else `<dir>/index.md` (prefer `.qmd` if both).
  * Link href: `/<dir>/` (leading + trailing slash).
* **File items** (`*.qmd` or `*.md`):

  * Source file: the file itself.
  * Link href (directory-style): `/parent/file-stem/`.

### 4.2 Href normalization (strict)

* Always **leading `/`**.
* Collapse duplicate slashes.
* Resolve `.` and `..` segments.
* **Enforce trailing `/`**.

## 5) Merge Semantics (intentionally simple)

* Concatenate **only** the root arrays `website.sidebar.contents` from each YAML, respecting `_sidebar.conf` order.
* **No merging** at any depth; keep branches independent.
* **No deduplication**; duplicates may appear under multiple branches.

## 6) Title Resolution (leaf items)

Resolution order:

1. **Front matter `title` (string)** in QMD/MD — keep inline HTML intact.
2. First **ATX H1** (`^#\s+…`) in body — keep inline HTML intact. (Setext H1 is ignored to avoid accidental matches.)
3. **Path-based fallback:**

   * If the last path segment is a recognized **language tail** (default: `ja`, `en`), use the **parent’s last segment** instead.
   * Otherwise, use the **last non-empty segment**.
   * Convert hyphen/underscore to spaces, title-case heuristically (implementation choice).
4. **Final fallback:** `"untitled"`.

**Object-form leaves `{text, href}`**

* If the file is **readable** and has a **front-matter title** or **H1**, use that and **ignore** `text`.
* If unreadable/missing/no title/H1 → use `text` if present; else apply step 3 → step 4.

**Section titles**

* Literal from YAML `section`. Inline HTML is preserved.

## 7) Rendering Rules

* **Indentation:** 2 spaces per depth level.
* **Section node:** `- {section-title}` then recursively render `contents` one level deeper.
* **Leaf node:** `- [{resolved title}]({normalized-href})`
* Preserve ordering from YAML (and `_sidebar.conf` concatenation order).

## 8) Errors & Warnings

* Missing YAML listed in `_sidebar.conf`: **warn to stderr**, continue.
* YAML lacking `website.sidebar.contents`: **skip silently**.
* Missing QMD/MD for a leaf:

  * Still emit the link (computed from the path).
  * Title resolution falls back: `{text}` (object leaves) → path segment → `"untitled"`.
  * **Warn to stderr**. Include provenance (source YAML path; **line number if available**).
* Unknown dict at leaf level:

  * Attempt path extraction per key order; otherwise **warn** and **skip**.

> **Provenance note:** If you want line numbers, parse YAML with a loader that records node positions (e.g., `ruamel.yaml`). If unavailable, omit line numbers gracefully.

## 9) File Types & Parsing

### 9.1 QMD/MD parity

* Treat **`.md`** and **`.qmd`** identically for title extraction.
* Prefer `index.qmd` over `index.md` when both exist in a directory.

### 9.2 Title extraction details

* **Front matter:** Parse YAML block delimited by `---`/`...` (BOM permitted).

  * Use only scalar **string** `title`; if not a string (array/object), **skip** to H1.
* **H1 detection:** First line matching `^#\s+(.+?)\s*$`. Preserve inline HTML. Ignore setext H1 (`===`) to avoid false positives.

## 10) Performance & Caching

* Complexity is linear in item count; I/O dominated by file reads.
* Optional persistent cache: `{abs_path: {title: str, mtime: int, size: int}}`.

  * Validate cache entry by `(mtime, size)` on each run.

## 11) Constraints & Assumptions

* Authoring favors paths like `article-title/ja/`.
* No implicit **language filtering**; render exactly what YAML provides.
* Links are **always directory-style** (no `.html`).
* UTF-8 throughout; normalize line endings to `\n`.

## 12) CLI & Integration

### 12.1 Command

```bash
python bin/build_toc_md.py _sidebar.conf > _toc.md
```

### 12.2 Include in Quarto page(s)

```qmd
{ { < include _toc.md > } }
```

### 12.3 Pre-render hook

```yaml
project:
  pre-render: bin/pre_render.sh
```

`bin/pre_render.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
python bin/build_toc_md.py _sidebar.conf > _toc.md
```

## 13) Acceptance Matrix (Conformance)

1. **Directory leaf** `foo/ja/`

   * Reads `foo/ja/index.qmd` or `.md`; href `/foo/ja/`; title from file (HTML allowed).
2. **File leaf** `foo/page.qmd` or `.md`

   * Href `/foo/page/`; title from file (HTML allowed).
3. **Object leaf `{href, text}`**

   * File present with title/H1 → use file title; ignore `text`.
   * File missing/untitled → use `text`; else path fallback; else `"untitled"`.
4. **Language tail** `/ja/` last segment → fallback uses **parent** segment.
5. **Section HTML** (e.g., `<ruby>…</ruby>`) is preserved in output.
6. **Duplicates** under multiple sections are all rendered.
7. **Missing YAML** or empty `contents` handled per §8.
8. **Unknown leaf object** with no resolvable path → warn & skip.
9. **Unicode paths** & spaces render correctly in hrefs and titles.
10. **Href normalization**: leading slash, trailing slash, no `.`/`..`, no double slashes.

## 14) Extension Hooks (future-proof)

* `--strict` → missing file becomes an **error** (non-zero exit).
* `--prune-empty` → drop sections with no printable descendants.
* `--root <path>` → override project root detection.
* `--langs ja,en,th` → configure language tails for fallback step.
* `--prefer-title qmd|yaml` → if `yaml`, object leaves prefer `{text}` even when file exists (default: `qmd`).
* `--allow-md` (default **on**) → keep `.md` parity with `.qmd`.
* Title cache path override (e.g., `--cache .toc_title_cache.json`).

## 15) Examples

### 15.1 `_sidebar.conf`

```
_sidebar.before.yml
beat-orientation/_quarto.index.ja.yml
_sidebar.after.yml
```

### 15.2 YAML (excerpt)

```yaml
website:
  sidebar:
    contents:
      - section: "<ruby><rb>多層弱拍基軸律動</rb><rt>グルーヴィ</rt></ruby>"
        contents:
          - beat-orientation/benefits-of-multi-layered-weak-beat-oriented-rhythm-theory/ja/
          - beat-orientation/mechanism-of-tatenori/ja/
      - href: beat-orientation/letter-to-native-mora-timed-speakers/ja/
        text: "Letter (used only if file has no title)"
```

### 15.3 Rendered Markdown

```md
- <ruby><rb>多層弱拍基軸律動</rb><rt>グルーヴィ</rt></ruby>
  - [Benefits of Multi-layered Weak-Beat Oriented Rhythm Theory](/beat-orientation/benefits-of-multi-layered-weak-beat-oriented-rhythm-theory/ja/)
  - [Mechanism of Tatenori](/beat-orientation/mechanism-of-tatenori/ja/)
- [Letter to Native Mora-Timed Speakers](/beat-orientation/letter-to-native-mora-timed-speakers/ja/)
```

### 15.4 Attachments (more examples)

```yaml
website:
  sidebar:
    contents:
      - text: "律動図鑑トップ"
        href: index.qmd
      - tatenori-theory/ja/index.qmd
```

```yaml
website:
  sidebar:
    contents:
      - section: "<ruby><rb>多層弱拍基軸律動</rb><rt>グルーヴィダンスミュージック</rt></ruby>理論"
        contents:
          - beat-orientation/benefits-of-multi-layered-weak-beat-oriented-rhythm-theory/ja/index.qmd
          - beat-orientation/headians-and-bottomians-of-beat-orientation/ja/index.qmd
          - beat-orientation/phonological-analysis-of-rhythm-types-in-languages/ja/index.qmd
          - beat-orientation/letter-to-native-mora-timed-speakers/ja/index.qmd
          - beat-orientation/the-crossing-point-of-language-and-music/ja/index.qmd
          - beat-orientation/multi-layered-weak-beat-precedence/ja/index.qmd
          - beat-orientation/multi-layered-weak-beat-oriented-rhythm-theory-summary/ja/index.qmd
          - beat-orientation/mechanism-of-tatenori/ja/index.qmd
```

```yaml
website:
  sidebar:
    contents:
      - distributed-groove-theory/ja/index.qmd
      - offbeat-count-theory/index.qmd
      - weak-beat-as-sun-strong-beat-as-earth/master-ja.qmd
      - tatenori-and-psychology/index.md
      - mechanism-behind-tatenori/index.md
```

## 16) Implementation Notes (non-normative but helpful)

* Use a BOM-tolerant front-matter regex (optional) to extract the YAML block quickly; prefer a real YAML parser afterward.
* For provenance (warnings), `ruamel.yaml` exposes line/col for nodes. If using PyYAML, line tracking requires custom loaders or is omitted.
* Title heuristics for fallback (hyphen/underscore → space; title case) are optional; preserving original segment is acceptable.

---

# Related things you might want to ask next

* A **validator** (`toc-validate`) that prints the tree, warns on missing/untitled nodes, and **fails CI on warnings**.
* A tiny **CSS** snippet to tune spacing for top-level items only (keep nested lists compact).
* A **title cache** design keyed by `(abs_path, size, mtime)` to survive renames reliably.

# Background info that helps

* Quarto preserves Markdown with inline HTML; directory-style links avoid `.html` vs `/` mismatches between preview and static hosting (e.g., GitHub Pages, CloudFront). Normalizing hrefs (leading + trailing slash, resolving `.`/`..`) eliminates subtle routing issues.

---

## Two short summaries (as you prefer both)

**Tone-matched summary:**
“Build a Markdown TOC from Quarto sidebars. Titles come from the source QMD/MD (HTML intact). Object leaves use `text` only if the page can’t supply a title. No merging, no dedup. Directory-style links with strict normalization.”

**Neutral/analytical summary:**
“The tool concatenates `website.sidebar.contents` arrays from listed YAMLs, renders a nested Markdown list with directory-style links, and resolves leaf titles from QMD/MD front matter or H1, preserving inline HTML. Object-form `text` is used solely as fallback. Robust path normalization and clear warning semantics are specified.”

---

## Native-style rewrites table (multi-register)

| Style          | Rewrite                                                                                                                                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tone-matched   | “Spec v2.1: TOC from sidebars; titles from QMD/MD (HTML kept); object `{text}` is fallback only; strict directory hrefs; no merges/dedup.”                                                                             |
| Casual         | “Make a nested Markdown TOC from your sidebars. Grab titles from the files; only use the YAML label if the file doesn’t have one.”                                                                                     |
| Academic       | “A deterministic procedure constructs a hierarchical Markdown TOC from Quarto sidebars, deriving leaf labels from primary QMD/MD metadata while preserving inline HTML; YAML labels function solely as contingencies.” |
| Gen-Z          | “Build the TOC off the sidebars. Titles come from the page; YAML `text` talks only when the page’s silent.”                                                                                                            |
| Polite         | “This generates a Markdown TOC from your sidebars, preferring page titles and using YAML `text` only when necessary.”                                                                                                  |
| Business       | “Deterministic TOC generation with file-derived titles, normalized directory links, and clear fallbacks for missing metadata.”                                                                                         |
| Minimalist     | “TOC from sidebars. Titles from files. `text` only if needed.”                                                                                                                                                         |
| Socratic       | “If YAML disagrees with the page, which is authoritative? We specify the page title; YAML is fallback.”                                                                                                                |
| Poetic         | “Let each page name itself; the YAML speaks only when the page falls quiet.”                                                                                                                                           |
| Provocative    | “Stop letting YAML lie—trust the page. `text` is backup, not truth.”                                                                                                                                                   |
| Child-friendly | “We make a link list. Each page tells its name. If it won’t, we use the label.”                                                                                                                                        |
| Old-school     | “Reads sidebars, writes TOC. Uses document titles; labels are backup. Slashes normalized.”                                                                                                                             |
| Journalistic   | “New spec standardizes TOC creation: page-first titles, YAML as fallback, normalized directory links, and explicit warnings.”                                                                                          |
| Tweetable      | “Markdown TOC from Quarto sidebars: file-first titles (HTML kept), YAML `text` only if missing. Strict directory links. No merges/dedup.”                                                                              |

