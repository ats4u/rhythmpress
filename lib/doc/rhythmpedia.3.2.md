# v3.2 Library Specification

## General rules

* All functions must be **CWD-agnostic**. Never rely on `os.chdir()`; operate only on **explicit `Path` arguments**.
* Validate inputs early; fail fast with clear exceptions.

---

## `create_toc_v1`

**Signature:**
`create_toc_v1(input_md: Path, link_target_md: str) -> str`

**Behavior:**

* Reads `input_md` (a **file**), runs Pandoc to produce a markdown TOC.
* Uses a **hardcoded template** located at `./lib/templates/toc` (path resolved **relative to this module file**).
* Rewrites in-document anchor links `](#id)` → `]({link_target_md}#id)`.

**Requirements & errors:**

* `input_md` **must be** a `Path` to an existing file → else `FileNotFoundError`.
* Template must exist at `lib/templates/toc` → else `FileNotFoundError`.
* `pandoc` must be on PATH → else `RuntimeError("pandoc not found")`.
* Pandoc non-zero exit → `RuntimeError(f"pandoc failed: …")`.

**CWD:** Irrelevant; all paths passed to Pandoc are **absolute**.

---

## `qmd_all_masters`

**Signature:**
`qmd_all_masters(qmd_fn: callable[[Path], None], root: Path) -> None`

**Behavior:**

* Scans `root` for `master-*.qmd` (non-recursive): `root.glob("master-*.qmd")`.
* Calls `qmd_fn(p: Path)` for each match in sorted order.

**Requirements & errors:**

* `root` is **required** (no default); must be a `Path`.
* `root` must **exist** and be a **directory** → else `ValueError("root must be an existing directory")`.
* If `root` is a **file** → `ValueError("root must be a directory")`.
* No matches: **no error**; returns without side effects.

**CWD:** Irrelevant.

---

## `clean_directories_except_attachments_qmd`

**Signature:**
`clean_directories_except_attachments_qmd(root: Path) -> None`

**Behavior:**

* Iterates **immediate subdirectories** of `root`.
* **Deletes** every subdirectory **except** those whose name **starts with `"attachments"`** (e.g., `attachments`, `attachments-en` are preserved).
* Uses `shutil.rmtree` for deletion.

**Requirements & errors:**

* `root` is **required**; must be a `Path`.
* `root` must **exist** and be a **directory** → else `ValueError`.
* If `root` is a **file** → `ValueError`.
* Deletion errors propagate (you’ll see tracebacks) unless you later choose to catch/log them.

**CWD:** Irrelevant.

---

## Unchanged / informational

* `split_master_qmd(master_path: Path)` and `copy_lang_qmd(master_path: Path)` already operate on explicit paths and remain CWD-agnostic.
* `parse_frontmatter(text)`, `parse_qmd_teasers(text, …)`, `proc_qmd_teasers(items, basedir, lang, …)` are pure functions (no FS access) and unchanged.

---

## Exceptions summary

* **`ValueError`** — invalid `root` argument (missing, not a directory, or a file).
* **`FileNotFoundError`** — missing `input_md` or missing `lib/templates/toc`.
* **`RuntimeError`** — Pandoc missing / failed; YAML parsing problems in front matter where applicable.

---

## Minimal reference implementations (patch-style)

```python
# lib/rhythmpedia.py (excerpts)

from pathlib import Path
import subprocess, shutil

# ---- create_toc_v1 (hardcoded lib/templates/toc; no CWD reliance) ----
def create_toc_v1(input_md: Path, link_target_md: str) -> str:
    if not isinstance(input_md, Path):
        raise ValueError("input_md must be a Path")
    if not input_md.is_file():
        raise FileNotFoundError(f"input_md not found: {input_md}")

    # template under ./lib/templates/toc (relative to this file)
    module_dir = Path(__file__).resolve().parent          # .../lib
    template = module_dir / "templates" / "toc"
    if not template.exists():
        raise FileNotFoundError(f"pandoc template not found: {template}")

    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc not found on PATH")

    cmd = [
        "pandoc",
        str(input_md),
        "--toc",
        "--toc-depth=6",
        "--to=markdown",
        f"--template={str(template)}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed ({proc.returncode}): {proc.stderr.strip()}")

    toc_md = proc.stdout
    return re.sub(r"\]\(#", f"]({link_target_md}#", toc_md)

# ---- qmd_all_masters (root: Path, required, dir-only) ----
def qmd_all_masters(qmd_fn, root: Path) -> None:
    if not isinstance(root, Path):
        raise ValueError("root must be a pathlib.Path")
    if not root.exists() or not root.is_dir():
        raise ValueError(f"root must be an existing directory: {root}")

    for p in sorted(root.glob("master-*.qmd")):
        qmd_fn(p)

# ---- clean_directories_except_attachments_qmd (root: Path, required, dir-only) ----
def clean_directories_except_attachments_qmd(root: Path) -> None:
    if not isinstance(root, Path):
        raise ValueError("root must be a pathlib.Path")
    if not root.exists() or not root.is_dir():
        raise ValueError(f"root must be an existing directory: {root}")

    for item in root.iterdir():
        if item.is_dir():
            if item.name.startswith("attachments"):
                print(f"🛡️  Skipping: {item}")
                continue
            print(f"🧹 Removing: {item}")
            shutil.rmtree(item)
```

---

## Call-site guidance (subcommands)

* Convert incoming CLI strings to `Path` **before** calling the library.
* For **multi-target** subcommands (v3.1), pass each as `Path`:

  ```python
  # copy-lang
  for t in targets:
      root = (t if t.is_absolute() else Path.cwd()/t).resolve()
      root = root.parent if root.is_file() else root
      qmd_all_masters(copy_lang_qmd, root)  # expects a directory Path
  ```
* For **clean**:

  ```python
  clean_directories_except_attachments_qmd(root)  # root: Path (dir)
  qmd_all_masters(clean_directories_except_attachments_qmd, root)  # if you want per-master semantics later
  ```

---

## Migration notes

* **Breaking change:** `qmd_all_masters` and `clean_directories_except_attachments_qmd` no longer accept strings or omit `root`.
* Anywhere you used `Path(".")` as a default is still valid; just make it **explicit**.
* Remove any lingering `pushd` wrappers that were only compensating for CWD.

If you want, I can push a patch that enforces these checks and updates the two subcommands we’ve been editing to pass `Path` objects explicitly.


# v3.2.1 Library & CLI Spec (revision of v3.2) (CLI Strict-Args Addendum)

3.2.1 – CLI: stricter dir-only arguments; non-dir → exit 2. Library API unchanged.

This is a small addendum after the 3.2 doc.

No API changes; library remains v3.2. This addendum standardizes CLI behavior: directory-only positional args; exit 2 on invalid paths; no chdir/path mangling.

All library rules remain as specified in v3.2.


## General rules (unchanged)

* **CWD-agnostic library.** No `chdir`. All FS functions take **explicit `Path`** args.
* **Fail fast.** Validate inputs early with clear exceptions.

---

## `create_toc_v1` (unchanged)

**Signature:** `create_toc_v1(input_md: Path, link_target_md: str) -> str`
**Behavior & errors:** same as v3.2 — template fixed at `./lib/templates/toc`, absolute paths, `FileNotFoundError` for missing inputs/template, `RuntimeError` if `pandoc` missing/fails.

---

## `qmd_all_masters` (unchanged)

**Signature:** `qmd_all_masters(qmd_fn: callable[[Path], None], root: Path) -> None`

* `root` **must** be an existing **directory** (`ValueError` otherwise).
* Non-recursive `root.glob("master-*.qmd")`.
* No matches → no error.

---

## `clean_directories_except_attachments_qmd` (unchanged)

**Signature:** `clean_directories_except_attachments_qmd(root: Path) -> None`

* `root` **must** be an existing **directory** (`ValueError` otherwise).
* Deletes immediate subdirs except names starting with `attachments`.

---

## Unchanged helpers

Pure functions remain as in v3.2:

* `split_master_qmd(master_path: Path)`, `copy_lang_qmd(master_path: Path)`
* `parse_frontmatter`, `parse_qmd_teasers`, `proc_qmd_teasers`, etc.

---

## Exceptions summary (unchanged)

* `ValueError` — invalid `root` (missing / not a dir / file).
* `FileNotFoundError` — missing `input_md` or `lib/templates/toc`.
* `RuntimeError` — `pandoc` missing/failure; YAML errors as applicable.

---

## NEW in v3.2.1 — Subcommand conventions (CLI wrappers)

These rules standardize how **bin/** subcommands validate inputs and interact with the v3.2 library:

1. **Directory-only arguments**

* Positional paths, if provided, **must be existing directories**.
* If any path is missing or not a directory → print an error to **stderr** and **exit 2**.
* **No file→parent fallback. No skipping.**

2. **Default target**

* If **no paths** are provided, act on **`.`** (current working directory). The current dir must be a directory.

3. **Multiple targets**

* Subcommands may accept multiple directory arguments and process each independently. All must validate as directories up front; fail fast if any is invalid.

4. **No implicit chdir**

* Subcommands pass validated `Path` objects directly to the library; **do not** `chdir` before calling.

5. **Exit codes**

* `0` on success (even if there was “nothing to do”).
* `1` reserved for tool-specific soft failures (e.g., `--strict` in TOC generator).
* `2` for **argument/validation errors** (missing/non-dir paths, etc.).

---

## Minimal reference (CLI) — copy-lang & split

```python
# bin/rhythmpedia-copy-lang.py (v3.2.1)
ap.add_argument("paths", nargs="*", type=Path, help="Article directories (default: .)")
targets = args.paths or [Path(".")]

roots = []
for t in targets:
    p = (t if t.is_absolute() else (Path.cwd() / t)).resolve()
    if not p.exists():
        print(f"[ERROR] not found: {t}", file=sys.stderr); sys.exit(2)
    if not p.is_dir():
        print(f"[ERROR] not a directory: {t}", file=sys.stderr); sys.exit(2)
    roots.append(p)

for root in roots:
    rhythmpedia.qmd_all_masters(rhythmpedia.copy_lang_qmd, root)
```

```python
# bin/rhythmpedia-split.py (v3.2.1)
# same validation as above, then:
for root in roots:
    rhythmpedia.qmd_all_masters(rhythmpedia.split_master_qmd, root)
```

---

## Migration notes (delta from v3.2)

* The **library API** is unchanged.
* **Subcommands** are now **strict** about directory arguments (no file handling, no skipping).
* Keep using explicit `Path` objects to call library functions; remove any `pushd`/`chdir` logic.

If you want, I can stamp the spec header/footer into your repo as `SPEC-v3.2.1.md` and add quick unit tests for the CLI exit codes.

