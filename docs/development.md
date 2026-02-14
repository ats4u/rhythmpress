# Development notes

This document is for contributors and for future-you: how the repository is structured, how packaging works, how to add new commands safely, and how to avoid macOS metadata artifacts (`._*`, `.DS_Store`) when distributing or archiving.

## Repository layout

Rhythmpress uses a `src/` layout.

- `pyproject.toml`  
  Packaging metadata (setuptools). The console entry point is `rhythmpress = rhythmpress.scripts.cli:main`.

- `requirements.txt`  
  A pinned development environment snapshot. It currently contains far more than the runtime minimum (e.g., Jupyter stack). Treat it as “dev convenience,” not as the minimal install spec.

- `src/rhythmpress/`  
  Library code and the command implementations.

  - `src/rhythmpress/scripts/`  
    Subcommands live here as `rhythmpress_<name>.py` or `rhythmpress_<name>.sh`.

  - `src/rhythmpress/templates/`  
    Small templates used by generators (e.g., TOC markdown template).

  - `src/rhythmpress/doc/`  
    Internal/legacy notes (not the public `docs/` directory).

## How the CLI dispatcher works

`rhythmpress` is a dispatcher. It does not depend on global PATH lookups for subcommands; it only executes scripts in `src/rhythmpress/scripts/`.

Key behaviors:

- Command normalization: users can run `kebab-case`, `snake_case`, or even accidental spaces.  
  Example: `preproc-clean`, `preproc_clean`, and `"preproc clean"` resolve to the same target.

- Target resolution: the dispatcher searches for:
  - `scripts/rhythmpress_<cmd>` (no extension)
  - `scripts/rhythmpress_<cmd>.py`
  - `scripts/rhythmpress_<cmd>.sh`

- Python scripts are executed as modules (`python -m rhythmpress.scripts.<module>`), so relative imports inside the package work reliably.

- Shell scripts are executed either directly (if executable) or via `bash` (if not executable). This means you do not need to rely on POSIX executable bits being preserved by wheel installs.

## Adding a new subcommand

1) Create a file under `src/rhythmpress/scripts/`:

- Python: `rhythmpress_my_new_command.py`
- Shell: `rhythmpress_my_new_command.sh`

2) Keep the implementation “command-line first”:
- Use `argparse` in Python scripts.
- Return meaningful exit codes.
- Print errors to stderr when practical.

3) Verify it is discoverable:

```sh
rhythmpress list
````

The command will appear as `my-new-command` (display uses kebab-case even if the filename is snake_case).

## Runtime dependencies vs dev dependencies

Current state (important):

* `pyproject.toml` does not yet declare `[project.dependencies]`.
* The code imports `yaml` (PyYAML) in multiple places, and `watchfiles` in `auto-rebuild`.

Practical implication:

* If someone installs Rhythmpress without installing dependencies separately, some commands will fail at runtime.

Recommended direction (if you want external use):

* Declare minimal runtime deps in `pyproject.toml`, e.g.:

  * `PyYAML`
  * `watchfiles` (or make it an optional extra if you want)

Recommended development split:

* Keep `requirements.txt` as a “dev full stack” snapshot if you like.
* Optionally add `requirements-dev.txt` and keep runtime minimal in `pyproject.toml`.

## External toolchain dependencies (non-Python)

Rhythmpress is a glue tool around Quarto, plus a few external utilities:

* `quarto` (Quarto CLI)
  Required for preview/render workflows (`quarto preview`, `quarto render`).

* `yq` v4 (Mike Farah)
  Required for sidebar merge (`rhythmpress render-sidebar`). Other `yq` implementations are incompatible.

You SHOULD document these in README (requirements section) because pip cannot install them.

## Local development setup

A typical editable install:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip

# Editable install
pip install -e .

# Optional: full dev environment snapshot
pip install -r requirements.txt
```

Sanity checks:

```sh
rhythmpress list
rhythmpress eval >/dev/null
```

For real functional testing, use a real Quarto project (because many commands assume `_quarto.yml` and a repo root).

## Smoke-testing strategy (recommended)

There is no formal test suite in the repository right now, so keep a lightweight “smoke test” discipline:

1. Command discovery:

```sh
rhythmpress list
```

2. Environment activation:

```sh
eval "$(rhythmpress eval)"
test -n "$RHYTHMPRESS_ROOT"
```

3. Build pipeline (on a sample Quarto project):

* `rhythmpress build` (with and without `LANG_ID`)
* `rhythmpress build --skip-clean`
* `rhythmpress auto-rebuild` (requires `watchfiles`)
* `rhythmpress render-sidebar _sidebar-<lang>.generated.conf` (requires `yq` v4)
* `quarto render` + `rhythmpress sitemap`

If you want external contributors, it is worth adding a tiny fixture project under `examples/` and a `scripts/smoke.sh` that runs these checks in CI.

## Packaging and release checklist

Rhythmpress is packaged via setuptools (`pyproject.toml`).

When you release:

1. Bump version in `pyproject.toml`:

* `[project] version = "x.y.z"`

2. Ensure `LICENSE` exists at repo root if you want the MIT license to be explicit for downstream consumers (recommended).

3. Build artifacts:

```sh
python -m pip install -U build twine
python -m build
twine check dist/*
```

4. Tag and publish (if using git tags / PyPI). Keep tags consistent with version.

Packaging note:

* Non-Python files are shipped via `tool.setuptools.package-data`:

  * `templates/*`
  * `doc/*`
  * `scripts/*`
    If you add files in deeper subdirectories, you may need to expand these globs.

## macOS metadata hygiene (avoid `._*` and other junk)

If you create tarballs on macOS, you can accidentally include AppleDouble files (`._*`) and extended attributes. This is already visible as tar warnings like `LIBARCHIVE.xattr...` and extra files such as `._pyproject.toml`.

### Prevention (best)

When creating a tarball on macOS:

```sh
COPYFILE_DISABLE=1 tar -czf rhythmpress.tar.gz \
  --exclude='._*' --exclude='.DS_Store' \
  rhythmpress/
```

If you use `bsdtar` (default macOS `tar`), `COPYFILE_DISABLE=1` is the key.

### Cleanup (repo)

Remove AppleDouble files from your working tree:

```sh
find . -name '._*' -delete
find . -name '.DS_Store' -delete
```

If you copied folders between filesystems and want to clean resource forks:

```sh
dot_clean -m .
```

### Git ignores (recommended)

Add these to a top-level `.gitignore`:

```gitignore
.DS_Store
._*
```

This prevents accidental commits, but it does not automatically prevent tar tools from embedding xattrs; keep using `COPYFILE_DISABLE=1` for archives.

## CI notes (if you add CI later)

To keep builds reproducible:

* Install `yq` v4 explicitly (do not rely on “whatever yq exists”).
* Avoid ultra-shallow clones if you rely on git history for `cdate/mdate` injection.
* Run the same high-level pipeline as users:

  * `eval "$(rhythmpress eval)"`
  * `rhythmpress build`
  * `quarto render`
  * `rhythmpress sitemap`

## Suggested contribution etiquette

If you accept external contributions, these rules keep the project maintainable:

* One behavior change per PR.
* Update docs when behavior changes (README + the relevant file under `docs/`).
* Prefer adding small, explicit helper functions over clever inlined logic (especially inside build loops).
* Be conservative with “magic”: Rhythmpress’s value is predictability.


