# Rhythmpress Project Plugin Package Format

Created: 20260506-181609
Updated: 20260507-172326

Status: draft specification.

Canonical plugin-system behavior is now specified in
[Rhythmpress Plugin System Spec](spec-rhythmpress-plugin-system.md). This file
remains the package-format companion and must not contradict the canonical
plugin storage, ordering, reference-in-place wiring, or deploy semantics defined
there.

## Purpose

Define the package artifact and lifecycle for Rhythmpress project plugins.

The package format is the implementation form for project feature packs. A package keeps CSS, JavaScript, filters, support files, Quarto wiring contributions, optional deploy rules, generated exclusions, and verification rules together. By default, package files are referenced in place from `.rhythmpress-plugins/packages/<plugin-id>/` instead of copied into the project tree.

## Goals

- Keep each feature as one portable, inspectable unit.
- Make packages easy to edit during development.
- Allow packed distribution without losing the editable structure.
- Reference package contents deterministically from generated Quarto wiring.
- Record optional deployed-file ownership so future checks, repairs, updates, and uninstall are possible.
- Avoid scattering CSS, JavaScript, and configuration before install.

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
toc-helper/
  plugin.yml
  assets/
    rhythmpress-toc.mjs
    rhythmpress-toc.css
  filters/
  includes/
  templates/
    starter-toc.qmd
```

Packed distribution form:

```text
toc-helper.tar.gz
```

The archive must contain exactly one package root directory or a root-level `plugin.yml`. The unpacked tree must be byte-for-byte inspectable as the same development form.

Rationale:

- directory form is easy to rewrite, diff, and edit;
- tar form is one portable artifact;
- both preserve multipart package contents without scattering them into the project before install.

## Package Root

Required package root entries:

```text
plugin.yml
```

Optional package root entries:

```text
assets/
filters/
includes/
templates/
docs/
tests/
LICENSE
README.md
```

Rules:

- `plugin.yml` is the package source of truth.
- Package content paths are package-local unless a `deploy` rule explicitly projects them into the project tree.
- `docs/` is human documentation and is not deployed unless explicitly listed.
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

quarto:
  global:
    format.html.css:
      - assets/rhythmpress-toc.css
    format.html.include-in-header:
      - includes/rhythmpress-toc-header.html
  metadata: {}

deploy:
  files: []

starter-content:
  requires:
    - "#toc"

gitignore: []
quartoignore: []
generated-exclusions: []

external-tools: []
external-scripts: []

verification:
  - type: package-file-exists
    path: assets/rhythmpress-toc.mjs
  - type: generated-config-contains
    path: .rhythmpress-plugins/packages/toc-helper/assets/rhythmpress-toc.css
```

Required fields:

- `schema`
- `id`
- `version`
- `description`
- `compatibility`
- `quarto` or `deploy`

Required fields for each `deploy.files` entry:

- `from`
- `to`
- `mode`

Recommended fields:

- `features.provides`
- `depends-on`
- `conflicts-with`
- `generated-exclusions`
- `verification`

## Deploy Target Directory Policy

Reference-in-place wiring is the default. Deploy rules are the explicit escape
hatch for files that must exist in a project path or public output path.

Initial deploy target allowlist:

| Target path pattern | Ownership | Public-facing? |
| --- | --- | --- |
| `assets/**` | Public web/runtime asset | yes |
| `attachments*/**` | Content-facing asset | yes or source-facing |
| `.quarto-filters/**` | Quarto/Pandoc filter infrastructure | no |
| `_extensions/**` | Quarto extension infrastructure | mixed |
| `include/**` | Include snippets or source fragments | no |
| `templates/**` | Project-local authoring templates | no |

Package authors must not deploy into `.rhythmpress-plugins/`, `.git/`, `.site/`, `.site-*/`, generated profile outputs, or any root-level file unless a later spec extension explicitly allows it.

Package authors must not use project-branded hidden prefixes such as `.<project-name>-*` for deployed project-local files. If a future deploy class needs project-private support files, use static names so Rhythmpress can discover, audit, and reason about them predictably.

Generated outputs are never valid package targets:

```text
.site/
.site-*/
.quarto/
_quarto-<lang>.yml
_sidebar-*.generated.*
lang-switcher.generated.mjs
```

If a package needs CSS, JavaScript, filters, templates, helper scripts, or config snippets, those files must be declared explicitly in `plugin.yml` as Quarto wiring, verification input, or optional deploy input. Related behavior should be grouped into one package or into declared dependent packages rather than copied as scattered anonymous files.

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
2. project-local packages under `.rhythmpress-plugins/packages/`;
3. user package directory under `$RHYTHMPRESS_HOME/packages/`;
4. built-in Rhythmpress package directory shipped with the Python package;
5. paths listed in `RHYTHMPRESS_PLUGIN_PATH`, left to right.

First implementation may support only explicit paths and built-in packages, but the package metadata must not assume one fixed location.

## Project State Files

Project-local package state lives under `.rhythmpress-plugins/`:

```text
.rhythmpress-plugins/
  packages.yml
  packages/
    toc-helper/
  generated/
```

`packages.yml` is the active ordered package set. Generated plugin wiring is derived from `packages.yml` and package manifests. `_quarto.yml` may contain the Rhythmpress project skeleton, but package order must not be inferred from arbitrary `_quarto.yml` map order.

Optional deploy ownership state records:

- active package ID and version;
- package source digest;
- owning feature ID;
- deployed file targets;
- deployed file hashes;
- generated config contributions;
- generated exclusions registered;
- user-managed or package-managed status.

Optional future lockfile:

```text
.rhythmpress-plugins/packages.lock.yml
```

The lockfile is reserved for exact package resolution if remote registries or multiple package roots are added later. It is not required in the first implementation.

## Wiring And Optional Deployment

Reference-in-place wiring is the default. Rhythmpress reads `packages.yml`,
loads active package manifests in order, and generates Quarto config entries
that point back into `.rhythmpress-plugins/packages/<plugin-id>/`.

Wiring generation writes:

- generated plugin config fragments or generated profile config;
- optional ignore patterns;
- optional deploy ownership state.

Wiring generation must not write:

- generated artifacts;
- rendered output;
- files outside the allowed target directory classes unless the package spec is extended with an explicit new class;
- files not listed in `plugin.yml`;
- package docs unless listed as deployed files.

Install order:

1. resolve package and dependencies;
2. validate package schema and compatibility;
3. install package under `.rhythmpress-plugins/packages/<plugin-id>/`;
4. update `.rhythmpress-plugins/packages.yml`;
5. generate Quarto wiring from active package order;
6. apply optional `deploy.files` writes;
7. write deploy ownership state after all writes succeed;
8. run lightweight verification.

If any step fails before ownership state is written, the operation must fail without partially claiming ownership. Atomic file replacement should be used for individual file writes where possible.

## Plugin Lifecycle Triggers

Allowed triggers:

```sh
rhythmpress project create
rhythmpress plugin install <path-or-package-id>
rhythmpress plugin uninstall <plugin-id>
rhythmpress plugin list
rhythmpress plugin inspect <plugin-id-or-path>
rhythmpress project check
rhythmpress build
```

Trigger behavior:

- `project create` creates the core skeleton and may seed default package state when explicitly designed to do so.
- `plugin install` installs a package, adds it to `packages.yml`, regenerates plugin wiring, and applies optional deploy files.
- `plugin uninstall` removes a package from `packages.yml`, regenerates plugin wiring, and removes owned deployed files according to policy.
- `project check` verifies state and reports drift without writing.
- `rhythmpress build` may verify generated plugin wiring, but must not enable new packages by itself.

Build-trigger rule:

`rhythmpress build` must not enable new packages by itself. If it regenerates plugin wiring, it may only use packages already listed in `.rhythmpress-plugins/packages.yml`. If a conflict is detected, build fails before preprocessing.

## Install

Install means:

- package is resolved;
- dependencies are installed or already active first;
- package contents are placed under `.rhythmpress-plugins/packages/<plugin-id>/`;
- `.rhythmpress-plugins/packages.yml` records active order;
- generated Quarto wiring references package files in place;
- optional deployed files are copied or linked and ownership is recorded.

Example:

```sh
rhythmpress plugin install ./packages/toc-helper.tar.gz
rhythmpress plugin install toc-helper
```

Install must refuse:

- unknown package ID;
- incompatible package;
- dependency cycles;
- package conflicts;
- target path escaping project root;
- unmanaged deploy collisions;
- user-modified managed deploy collisions.

## Uninstall

Uninstall means:

- package ID is removed from `packages.yml`;
- generated Quarto wiring is regenerated from remaining active packages;
- generated exclusions are removed when no other active package owns them;
- deployed files are removed, preserved, or unmanaged according to policy;
- package directory is removed unless policy preserves archives.

Uninstall policy per deployed file:

| File State | Default Action |
|---|---|
| package-managed and unchanged | remove |
| package-managed but user-modified | preserve and mark unmanaged |
| shared by another active package | preserve |
| unmanaged | preserve |

The command must print every preserved modified file.

Generated config unpatching is normally regeneration from `packages.yml`, not a raw edit/delete operation against user-managed `_quarto.yml` or `_metadata-<lang>.yml`.

## Conflict Handling

Deploy conflict rules:

- unmanaged existing target file: conflict;
- managed target with matching hash: ok;
- managed target missing: recreate;
- managed target modified by user: conflict;
- target directory where file is expected: conflict;
- target file where directory is expected: conflict.

`--force` may repair missing or unchanged managed deployed files. It must not overwrite user-modified files unless a later explicit merge/update command exists.

## Updates

Package update is separate from install.

Future command shape:

```sh
rhythmpress plugin update <plugin-id>
```

Update policy:

- compare old package version and new package version;
- compute generated wiring and optional deployed-file changes;
- apply only unchanged managed deployed files automatically;
- preserve user-modified managed files and report conflicts;
- never delete user-modified files silently;
- record old and new package digests in ownership state.

The first implementation may reject updates and instruct users to deactivate/reactivate only when safe.

## Dependency Model

Dependencies are package IDs or feature IDs:

```yml
depends-on:
  - core
  - toc-helper
```

Rules:

- dependencies install before dependents;
- cycles are invalid;
- version constraints may be added later;
- package conflicts are checked after full dependency resolution.

Conflict example:

```yml
conflicts-with:
  - another-toc-helper
```

## Quarto Wiring Model

Quarto wiring contributions are declarative.

Contribution targets:

- `quarto.global`: contributes to global project config;
- `quarto.metadata.<lang>`: contributes to selected language metadata;
- `gitignore`: appends ignore patterns;
- `quartoignore`: appends Quarto ignore patterns.

Wiring merge rules:

- maps deep-merge;
- lists append in `.rhythmpress-plugins/packages.yml` order;
- duplicate handling is per-key and disabled unless declared safe;
- scalar conflicts fail unless the key is explicitly listed as last-wins;
- raw HTML blocks must be generated from package-owned include files or package-owned text values.

First implementation should restrict contribution shapes to well-known Quarto paths to keep behavior deterministic. Plugins must not edit `_quarto.yml` or `_metadata-<lang>.yml` directly.

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
- rendered bytes are package-local generated inputs unless explicitly deployed;
- deployed template output targets must be listed in `deploy.files`.

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
| `package-file-exists` | Package-local file exists. |
| `deployed-file-exists` | Optional deployed file exists. |
| `file-absent` | Generated or disabled target is absent. |
| `generated-config-contains` | Generated plugin config contains expected value. |
| `config-key-type` | Config key has expected type. |
| `ignore-contains` | Ignore file contains expected pattern. |
| `feature-enabled` | Desired feature state is enabled. |
| `package-installed` | Package is listed in `packages.yml` and present under `packages/`. |

Verification must not run Quarto, Playwright, LilyPond, network calls, or deployment tools unless explicitly requested by a separate lifecycle proof command.

## Build Interaction

`rhythmpress build` can use packages in two ways:

1. Check mode: verify active package directories and generated wiring before preprocessing.
2. Sync mode: regenerate plugin wiring from `packages.yml` before preprocessing.

Default should be conservative:

- check active package state;
- fail clearly on drift;
- allow an explicit project setting or flag to regenerate wiring during build.

Possible future flag:

```sh
rhythmpress build --sync-plugins
```

If build syncs plugins, it must use the same generated-wiring plan, deploy conflict checks, and ownership rules as `rhythmpress plugin install` / `rhythmpress plugin uninstall`.

## Example Package: TOC Helper

```text
toc-helper/
  plugin.yml
  assets/
    rhythmpress-toc.mjs
    rhythmpress-toc.css
  includes/
    rhythmpress-toc-header.html
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
quarto:
  global:
    format.html.css:
      - assets/rhythmpress-toc.css
    format.html.include-in-header:
      - includes/rhythmpress-toc-header.html
starter-content:
  requires:
    - "#toc"
verification:
  - type: package-file-exists
    path: assets/rhythmpress-toc.mjs
  - type: generated-config-contains
    path: .rhythmpress-plugins/packages/toc-helper/assets/rhythmpress-toc.css
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
quarto:
  global:
    metadata.lilypond-preamble: lilypond/lilypond-preamble.ly
    format.html.filters:
      - filters/lilypond.lua
    resources:
      - lilypond/*.ly
gitignore:
  - /lilypond-out/
generated-exclusions:
  - lilypond-out/
verification:
  - type: package-file-exists
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
- `.rhythmpress-plugins/packages.yml` active package ordering;
- reference-in-place Quarto wiring for known paths;
- optional `deploy.files` copy mode;
- `.gitignore` appends;
- deployed-file ownership records;
- check-only verification;
- optional default package seeding during `project create` only if explicitly designed.

First implementation may defer:

- tar archive input;
- remote package registries;
- signatures;
- update command;
- uninstall command;
- build-time sync;
- package lockfile;
- complex config unpatching.
