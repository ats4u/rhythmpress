# Rhythmpress Plugin System Spec

Status: draft
Updated: 20260507-173821

This document defines the proposed project-local plugin system for Rhythmpress.
The design goal is to keep plugin installation simple, ordered, inspectable, and
safe while avoiding unnecessary file copying into the project tree.

## Core Model

`.rhythmpress-plugins/packages/` stores package contents.
`.rhythmpress-plugins/packages.yml` stores the active package order.

```text
.rhythmpress-plugins/
  packages.yml
  packages/
    rhythmdo-theme/
      plugin.yml
      assets/
      filters/
      includes/
    rhythmdo-video.tar.gz
  generated/
    _quarto.plugins.yml
    _metadata-en.plugins.yml
    _metadata-ja.plugins.yml
```

Rules:

- A directory under `packages/` with `plugin.yml` is an installed package.
- A `.tar.gz` under `packages/` is an available archive, not active by itself.
- `packages.yml` is the active ordered set and the source of precedence.
- Package directory names remain as given; Rhythmpress must not invent renaming
  rules for users to learn.
- Generated files under `.rhythmpress-plugins/generated/` are derived state and
  may be deleted and regenerated.

## Active Package Order

`packages.yml` is intentionally YAML so users can add comments and hand-edit
ordering.

Minimal form:

```yaml
packages:
  - rhythmdo-theme
  - rhythmdo-video
  - rhythmdo-lilypond
```

Expanded form, reserved for later:

```yaml
packages:
  - id: rhythmdo-theme
    enabled: true
  - id: rhythmdo-video
    enabled: true
  - id: rhythmdo-lilypond
    enabled: false
```

Initial implementation should support only the minimal list form.

Ordering semantics:

- Packages are evaluated in `packages.yml` order.
- List-valued Quarto contributions append in that order.
- CSS precedence follows normal browser cascade. Later package CSS appears later
  in generated Quarto config.
- Filter order follows the generated list order.
- Scalar conflicts are rejected unless the key is explicitly declared as
  last-wins by the plugin wiring contract.

## Package Manifest

Each package directory must contain `plugin.yml`.

Example:

```yaml
id: rhythmdo-video
version: 0.1.0
name: Rhythmdo Video Embeds

quarto:
  global:
    format.html.css:
      - assets/rhythmdo-video-embed.css
    format.html.filters:
      - filters/video.lua
    format.html.include-in-header:
      - includes/video-header.html

  metadata:
    en:
      format.html.css:
        - assets/video-en.css
    ja:
      format.html.css:
        - assets/video-ja.css

deploy:
  files:
    - from: public/player.js
      to: assets/player.js
      mode: copy
```

Manifest path rules:

- Paths under `quarto` are relative to the package directory and are referenced
  in place by generated Quarto config.
- Paths under `deploy.files[].from` are relative to the package directory.
- Paths under `deploy.files[].to` are relative to the project root.
- `deploy` is optional and should be used only when a file must exist at a
  project path or public output path.

## Reference-In-Place Wiring

The default behavior is to reference package files in place instead of copying
them into normal project directories.

For a package at:

```text
.rhythmpress-plugins/packages/rhythmdo-video/
```

This manifest entry:

```yaml
quarto:
  global:
    format.html.css:
      - assets/rhythmdo-video-embed.css
```

generates a Quarto reference like:

```yaml
format:
  html:
    css:
      - .rhythmpress-plugins/packages/rhythmdo-video/assets/rhythmdo-video-embed.css
```

Benefits:

- Uninstall normally removes only the package directory and regenerates wiring.
- Plugin files do not scatter across the project tree.
- The package directory remains inspectable as the source of truth.
- File ownership is simple.

## Quarto Wiring Targets

Plugins may contribute to multiple config targets:

- global project config equivalent to `_quarto.yml`;
- language metadata config equivalent to `_metadata-<lang>.yml`;
- future target-specific metadata files if Rhythmpress adds them explicitly.

Plugins must not edit `_quarto.yml` or `_metadata-<lang>.yml` directly.
Rhythmpress owns generated wiring files or managed blocks.

Preferred generated files:

```text
.rhythmpress-plugins/generated/_quarto.plugins.yml
.rhythmpress-plugins/generated/_metadata-en.plugins.yml
.rhythmpress-plugins/generated/_metadata-ja.plugins.yml
```

If Quarto cannot include generated YAML fragments directly in the required
locations, Rhythmpress may instead compose generated `_quarto-<lang>.yml`
profiles during the existing profile-generation step.

## Supported Contribution Keys

Initial supported keys should be intentionally narrow:

```text
resources
format.html.css
format.html.filters
format.html.include-in-header
format.html.include-after-body
```

Additional keys require an explicit merge policy before support is added.

Merge policy:

- mappings recurse key by key;
- lists concatenate in active package order;
- duplicate list entries may be de-duplicated only if the key declares that as
  safe;
- scalars are rejected on conflict by default;
- last-wins scalar behavior is allowed only for keys explicitly listed by the
  spec.

## Deploy Files

`deploy.files` is the explicit escape hatch for files that must be projected
into the project tree.

Example:

```yaml
deploy:
  files:
    - from: public/player.js
      to: assets/player.js
      mode: copy
```

Supported modes:

- `copy`: default and cross-platform.
- `symlink`: optional development mode only.

Uninstall behavior:

- Copied files are removed only if their hash still matches the installed hash.
- Modified copied files cause uninstall to fail unless `--force` is used.
- Symlink uninstall removes only the symlink, never the target.

## Security And Path Validation

Package extraction and deploy validation must reject:

- absolute paths;
- `..` path traversal;
- unsafe symlinks;
- files targeting `.rhythmpress-plugins/`;
- files targeting `.git/`;
- files targeting `.site/` or `.site-*/`;
- files targeting generated profile outputs such as `_quarto-<lang>.yml`;
- files outside explicitly allowed deploy target classes.

Initial deploy target allowlist:

```text
assets/
.quarto-filters/
_extensions/
attachments/
include/
templates/
```

Root-level deploy files are denied by default. A root-level file requires an
explicit spec extension and conflict policy.

## Commands

Minimum command surface:

```sh
rhythmpress plugin install <path-or-package-id>
rhythmpress plugin uninstall <plugin-id>
rhythmpress plugin list
rhythmpress plugin inspect <plugin-id-or-path>
```

Install behavior:

1. Resolve the package archive or directory.
2. Validate `plugin.yml`.
3. If the input is `.tar.gz`, safely extract it into `packages/<plugin-id>/`.
4. If the input is a directory, copy it into `packages/<plugin-id>/` by default.
5. Add `<plugin-id>` to `packages.yml` if absent.
6. Regenerate plugin wiring.
7. Apply `deploy.files` if declared.
8. Run lightweight validation.

Uninstall behavior:

1. Validate that `<plugin-id>` is active or installed.
2. Remove generated wiring by regenerating from remaining active packages.
3. Remove owned deployed files if safe.
4. Remove `packages/<plugin-id>/`.
5. Remove `<plugin-id>` from `packages.yml`.

Archive files under `packages/*.tar.gz` may be kept unless a future `--purge`
mode explicitly removes them.

## Future Git URL Install

Git repository URLs are a useful future distribution input, but they are not in
scope for the next implementation session.

Possible future syntax:

```sh
rhythmpress plugin install https://github.com/example/rhythmpress-plugin-video.git
rhythmpress plugin install https://github.com/example/rhythmpress-plugin-video.git#v0.1.0
rhythmpress plugin install https://github.com/example/rhythmpress-plugin-video.git#<commit>
```

Rules for future Git URL support:

- A Git URL is an input source only.
- `.rhythmpress-plugins/packages/` remains the project source of truth after
  install.
- `packages.yml` remains the active package order and precedence source.
- Rhythmpress should clone or fetch into a temporary/cache location, validate
  `plugin.yml`, then copy the validated package into
  `.rhythmpress-plugins/packages/<plugin-id>/`.
- `plugin.yml:id` determines the installed package ID; the repository name does
  not.
- Branch refs may be accepted later, but Rhythmpress must record the resolved
  commit because branches are mutable.
- Tags or commit hashes are preferred for reproducible installs.
- Source metadata should record the Git URL, requested ref, and resolved commit
  in derived state or a future lock file.

Next implementation scope:

- Do not implement Git URL install.
- Focus on local package directories, optional archive handling if approved, the
  `packages.yml` order file, and generated Quarto wiring.

## Open Questions

- Can Quarto reliably consume YAML fragments under `.rhythmpress-plugins/`, or
  must Rhythmpress always compose generated profile YAML files?
- Which scalar Quarto keys, if any, should support last-wins plugin precedence?
- Should list de-duplication be global, per key, or disabled for the first
  implementation?
- Should inactive package directories be allowed, or should every directory
  under `packages/` be required to appear in `packages.yml`?
- Should `packages.yml` support comments generated by Rhythmpress, or should
  Rhythmpress preserve user comments by editing minimally?
