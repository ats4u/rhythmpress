Absolutely. Here's the **comprehensive, precise, and exhaustive specification** for your finalized `create_toc_v2` program.

---

# ✅ Final Specification for `create_toc_v2`

*(As of 2025-08-08, version using Quarto `output: asis`)*

---

## 🧭 Purpose

`create_toc_v2` is a **pure Python** program that dynamically generates a **Markdown-formatted, nested Table of Contents (TOC)** from a `master-<lang>.qmd` file.

The output is designed to:

* **Match the folder structure** created by the Quarto splitter
* **Respect slugs**, even if implicitly defined via `<ruby>` or visible text
* **Integrate into Quarto pages** using `#| output: asis` for in-place dynamic TOC injection
* **Use public-facing, web-accessible URLs**, not internal filenames

---

## 📥 Function Signature

```python
def create_toc_v2(input_md: str, link_target_md: str = ".") -> None
```

### Parameters:

| Name             | Type  | Description                                                             |
| ---------------- | ----- | ----------------------------------------------------------------------- |
| `input_md`       | `str` | Path to a `master-<lang>.qmd` file. Lang ID is extracted from filename. |
| `link_target_md` | `str` | Optional base path prefix to prepend to each link (default is `"."`).   |

---

## 📤 Output

* Prints a **nested bullet-point TOC** in **Markdown format** using:

  * `- [Title](link)`
  * Indentation reflects header levels (`##`, `###`, `####`, etc.)
* Output is directly usable in Quarto dynamic blocks with:

  ```markdown
  #| output: asis
  ```

---

## 📄 Input File Requirements

The file must:

* Be named in the format: `master-<lang-id>.qmd`

  * `lang-id` must contain no dots (e.g., `master-ja.qmd`, `master-en.qmd`)
* Contain Markdown headers:

  * `## Section Title {#slug}`
  * `### Subsection Title` (with or without `{#slug}`)
  * Optional use of `<ruby>base<rt>...<rt>` for slug fallback

---

## 📚 Header Parsing Behavior

The program scans all headers from level 2 (`##`) to level 6 (`######`).

### Header line format:

```markdown
### Header Title {#optional-slug}
```

### Extracted info per header:

* **Level**: Number of `#` characters (e.g., `###` = level 3)
* **Display title**: The visible text, stripped of HTML (e.g., `<ruby>` removed)
* **Slug**: Resolved in this strict priority:

---

## 🧠 Slug Resolution Logic

| Priority | Condition              | Description                                                                  |
| -------- | ---------------------- | ---------------------------------------------------------------------------- |
| 1️⃣      | `{#slug}` present      | Use the slug exactly as written                                              |
| 2️⃣      | `<ruby>base<rt>...`    | Extract only the base text (before `<rt>`) and use as slug (Unicode allowed) |
| 3️⃣      | Fallback slugification | Slugify the visible header title:                                            |
|          |                        | - Convert whitespace to `-`                                                  |
|          |                        | - Strip common Japanese and Western punctuation                              |
|          |                        | - Preserve all Unicode characters                                            |

---

## 🔗 Link Generation Rules

### For level-2 headers (`##`):

| Element    | Rule                                                        |
| ---------- | ----------------------------------------------------------- |
| Slug       | Used as the **directory name**                              |
| Lang ID    | Extracted from `input_md` filename (`master-ja.qmd` → `ja`) |
| Final link | `./<slug>/<lang-id>/`                                       |

### For level-3+ headers (`###`, `####`, etc.):

| Element     | Rule                                         |
| ----------- | -------------------------------------------- |
| Parent slug | Taken from most recent level-2 (`##`) header |
| Own slug    | Extracted by rules above                     |
| Final link  | `./<parent-slug>/<lang-id>/#<sub-slug>`      |

---

## 🔢 Indentation

| Header Level | Markdown TOC Indent |
| ------------ | ------------------- |
| `##`         | 0 spaces            |
| `###`        | 2 spaces            |
| `####`       | 4 spaces            |
| `#####`      | 6 spaces            |
| etc.         | +2 spaces per level |

---

## 🧾 Example

### Input filename:

```plaintext
master-ja.qmd
```

### Input content:

```markdown
## Distributed Groove Theory {#distributed-groove-theory}
### Core Ideas {#core}
### <ruby>メタ</ruby>分割

## 日本語の認知影響
### 音節タイミング
```

### Output:

```markdown
- [Distributed Groove Theory](./distributed-groove-theory/ja/)
  - [Core Ideas](./distributed-groove-theory/ja/#core)
  - [メタ分割](./distributed-groove-theory/ja/#メタ)
- [日本語の認知影響](./日本語の認知影響/ja/)
  - [音節タイミング](./日本語の認知影響/ja/#音節タイミング)
```

---

## ⚠️ Edge Cases

| Case                       | Behavior                                                |
| -------------------------- | ------------------------------------------------------- |
| Header before any `##`     | Ignored (no top-level context to attach to)             |
| No slug and no `<ruby>`    | Fallback slugify (preserve Unicode, strip punctuation)  |
| Duplicate headers or slugs | Not deduplicated (user responsibility)                  |
| Bad filename format        | Raises `ValueError` if filename not `master-<lang>.qmd` |

---

## 🧑‍💻 Intended Use

Embed inside `.qmd` files like so:

````markdown
## Contents

```\{python\}
#| output: asis
create_toc_v2("master-ja.qmd")
```
````

This renders an in-place, linkable TOC that works even in **published Quarto sites** (where `index.qmd` is served as `/ja/` or `/ja.qmd`).

---

Let me know if you'd like a machine-readable version (e.g., YAML or JSON TOC output), sidebar autogeneration, or GitHub Action integration next.

