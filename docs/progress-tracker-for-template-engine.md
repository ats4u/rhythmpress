# Progress Tracker For Template Engine

Created: 20260505-154437

## Goal

Build a `rhythmpress project create` template engine that creates an empty, full-functioning Rhythmpress project with production-ready configuration.

Dedicated implementation specification:

- [Project Lifecycle Template Engine Specification](spec-rhythmpress-project-lifecycle-template-engine.md)
- [Scriptlet Dependency Map](spec-rhythmpress-project-scriptlet-dependency-map.md)
- [Plugin Feature Packs](spec-rhythmpress-project-plugin-feature-packs.md)
- [Plugin Package Format](spec-rhythmpress-project-plugin-package-format.md)

The generated project should be able to run the standard Rhythmpress lifecycle without manual framework wiring:

```sh
rhythmpress build
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize --output-dir .site --skip-social-cards
```

## Definition Of Done

- A new Rhythmpress command exists: `rhythmpress project create`.
- Future project lifecycle commands are planned for language management.
- The command creates source-layer project files, not generated artifacts.
- The created project has working Quarto base config.
- The created project has working Rhythmpress target configuration.
- The created project supports one or more language profiles.
- The created project has starter article masters and `.article_dir` sentinels.
- The created project can generate sidebar confs, sidebars, TOC includes, and `_quarto-<lang>.yml` profiles.
- Optional LilyPond support can be included.
- Optional GitHub Actions deployment workflow can be included.
- The generator is dogfooded against `thetokyojazz.com` through a staging run.

## Phased Checklist

- [ ] Rhythmpress docs pass
- [x] `rhythmdo-com` source/generated classification, substantially complete with carry-forward gaps below
- [ ] Template inventory
- [ ] Command interface design
- [ ] Template file implementation
- [ ] Generator implementation
- [ ] Verification fixture
- [ ] Tokyo Jazz dogfood run

## Source Classification Rules

- Source files are authored and should be emitted by the template engine.
- Generated files prove the framework works but should normally be regenerated.
- Quarto output directories and Rhythmpress output directories are build artifacts.
- Site-specific content from `rhythmdo-com` should not become the default template.
- Reusable support code, filters, and assets should be copied only after separating generic framework pieces from Rhythmdo branding.

## Candidate Command Shape

```sh
rhythmpress project create my-site \
  --title "My Site" \
  --site-url "https://example.com/" \
  --langs en,ja \
  --default-lang en \
  --with-lilypond \
  --with-github-actions
```

Planned project lifecycle command family:

```sh
rhythmpress project create my-site --langs en,ja --default-lang en
rhythmpress project add-language fr
rhythmpress project remove-language fr --dry-run
rhythmpress project check
```

The existing page scaffold command remains separate:

```sh
rhythmpress create-page my-topic --lang en
```

## Open Decisions

- Should the generator live only as a CLI command, or should it also expose a library function?
- Should LilyPond support be default-on or flag-controlled?
- Should social-card rendering be included by default or opt-in?
- Should the starter article be named `home`, `about`, or configurable?
- Should generated projects include Japanese metadata by default when `ja` is requested?
- Should templates use simple token replacement or structured YAML generation for config files?

## Verification Commands

Run these in a generated fixture project:

```sh
git status --short
rhythmpress build --dry-run
rhythmpress build --skip-clean
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize --output-dir .site --site-url https://example.test/ --skip-social-cards
```

## Expanded Multi-Pass Analysis Plan

The organizing question is:

> What is the smallest source tree that satisfies the Rhythmpress lifecycle, and what parameters are required to generate it safely?

### 1. File Provenance Graph

For every important file in `rhythmdo-com`, identify the owner:

- authored by a user
- emitted by `rhythmpress project create`
- emitted by `rhythmpress build`
- emitted by `rhythmpress render-sidebar`
- emitted by Quarto
- emitted by deploy/final artifact steps

Output:

- a copy/adapt/regenerate/ignore classification
- a list of files that must never be treated as canonical templates

Subpasses:

- [x] Pass 1a: visible inventory from `rg --files`
- [x] Pass 1b: hidden and ignored inventory from an explicit all-files command
- [x] Pass 1c: direct config and representative-master inspection

Pass 1 completion criteria:

- `.article_dir` sentinels are accounted for.
- Article `.gitignore` files are accounted for.
- Generated profiles and sidebar artifacts are classified.
- Language root pages such as `en/index.qmd` and `ja/index.qmd` are classified.
- Language-specific not-found pages such as `en/404.qmd` and `ja/404.qmd` are classified.
- A candidate minimum source tree is drafted from evidence rather than filename inference.

Carry-forward gaps:

- Resolved in Pass 3: `404.qmd`, `en/404.qmd`, and `ja/404.qmd` are authored source.
- Resolved in Pass 3: exact article `.gitignore` contents were inspected.
- Resolved in Pass 3: empty-project Git-date policy was chosen for implementation planning.

### 2. Command Dependency Graph

Status: complete.

Map Rhythmpress commands to their required inputs and generated outputs:

- `preproc` needs `master-<lang>.*`
- `preproc-clean` needs `.article_dir`
- `sidebar-confs` needs `_rhythmpress.conf` and per-article sidebars
- `render-sidebar` needs `RHYTHMPRESS_ROOT`, `yq`, and sidebar confs
- `quarto-profile` needs `_quarto.yml`, `_metadata-<lang>.yml`, and generated sidebar YAML
- `render-all` needs generated `_quarto-<lang>.yml`

Output:

- command-level input/output table
- required external tools and environment variables

Dependency:

- Pass 1b and Pass 1c are complete enough to start this pass.
- Carry-forward 404 and article-ignore gaps should not block command input/output mapping.

### 3. Empty-Project Build Problem

Status: complete for planning.

Determine how a brand-new generated project can build despite Git-date requirements.

Options to evaluate:

- initialize git and create an initial commit
- add a `--no-git-dates` mode
- add fallback dates for uncommitted starter masters
- document that the first commit is required before `rhythmpress build`

Output:

- chosen policy for generated starter projects
- required implementation or documentation changes

Chosen policy:

- Do not auto-create Git commits by default.
- Preserve strict Git-date behavior for existing projects unless an explicit fallback policy is enabled.
- Add a future opt-in fallback date policy for generated starter projects so `project create` output can build before the first user commit.
- Prefer Git dates when available; otherwise use starter front matter or generator timestamp with a visible warning.

### 4. Minimal Skeleton Reduction

Status: complete as a documentation-only skeleton specification.

Start from the `rhythmdo-com` framework shape and remove pieces until the lifecycle breaks.

Plan revision after Pass 3:

- Under the current discuss-first scope, do this as a documented skeleton specification from evidence.
- Do not create or delete fixture directories until a separate write/test approval is given.
- The skeleton must include starter date metadata and article `.gitignore` behavior, because Pass 3 showed a generated project otherwise fails before first commit.

Output:

- minimum valid source tree
- minimum language/profile files
- minimum starter article structure
- minimum sidebar inputs

Result:

- Minimum core source tree has been defined.
- Minimum per-language expansion has been defined.
- Minimum starter article structure has been defined.
- Minimum sidebar before/after inputs have been defined.
- Runtime validation is deferred to Pass 8 because fixture writes were intentionally out of scope.

### 5. Feature Pack Boundaries

Status: complete.

Separate the template engine into core and optional feature packs as an implementation contract table:

- core Rhythmpress project
- 404 pages
- language switcher
- multilingual support
- LilyPond support
- social cards
- GitHub Actions
- Cloudflare worker/router
- custom CSS/assets
- hooks/custom sidebar patching

Output:

- feature flag name
- default on/off status
- source files owned by the generator
- generated files intentionally excluded
- external dependencies
- required parameters
- conflicts or ordering constraints

Result:

- Core and optional feature-pack boundaries are recorded in findings.
- 404 pages are recommended/default-on but not lifecycle-minimum.
- Multilingual support is derived from `--langs`.
- Language switcher is default-on only for multilingual projects.
- LilyPond, social cards, GitHub Actions, Cloudflare router, custom assets, and hooks are opt-in.
- Softbreak cleanup is not default-on because it can affect wrapped space-delimited prose.

### 6. Parameter Model

Status: complete.

Use Pass 5 to define every project variable and its canonical owner:

- project title
- site URL
- default language
- language list
- author
- copyright
- GitHub repo
- output directory
- starter article name
- theme choice
- feature flags

Output:

- template variable table
- owning file or feature pack for each variable
- validation rules
- default values
- required vs optional status
- derived values that should not be stored twice

Result:

- Parameter table is recorded in findings.
- Language normalization and validation policy is recorded.
- Canonical owner rules are recorded.
- Derived values that should not be duplicated are recorded.

### 7. Idempotency And Overwrite Policy

Status: complete.

Define safe write behavior:

- refuse non-empty target directories by default
- `--force` overwrites only known template-owned files
- `--dry-run` reports planned writes
- never delete user content
- reserve `--update-framework` as a future mode

Output:

- write policy
- conflict policy
- dry-run output contract
- template ownership manifest concept
- file-by-file overwrite matrix for core and feature packs

Result:

- Default create mode accepts a missing or empty target directory and refuses existing non-empty targets.
- `--dry-run` reports the full planned write set without creating directories or files.
- `--force` is constrained to known template-owned paths and must not delete unknown files.
- A template ownership manifest is required before future safe update behavior can overwrite managed files without clobbering user edits.
- Generated artifacts remain outside `project create`; existing generated artifacts are ignored or reported, never removed.

### 8. Golden Fixture Verification

Status: complete for planning.

Define fixture verification in two phases:

- documentation-only fixture plan under the current read/write scope
- actual fixture execution later under separate write/test approval

Eventual checks:

- generated source tree matches expected files
- `rhythmpress build --skip-clean` works
- `_quarto-<lang>.yml` is generated
- sidebar files are generated
- `render-all` works
- `assemble` works
- `finalize --skip-social-cards` works

Output:

- repeatable fixture test plan
- acceptance checklist for `project create`
- separate checklist for uncommitted starter behavior after fallback-date implementation

Result:

- Defined core, multilingual, write-policy, lifecycle, and optional-pack fixture tracks.
- Split current strict-Git verification from future uncommitted-starter verification.
- Recorded expected source files, generated files, and files that must remain absent before build.
- Deferred actual fixture creation and lifecycle execution until separate write/test approval.

### 9. Generator Implementation Design

Status: complete.

Turn the analysis into an implementation plan:

- module and command layout
- template renderer or structured writer approach
- manifest data model
- write planner and dry-run output model
- CLI validation flow
- fallback Git-date integration point
- minimum test files and fixture scripts

Output:

- implementation design checklist
- file-level edit plan
- test plan for the first implementation patch

Result:

- Chose a new grouped command script: `src/rhythmpress/scripts/rhythmpress_project.py`.
- Chose a separate project lifecycle library module for the implementation.
- Chose structured data generation for YAML/JSON and small text renderers for QMD/gitignore files.
- Defined the write planner, manifest ownership model, CLI validation flow, and first implementation patch scope.
- Deferred broad optional packs and semantic update mode until after core creation is working.

### 10. Command Taxonomy And Concern Review

Status: next active pass.

Validate the corrected command model before coding:

- `rhythmpress project create`
- `rhythmpress project add-language`
- `rhythmpress project remove-language`
- possible `rhythmpress project check`
- existing `rhythmpress create-page`
- no `rhythmpress create page`
- no new `rhythmpress create-project` command

Output:

- plan corrections from user concerns
- final command taxonomy before implementation
- revised implementation patch scope

### 11. First Implementation Patch

Status: pending.

Implement the core generator behind `rhythmpress project create`:

- argument parser and command discovery
- language, path, and URL validation
- deterministic source file planning
- dry-run reporting
- safe write/apply behavior
- ownership manifest
- minimum verification script

Output:

- working `rhythmpress project create` command for the core skeleton
- automated verification for dry-run, file creation, generated-artifact exclusion, and conflict handling
- documented known limitation for current strict Git-date behavior if fallback is not included in the first patch

## Progress Log

### 20260506-235708 Rhythmpedia Legacy Archive

- Archived three historical Rhythmpedia-era docs from `rhythmdo-com/lib/doc/` under `docs/archive/rhythmpedia-legacy/`.
- Added an archive README marking the copied files as historical only, not current Rhythmpress implementation authority.
- Preserved useful background on CWD-agnostic path handling, conf-driven navigation, and old split/copy preprocessing behavior.

### 20260506-182447 First Patch Contract

- Added a first-patch contract to the lifecycle specification.
- Pinned the first implementation to `rhythmpress project create`, source skeleton generation, `_quarto.yml` with visible `rhythmpress:` defaults, core default TOC helper assets, manifest/conflict behavior, and focused verification.
- Explicitly deferred plugin package manager commands, build-time package sync, tar package support, CSS feature-pack migration, language add/remove commands, and full lifecycle proof.

### 20260506-182041 Easy-To-Forget Guardrails

- Added README index for `spec-rhythmpress-project-*` specs.
- Added lifecycle easy-to-forget implementation constraints.
- Re-emphasized that first patch is core only, package lifecycle commands are future work, build must not enable packages, `_rhythmpress.conf` remains an article target list, and generated artifacts are never templated.

### 20260506-181609 Plugin Package Format Spec

- Created `docs/spec-rhythmpress-project-plugin-package-format.md`.
- Defined editable directory packages and packed archive packages.
- Specified `plugin.yml`, package lookup, activation, deactivation, sync, build interaction, ownership, conflicts, updates, dependencies, security, config patches, template rendering, and verification.
- Linked the package format from the feature-pack and lifecycle specifications.

### 20260506-143043 Default TOC Helper Decision

- Updated the dependency map to migrate a cleaned visible TOC helper by default.
- Recorded that `toc-ul.mjs` is the behavior basis because it injects a visible nested TOC.
- Recorded that `toc-generator.mjs` should not be installed as-is because it is console/developer output.
- Added `toc-helper: true` to the `rhythmpress.project.features` skeleton.

### 20260506-142202 Scriptlet Dependency Specs

- Redid the read-only dependency pass over current `rhythmdo-com` scriptlets.
- Created `docs/spec-rhythmpress-project-scriptlet-dependency-map.md` with the dependency table and migration decisions.
- Created `docs/spec-rhythmpress-project-plugin-feature-packs.md` with the deterministic feature-pack design.
- Updated the lifecycle specification to link the new specs and expand the `rhythmpress.project.features` skeleton.

### 20260506-135256 Specification Prefix Clarification

- Renamed `docs/spec-project-lifecycle-template-engine.md` to `docs/spec-rhythmpress-project-lifecycle-template-engine.md`.
- Renamed `docs/spec-project-plugin-scriptlet-audit.md` to `docs/spec-rhythmpress-project-plugin-scriptlet-audit.md`.
- Documented the `spec-rhythmpress-project-*` naming convention in the root README.

### 20260506-133847 Plugin Scriptlet Audit Spec

- Created `docs/spec-rhythmpress-project-plugin-scriptlet-audit.md`.
- Defined the project plugin concept, scriptlet classification categories, manifest model, candidate plugin IDs, and dependency audit table.
- Set the next work as read-only dependency analysis of current `rhythmdo-com` scriptlets.

### 20260506-133001 Implementation Traps

- Added an implementation traps section to the dedicated specification.
- Recorded fragile points around root render rules, runtime QMD chunks, environment setup, sidebar generation, Git dates, ignore files, `_rhythmpress.conf`, language switcher output, `--force`, and manifest timing.

### 20260506-132825 Implementation Sequence

- Added the implementation sequence to the dedicated specification.
- Added the first patch cut line: core `rhythmpress project create` only, with no language lifecycle commands, lifecycle execution, Git-date fallback, or optional packs.

### 20260506-132722 Remaining Contract Details

- Added source-of-truth precedence across `_quarto.yml`, `.rhythmpress-template.json`, materialized files, and `_rhythmpress.conf`.
- Recorded that `_rhythmpress.conf` must remain an article-target list only under current command readers.
- Added a minimum `_metadata-<lang>.yml` shape.
- Added `project create` exit-code and dry-run output contracts.
- Added local verification environment expectations.

### 20260506-131806 Rhythmpress Project Config Skeleton

- Added a required user-editable `_quarto.yml` `rhythmpress.project` skeleton to the dedicated specification.
- Clarified that `.rhythmpress-template.json` is internal ownership state, not the primary customization surface.
- Defined future `project check` as comparing `_quarto.yml` desired state with materialized files and manifest state.

### 20260506-131114 Spec Audit Corrections

- Added explicit minimum `_quarto.yml` requirements to the dedicated specification.
- Added concrete QMD template contracts for root entry, language home, root 404, language 404, and starter masters.
- Recorded runtime prerequisites for executable lifecycle verification.
- Clarified that `rhythmpress build` generates `lang-switcher.generated.mjs` even though `project create` must not.
- Corrected lifecycle verification to pass `--site-url` to `finalize --skip-social-cards`.

### 20260506-123604 Dedicated Specification Draft

- Created `docs/spec-rhythmpress-project-lifecycle-template-engine.md` as the implementation specification for `rhythmpress project create` and future project lifecycle commands.
- Linked the dedicated specification from this tracker.
- Kept coding paused until the specification and remaining concerns are reviewed.

### 20260505-175902 Command Taxonomy Correction

- Replaced `rhythmpress create-project` as the primary planned command with `rhythmpress project create`.
- Added project lifecycle commands for future language management: `add-language`, `remove-language`, and possible `check`.
- Kept the existing `rhythmpress create-page` command as the page scaffold command.
- Explicitly dropped `rhythmpress create page` from the plan.
- Moved coding behind a command-taxonomy and concern-review pass.

### 20260505-173538 Pass 9 Generator Implementation Design

- Selected the implementation layout for project creation.
- Defined the structured writer/text renderer split.
- Specified the manifest schema, write planner actions, validation flow, and initial verification scope.
- Marked the first implementation patch as the next pass, later revised by the command taxonomy correction.

### 20260505-171253 Pass 8 Golden Fixture Verification Plan

- Defined the documentation-only golden fixture plan.
- Split verification into current strict-Git behavior and future uncommitted-starter fallback behavior.
- Added acceptance checks for source tree shape, generated artifact boundaries, write policy, lifecycle commands, and optional feature packs.
- Marked generator implementation design as the next active pass.

### 20260505-170912 Pass 7 Idempotency And Overwrite Policy

- Recorded the project creation write policy, conflict policy, dry-run contract, and ownership manifest concept.
- Defined `--force` as a constrained repair/overwrite mode for template-owned files, not as arbitrary replacement.
- Added the core and feature-pack overwrite matrix to findings.
- Marked Pass 8 golden fixture verification as the next active pass.

### 20260505-170513 Pass 6 Parameter Model

- Defined the project creation parameter table with required/default status, validation, canonical owner, and derived values.
- Recorded conservative language ID normalization and validation rules.
- Assigned canonical ownership across `_quarto.yml`, `_metadata-<lang>.yml`, `_rhythmpress.conf`, starter masters, and feature packs.
- Marked Pass 7 overwrite/idempotency policy as the next active pass.

### 20260505-170304 Pass 5 Feature-Pack Contract

- Defined core and optional feature-pack boundaries for project creation.
- Set multilingual support as derived from language list rather than a separate flag.
- Set language switcher default-on only for multilingual projects.
- Kept LilyPond, social cards, GitHub Actions, Cloudflare router, custom assets, and sidebar hooks opt-in.
- Recorded dependencies and ordering constraints for each feature pack.

### 20260505-165411 Post-Skeleton Plan Revision

- Revised Pass 5 into a feature-pack contract table instead of broad exploration.
- Revised Pass 6 to consume Pass 5 and tie every parameter to an owning file or feature pack.
- Expanded Pass 7 to include a template ownership manifest and overwrite matrix.
- Split Pass 8 into a documentation-only fixture plan now and actual fixture execution later under separate write/test approval.

### 20260505-165125 Pass 4 Skeleton Specification

- Defined the minimum source tree for a one-language generated project.
- Defined multilingual expansion files, starter article shape, sidebar before/after inputs, root ignore files, and article `.gitignore`.
- Excluded generated artifacts and optional packs from the minimum skeleton.
- Deferred runtime proof to Pass 8 because fixture writes were not approved for this pass.

### 20260505-164856 Pass 3 Completion And Plan Revision

- Recorded strict current Git-date behavior and the empty generated project failure mode.
- Chose the planning policy: no automatic commits; preserve strict Git dates by default; add an opt-in fallback policy for generated starter projects.
- Resolved 404 page classification as authored source.
- Inspected article `.gitignore` contents and carried forward attachment-rule tightening for implementation.
- Revised Pass 4 to be a documentation-only skeleton specification until a separate fixture write/test approval is given.

### 20260505-163655 Pass 1 Completion Update

- Marked the visible, hidden/ignored, and direct config/master provenance subpasses complete.
- Marked `rhythmdo-com` source/generated classification substantially complete.
- Carried forward unresolved 404 classification, exact article `.gitignore` contents, and empty-project Git-date policy.
- Set Command Dependency Graph as the next active pass.

### 20260505-162853 Refined Provenance Plan

- Split the file provenance graph into visible inventory, hidden/ignored inventory, and direct config/master inspection.
- Added explicit completion criteria for sentinels, article `.gitignore`, generated artifacts, language root pages, language-specific not-found pages, and the candidate minimum source tree.
- Marked command dependency mapping as dependent on the completed provenance inventory.

### 20260505-155128 Expanded Analysis Plan

- Added the contract-focused multi-pass analysis plan.
- Added explicit provenance, command dependency, empty-project build, minimal skeleton, feature pack, parameter, idempotency, and golden fixture passes.
- Recorded the core organizing question for the template engine.

### 20260505-154437 Initial Tracker

- Created the dedicated progress tracker.
- Recorded the goal as a reusable `rhythmpress project create` template engine.
- Established that the generator should emit source-layer files and let Rhythmpress regenerate derived files.
