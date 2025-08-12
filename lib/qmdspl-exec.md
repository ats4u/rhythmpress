
Absolutely. Below is a **comprehensive, exhaustive, and up-to-date specification** of your latest Quarto Markdown splitter program, reflecting the exact behavior of the code you provided.

---

# ✅ **Quarto Section Splitter Program – Full Specification**

## 🧭 Overview

This Python program parses and splits a **Quarto `.qmd` master file** (`master-<lang>.qmd`) into multiple section-based files based on `##` (level-2) headers. It automatically generates nested output directories and index files suitable for multilingual Quarto websites. Additionally, it supports **Ruby annotation parsing** and **auto-ID generation** from Japanese or multilingual headers.

---

## 📥 Input

### 1. **Input Files**

* Must be named with the pattern:

  ```
  master-<lang_id>.qmd
  ```

  * Example: `master-ja.qmd`, `master-en.qmd`

### 2. **Expected Content Format**

Each input `.qmd` file may contain:

* **Preamble** (optional content before the first `##`)
* One or more **level-2 headers** (`## Title {#id}` or `## Title`)
* Optional **level-3 headers** (`### Subsection`)
* Headers may include **Ruby annotations** (e.g., `<ruby>漢字<rt>ふりがな</rt></ruby>`)

---

## 🔍 Parsing Logic

### 1. **Header Detection**

#### Level-2 (`##`) Headers

* Matched with:

  ```regex
  ^## (.+?)(?:\s*\{#([^\}]+)\})?\s*$
  ```
* Extracted:

  * `Title`: Group 1
  * `ID`: Group 2 (if present); otherwise auto-generated

#### Level-3 (`###`) Headers

* Matched with:

  ```regex
  ^### (.+?)(?:\s*\{#([^\}]+)\})?\s*$
  ```

### 2. **Auto ID Generation**

If no `{#id}` is given:

* ID is **generated** from base text (after stripping Ruby):

  * Removes non-word characters except:

    * Japanese (`\u4e00–\u9fff`, `\u3040–\u30ff`)
    * CJK punctuation (`\u3000–\u303f`)
  * Normalizes to:

    ```
    slugified-id = re.sub( disallowed, '-', ruby_base_text ).strip('-')
    ```

### 3. **Ruby Annotation Handling**

Ruby is stripped using an `HTMLParser` subclass:

* `<rt>` content (furigana) is removed
* Only **visible text** (base of the ruby) is preserved
* Supports both `<ruby><rb>…</rb><rt>…</rt></ruby>` and `<ruby>…<rt>…</rt></ruby>` styles

---

## 📦 Output

### 1. **Directory Structure**

For each `##` section in `master-<lang_id>.qmd`, output is:

```
<base_dir>/
├── <section_id>/
│   └── <lang_id>/
│       └── index.qmd      ← full section contents
├── <lang_id>/
│   └── index.qmd          ← master TOC + preamble
```

### 2. **File Contents**

#### a. Section File (`index.qmd`)

Each file contains:

* The full content of the `##` block (including body and any `###` children)

#### b. Master Index (`<lang_id>/index.qmd`)

Auto-generated `## Contents` section:

```markdown
## Contents

### [Section Title](section-id/)
Section description (text between `##` and first `###`, if any)

### [Next Section](...)
...
```

If any **preamble** text exists (before first `##`), it is placed before `## Contents`.

---

## 🧠 Behavioral Summary

| Feature                           | Description                                                      |
| --------------------------------- | ---------------------------------------------------------------- |
| 🗂️ Multi-section splitting       | Each level-2 section becomes a file                              |
| 🏷️ ID extraction + fallback      | Uses `{#id}` or auto-generates from base text                    |
| 🔤 Ruby stripping support         | Properly ignores `<rt>` (furigana)                               |
| 🌐 Multilingual support           | Detected via file name (`master-ja.qmd` → `ja`)                  |
| 📁 Recursive mkdir                | Uses `mkdir(parents=True, exist_ok=True)` for safe creation      |
| 📑 Subsection awareness           | Captures presence of `###` but doesn’t yet write them separately |
| 📄 Section description extraction | Captures paragraph between `##` and first `###`                  |
| 🔄 Re-entrant                     | Can run multiple times without errors (safe overwrite)           |

---

## ⚙️ Program Flow

### 1. Discover input files

```python
Path('.').glob('master-*.qmd')
```

### 2. For each file:

* Extract `lang_id` from filename
* Call `split_qmd(input_file, lang_id)`

### 3. In `split_qmd(...)`:

* Parse input file
* For each `##` section:

  * Extract `h2_title`, `h2_id`, `h2_block`
  * Detect child `###` blocks
  * Extract `h2_description` (pre-`###` content)
  * Write to:

    ```
    ./<h2_id>/<lang_id>/index.qmd
    ```
* Write `index.qmd` under `./<lang_id>/` with links

---

## ⚠️ Limitations / To-Do

| Area            | Limitation                                         | Possible Solution             |
| --------------- | -------------------------------------------------- | ----------------------------- |
| `###` splitting | `###` blocks are detected but not split into files | Add per-subsection split mode |
| Duplicate IDs   | No check for ID collisions                         | Add validation or auto-suffix |
| Header nesting  | Only `##` and `###` are processed                  | Extend for deeper levels      |
| CLI usability   | No CLI arguments                                   | Add `argparse` or CLI wrapper |
| Quarto YAML     | No automatic `_quarto.yml` generation              | Add sidebar + TOC automation  |

---

## 🧪 Example Case

### Input: `master-ja.qmd`

```markdown
# 前書き

これはイントロです。

## 日本語のリズムとは {#japanese-rhythm}

イントロ段落。

### タイミングの問題

説明...

## 第二章

別のセクション
```

### Output:

#### Directory Structure:

```
.
├── japanese-rhythm/
│   └── ja/
│       └── index.qmd
├── 第二章/
│   └── ja/
│       └── index.qmd
├── ja/
│   └── index.qmd
```

#### `ja/index.qmd`:

```markdown
# 前書き

これはイントロです。

## Contents

### [日本語のリズムとは](japanese-rhythm/)
イントロ段落。

### [第二章](第二章/)
```

---

If you want, I can generate:

* A test fixture set
* A sample CLI wrapper (`split-qmd.py --input master-ja.qmd`)
* `_quarto.yml` auto-updater script for navigation linking

Would you like that?

