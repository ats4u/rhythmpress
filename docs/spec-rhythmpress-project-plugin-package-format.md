# Rhythmpress Project Plugin Package Format

Created: 20260506-181609

Status: draft specification.

## Purpose

Define the package artifact and lifecycle for Rhythmpress project plugins.

The package format is the implementation form for project feature packs. A package keeps CSS, JavaScript, filters, support files, config patches, generated exclusions, and verification rules together until a project explicitly materializes it.

## Goals

- Keep each feature as one portable, inspectable unit.
- Make packages easy to edit during development.
- Allow packed distribution without losing the editable structure.
- Materialize package contents deterministically into a real project tree.
- Record ownership so future checks, repairs, updates, and deactivation are possible.
- Avoid scattering CSS, JavaScript, and configuration before activation.

## Non-Goals

The first package system must not:

- run arbitrary package installer scripts;
- execute package code during metadata inspection;
- fetch packages from the network;
- silently overwrite user-modified files;
- treat rendered/generated outputs as package source;
- implement package signing or a remote registry.

## Package Forms

Two equivalent forms are supported.

Development form:

```text
toc-helper.rppkg/
  plugin.yml
  files/
    assets/rhythmpress-toc.mjs
    assets/rhythmpress-toc.css
  templates/
    starter-toc.qmd
```

Packed distribution form:

```text
toc-helper.rppkg.tar
toc-helper.rppkg.tar.gz
```

The archive must contain exactly one package root directory or a root-level `plugin.yml`. The unpacked tree must be byte-for-byte inspectable as the same development form.

Rationale:

- directory form is easy to rewrite, diff, and edit;
- tar form is one portable artifact;
- both preserve multipart package contents without scattering them into the project before activation.

## Package Root

Required package root entries:

```text
plugin.yml
files/
```

Optional package root entries:

```text
templates/
docs/
tests/
LICENSE
README.md
```

Rules:

- `plugin.yml` is the package source of truth.
- `files/` contains source files to materialize into a project.
- `templates/` contains text templates rendered during materialization.
- `docs/` is human documentation and is not materialized unless explicitly listed.
- Paths inside the package must use `/` separators.
- Paths must be relative and must not contain `..`.

## `plugin.yml` Schema

Minimum shape:

```yml
schema: 1
id: toc-helper
version: 0.1.0
name: TOC Helper
description: Visible starter table-of-contents helper.

compatibility:
  rhythmpress: ">=0.1.2"
  package-schema: 1

default: true
depends-on: []
conflicts-with: []

features:
  provides:
    - toc-helper

files:
  - source: files/assets/rhythmpress-toc.mjs
    target: assets/rhythmpress-toc.mjs
    mode: file
    template: false
  - source: files/assets/rhythmpress-toc.css
    target: assets/rhythmpress-toc.css
    mode: file
    template: false

quarto-patch:
  format:
    html:
      include-in-header:
        - text: |
            <link rel="stylesheet" href="/assets/rhythmpress-toc.css" />
            <script type="module" src="/assets/rhythmpress-toc.mjs"></script>

metadata-patch: {}

starter-content:
  requires:
    - "#toc"

gitignore: []
quartoignore: []
generated-exclusions: []

external-tools: []
external-scripts: []

verification:
  - type: file-exists
    path: assets/rhythmpress-toc.mjs
  - type: config-contains
    path: _quarto.yml
    value: /assets/rhythmpress-toc.mjs
```

Required fields:

- `schema`
- `id`
- `version`
- `description`
- `compatibility`
- `files`

Recommended fields:

- `features.provides`
- `depends-on`
- `conflicts-with`
- `generated-exclusions`
- `verification`

## Identity And Versioning

Package IDs:

- must be lowercase;
- may contain ASCII letters, digits, and hyphens;
- must be stable across releases;
- must not use site-specific names for generic behavior.

Package versions:

- should use semantic versioning;
- are recorded in project state when activated;
- are used for compatibility checks and update decisions.

Feature IDs and package IDs may be the same, but they are not required to be identical. A package can provide multiple features, and one feature can later be implemented by a replacement package.

## Package Search Locations

Package resolution order:

1. explicit path passed to a command;
2. project-local packages under `.rhythmpress/packages/`;
3. user package directory under `$RHYTHMPRESS_HOME/packages/`;
4. built-in Rhythmpress package directory shipped with the Python package;
5. paths listed in `RHYTHMPRESS_PLUGIN_PATH`, left to right.

First implementation may support only explicit paths and built-in packages, but the package metadata must not assume one fixed location.

## Project State Files

User-facing desired state remains in `_quarto.yml`:

```yml
rhythmpress:
  project:
    features:
      toc-helper: true
      lilypond: false
    plugins:
      toc-helper:
        package: toc-helper
        version: 0.1.0
        materialize: true
```

Internal materialization state remains in `.rhythmpress-template.json`.

The manifest records:

- active package ID and version;
- package source digest;
- owning feature ID;
- materialized file targets;
- materialized file hashes;
- config patches applied;
- generated exclusions registered;
- user-managed or package-managed status.

Optional future lockfile:

```text
.rhythmpress/plugins.lock.yml
```

The lockfile is reserved for exact package resolution if remote registries or multiple package roots are added later. It is not required in the first implementation.

## Materialization

Materialization expands a package into a project tree.

Materialization writes:

- listed `files` targets;
- rendered listed templates;
- structured patches into `_quarto.yml`;
- structured patches into `_metadata-<lang>.yml`;
- ignore patterns;
- manifest state.

Materialization must not write:

- generated artifacts;
- rendered output;
- files not listed in `plugin.yml`;
- package docs unless listed as materialized files.

Materialization order:

1. resolve package and dependencies;
2. validate package schema and compatibility;
3. build a complete write plan;
4. validate target paths and conflicts;
5. apply file writes and config patches;
6. write manifest state after all writes succeed;
7. run lightweight verification.

If any step fails before the manifest write, the operation must fail without partially claiming ownership. Atomic file replacement should be used for individual file writes where possible.

## Materialization Triggers

Allowed triggers:

```sh
rhythmpress project create
rhythmpress project activate-plugin <package-or-feature>
rhythmpress project deactivate-plugin <package-or-feature>
rhythmpress project sync-plugins
rhythmpress project check
rhythmpress build
```

Trigger behavior:

- `project create` materializes core and default packages selected for the new skeleton.
- `project activate-plugin` records desired state and materializes the package.
- `project deactivate-plugin` removes config patches and removes or unmanages owned files according to the deactivation policy.
- `project sync-plugins` materializes missing or stale active packages.
- `project check` verifies state and reports drift without writing.
- `rhythmpress build` may run a pre-build plugin sync phase only for packages already enabled in project desired state.

Build-trigger rule:

`rhythmpress build` must not enable new packages by itself. It may materialize or repair packages already enabled in `_quarto.yml`, but only under the same conflict rules as `project sync-plugins`. If a conflict is detected, build fails before preprocessing.

## Activation

Activation means:

- package is resolved;
- dependencies are activated first;
- `_quarto.yml rhythmpress.project.features` is updated;
- `_quarto.yml rhythmpress.project.plugins` records package desired state;
- package contents are materialized;
- `.rhythmpress-template.json` records ownership.

Example:

```sh
rhythmpress project activate-plugin ./packages/toc-helper.rppkg
rhythmpress project activate-plugin toc-helper
```

Activation must refuse:

- unknown package ID;
- incompatible package;
- dependency cycles;
- package conflicts;
- target path escaping project root;
- unmanaged file collisions;
- user-modified managed file collisions.

## Deactivation

Deactivation means:

- desired feature state is disabled or removed;
- config patches owned by the package are removed when safely identifiable;
- generated exclusions are removed when no other active package owns them;
- materialized files are removed, preserved, or unmanaged according to policy;
- manifest state is updated.

Deactivation policy per file:

| File State | Default Action |
|---|---|
| package-managed and unchanged | remove |
| package-managed but user-modified | preserve and mark unmanaged |
| shared by another active package | preserve |
| unmanaged | preserve |

The command must print every preserved modified file.

Config unpatching must be ownership-aware. If a raw config block was edited by the user, the command should preserve it and report drift instead of deleting it.

## Conflict Handling

Materialization conflict rules:

- unmanaged existing target file: conflict;
- managed target with matching hash: ok;
- managed target missing: recreate;
- managed target modified by user: conflict;
- target directory where file is expected: conflict;
- target file where directory is expected: conflict.

`--force` may repair missing or unchanged managed files. It must not overwrite user-modified files unless a later explicit merge/update command exists.

## Updates

Package update is separate from activation.

Future command shape:

```sh
rhythmpress project update-plugin <package-or-feature>
```

Update policy:

- compare old package version and new package version;
- compute file and config patch changes;
- apply only unchanged managed files automatically;
- preserve user-modified managed files and report conflicts;
- never delete user-modified files silently;
- record old and new package digests in manifest.

The first implementation may reject updates and instruct users to deactivate/reactivate only when safe.

## Dependency Model

Dependencies are package IDs or feature IDs:

```yml
depends-on:
  - core
  - toc-helper
```

Rules:

- dependencies activate before dependents;
- cycles are invalid;
- version constraints may be added later;
- package conflicts are checked after full dependency resolution.

Conflict example:

```yml
conflicts-with:
  - another-toc-helper
```

## Config Patch Model

Config patches are declarative.

Patch kinds:

- `quarto-patch`: applies to `_quarto.yml`;
- `metadata-patch`: applies to every `_metadata-<lang>.yml` unless scoped;
- `metadata-patch-by-lang`: applies to selected language metadata;
- `gitignore`: appends ignore patterns;
- `quartoignore`: appends Quarto ignore patterns.

Patch merge rules:

- maps deep-merge;
- lists append unique values;
- scalar conflicts fail unless the package owns the existing value;
- raw HTML blocks must carry package ownership metadata in the manifest;
- unpatching removes only values owned by the package.

First implementation may restrict patch shapes to well-known Quarto paths to keep behavior deterministic.

## Template Rendering

Package templates may use a small variable context:

```text
project.title
project.site_url
project.languages
project.default_language
package.id
package.version
```

Template rules:

- no arbitrary code execution;
- missing variables fail validation;
- rendered bytes are hashed in the ownership manifest;
- template output targets must be listed in `files`.

The first implementation may use simple placeholder replacement instead of a full template engine.

## Security Rules

Archive extraction rules:

- reject absolute paths;
- reject `..` path traversal;
- reject symlink and hardlink entries in archives for first implementation;
- reject device files, FIFOs, and special files;
- reject files larger than a documented size limit unless explicitly allowed;
- normalize paths before conflict checks;
- never execute package-provided commands.

Package inspection must parse `plugin.yml` and list files only. It must not import or execute package code.

## Verification

Verification checks are declarative and lightweight.

Supported first checks:

| Check | Meaning |
|---|---|
| `file-exists` | Target file exists. |
| `file-absent` | Generated or disabled target is absent. |
| `config-contains` | Config file contains expected value. |
| `config-key-type` | Config key has expected type. |
| `ignore-contains` | Ignore file contains expected pattern. |
| `feature-enabled` | Desired feature state is enabled. |
| `package-materialized` | Manifest records package and owned files. |

Verification must not run Quarto, Playwright, LilyPond, network calls, or deployment tools unless explicitly requested by a separate lifecycle proof command.

## Build Interaction

`rhythmpress build` can use packages in two ways:

1. Check mode: verify active packages are materialized before preprocessing.
2. Sync mode: materialize missing managed package files before preprocessing.

Default should be conservative:

- check active package state;
- fail clearly on drift;
- allow an explicit project setting or flag to sync during build.

Possible future flag:

```sh
rhythmpress build --sync-plugins
```

If build syncs plugins, it must use the same write plan, conflict checks, and manifest rules as `project sync-plugins`.

## Example Package: TOC Helper

```text
toc-helper.rppkg/
  plugin.yml
  files/
    assets/rhythmpress-toc.mjs
    assets/rhythmpress-toc.css
```

```yml
schema: 1
id: toc-helper
version: 0.1.0
description: Visible starter table-of-contents helper.
compatibility:
  rhythmpress: ">=0.1.2"
  package-schema: 1
default: true
features:
  provides:
    - toc-helper
files:
  - source: files/assets/rhythmpress-toc.mjs
    target: assets/rhythmpress-toc.mjs
    mode: file
  - source: files/assets/rhythmpress-toc.css
    target: assets/rhythmpress-toc.css
    mode: file
quarto-patch:
  format:
    html:
      include-in-header:
        - text: |
            <link rel="stylesheet" href="/assets/rhythmpress-toc.css" />
            <script type="module" src="/assets/rhythmpress-toc.mjs"></script>
starter-content:
  requires:
    - "#toc"
verification:
  - type: file-exists
    path: assets/rhythmpress-toc.mjs
  - type: config-contains
    path: _quarto.yml
    value: /assets/rhythmpress-toc.mjs
```

## Example Package: LilyPond

```yml
schema: 1
id: filter-lilypond
version: 0.1.0
description: Render LilyPond notation during Quarto render.
compatibility:
  rhythmpress: ">=0.1.2"
  package-schema: 1
default: false
features:
  provides:
    - lilypond
external-tools:
  - lilypond
files:
  - source: files/filters/lilypond.lua
    target: filters/lilypond.lua
  - source: files/common-ly/lilypond-preamble.ly
    target: common-ly/lilypond-preamble.ly
quarto-patch:
  metadata:
    lilypond-preamble: common-ly/lilypond-preamble.ly
  format:
    html:
      filters:
        - filters/lilypond.lua
  resources:
    - common-ly/*.ly
gitignore:
  - /lilypond-out/
generated-exclusions:
  - lilypond-out/
verification:
  - type: file-exists
    path: filters/lilypond.lua
  - type: ignore-contains
    path: .gitignore
    value: /lilypond-out/
```

## First Implementation Cut

First implementation should support:

- directory package form;
- built-in package lookup;
- `plugin.yml` schema validation;
- file materialization;
- structured `_quarto.yml` patching for known paths;
- `.gitignore` appends;
- manifest ownership records;
- check-only verification;
- activation during `project create` for core/default packages.

First implementation may defer:

- tar archive input;
- remote package registries;
- signatures;
- update command;
- deactivation command;
- build-time sync;
- package lockfile;
- complex config unpatching.
