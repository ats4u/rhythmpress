# Findings Of Templating

Created: 20260505-154437

## Initial Findings

- Rhythmpress is a lifecycle and generation framework, not a static file bundle.
- `rhythmdo-com` should be treated as a reference implementation, not copied directly as a project template.
- The template engine should create canonical source-layer files and then rely on Rhythmpress commands to create generated outputs.
- `_quarto-<lang>.yml` files are generated products.
- `_sidebar-*.generated.conf`, `_sidebar-*.generated.yml`, and `_sidebar-*.generated.md` are generated products.
- Generated article pages such as `<article>/<lang>/index.qmd` and `<article>/<slug>/<lang>/index.qmd` are generated products.
- Article masters named `master-<lang>.md` or `master-<lang>.qmd` are canonical content sources.
- Article directories require `.article_dir` sentinels so clean operations can run safely.
- `rhythmpress-preproc: copy` and `rhythmpress-preproc: split` are the main author-facing page generation modes.
- `rhythmpress-preproc-sidebar: false` suppresses sidebar contribution while still allowing page generation.

## Reference Analysis Notes

### Rhythmpress Lifecycle

- `rhythmpress build` handles clean, preproc, sidebar conf generation, sidebar rendering, profile generation, and language switcher generation.
- `rhythmpress render-all` renders all generated `_quarto-<lang>.yml` profiles.
- `rhythmpress assemble` merges `.site-*` profile outputs into `.site`.
- `rhythmpress finalize` runs final artifact generation such as sitemap and social-card metadata.
- `rhythmpress run-all` runs the standard build, render, assemble, and finalize lifecycle.

### Project Source Layer

Files that a template engine should normally create:

- `_quarto.yml`
- `_rhythmpress.conf`
- `_metadata-<lang>.yml`
- `_sidebar-<lang>.before.yml`
- `_sidebar-<lang>.after.yml`
- `index.qmd`
- starter article directories with `.article_dir`
- starter `master-<lang>.qmd` files
- `.gitignore`
- optional `.github/workflows/deploy.yml`

### Support Layer

Reusable support candidates:

- `filters/meta-dates.lua`
- `filters/lilypond.lua`
- `filters/remove-softbreaks.lua`
- `filters/include-files.lua`, if retained for compatibility
- `common-ly/`, when LilyPond support is requested
- generic website SCSS/CSS assets after removing Rhythmdo branding

### Generated Layer

Files that should be regenerated rather than used as canonical templates:

- `_quarto-<lang>.yml`
- `_sidebar-<lang>.generated.conf`
- `_sidebar-<lang>.generated.yml`
- `_sidebar-<lang>.generated.md`
- `lang-switcher.generated.mjs`
- generated article pages
- `.site`, `.site-*`, `.quarto`, and other build outputs

## Filter Findings

- `filters/include-files.lua` is loaded in `rhythmdo-com`, but no current authored source usage was found.
- `filters/remove-softbreaks.lua` is loaded and global. It removes Pandoc soft breaks, which supports Japanese source wrapping but can join words if space-delimited prose is manually wrapped.
- `filters/lilypond.lua` is active and depends on project-root resolution through `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR`.

## Future Findings

Use these sections as the analysis continues:

### Template Inventory

#### 20260505-161345 Pass 1: `rhythmdo-com` File Provenance Graph

Inventory command used:

```sh
cd ~/rhythmdo-com && rg --files
```

Scope note:

- This pass classifies the visible, non-ignored file inventory from `rg --files`.
- Hidden and ignored files are not exhaustively visible in this pass, so `.article_dir`, article `.gitignore`, generated `_quarto-<lang>.yml`, generated sidebar artifacts, `.site*`, and `.quarto` still need a follow-up inventory pass with an explicit hidden/ignored-file command.

Owner model:

- `rhythmpress project create` should own only the reusable source skeleton.
- Site authors should own content masters, source assets, branding, redirects, ad files, and local editorial material.
- `rhythmpress build` should own generated page trees, generated sidebar files, generated Quarto profiles, and generated language-switcher modules.
- `rhythmpress render-all`, Quarto, `assemble`, and `finalize` should own rendered and final artifacts.

Copy/adapt/regenerate/ignore classification:

- Adapt for core project generation:
  - `_quarto.yml`
  - `_rhythmpress.conf`
  - `_metadata-en.yml`
  - `_metadata-ja.yml`
  - `index.qmd`
  - `404.qmd`, if the generated project includes a default not-found page
  - `requirements.txt`, only after reducing it to generic Rhythmpress project dependencies
- Adapt for starter content only:
  - Article master pattern from directories such as `about/`, `contact/`, `contact-form/`, `cookies/`, `disclaimer/`, `privacy-policy/`, `join/`, `dojo/`, `offbeat-count/`, `offbeat-count-theory/`, `tatenori-theory/`, and `influence-of-japanese-language-on-cognition/`
  - The template should copy the convention, not the Rhythmdo-specific prose.
  - A generated starter article should use minimal `master-<lang>.qmd` files plus `.article_dir` and article `.gitignore` sentinels.
- Adapt as optional support packs:
  - `filters/meta-dates.lua`
  - `filters/remove-softbreaks.lua`
  - `filters/lilypond.lua`
  - `filters/include-files.lua`, if retained for compatibility
  - `filters/obsidian-image-dimensions.lua`, if the template supports Obsidian-style image dimensions
  - `common-ly/lilypond-preamble.ly`
  - `common-ly/chromatic-solfege.ly`
  - `templates/empty.markdown`
  - `templates/default.md`
  - `templates/default-of-journal.md`
  - `templates/default-of-thoughts.md`
  - `templates/ai-attribution-footer.html`
- Adapt only after separating generic behavior from Rhythmdo branding:
  - `assets/styles.css`
  - `assets/toc-generator.mjs`
  - `assets/toc-ul.mjs`
  - `assets/cookie-settings.mjs`
  - `assets/groovespace.mjs`
  - `assets/groovespace.css`
  - `assets/dojo.css`
  - `assets/ats4u-twitter-video.mjs`
  - `attachments/`
  - `attachments-src/`
- Adapt as deploy/final-artifact feature packs, not core:
  - `_redirects`
  - `Ads.txt`
  - Cloudflare worker/router files from the Rhythmpress examples rather than copying site-specific routing blindly
  - GitHub Actions workflow, if present in hidden or ignored files in a later pass
- Regenerate, never use as canonical template source:
  - `lang-switcher-ui.generated.mjs`
  - any generated `_quarto-<lang>.yml`
  - any `_sidebar-<lang>.generated.conf`
  - any `_sidebar-<lang>.generated.yml`
  - any `_sidebar-<lang>.generated.md`
  - article output pages such as `<article>/<lang>/index.qmd`
  - split-section output pages such as `<article>/<slug>/<lang>/index.qmd`
  - rendered output directories such as `.site`, `.site-*`, and `.quarto`
- Ignore for the template engine:
  - `drafts/`
  - `lib-translation/`
  - `memo*.md`, `memo.ods`, and local analysis notes
  - `WORKLOG.md`
  - `README.md`, except as project-specific documentation inspiration
  - `band-material-*`, `*.odt`, `*.fodt`, `*.ods`, `*.pdf`, and PDF-derived images
  - `offbeat-count-theory-draft/`
  - `essays/`
  - `bin/offbeat-count-join-en`
  - `getmeta.ua`
  - `test.py`
  - `test.lua`
  - `build`
  - `requirements`
  - `BAK_rhythmpress.hook-after._sidebar-ja.generated.yml.py`
- Treat as legacy/local copies, not canonical framework source:
  - `lib/`
  - `lib/doc/`
  - `lib/templates/`
  - `lib/git_dates.py`
  - `lib/groovespace.py`
  - `lib/rhythmpedia.py`
  - `lib/strip_header_comments.py`
  - `lib/mkgz`

Hook classification:

- `_rhythmpress.hook-after._sidebar-en.generated.yml.py` and `_rhythmpress.hook-after._sidebar-ja.generated.yml.py` demonstrate that projects can patch generated sidebar YAML after rendering.
- The hook mechanism is reusable, but the hook bodies are site-specific until inspected.
- A core generated project should not need hook files.
- Hook support belongs in a later optional customization feature or documentation section.

Minimum skeleton implications from this pass:

- The core template should generate configuration, metadata, root page, minimal sidebars, and one starter article.
- The starter article should prove both preprocessing and sidebar wiring without copying Rhythmdo content.
- LilyPond should be a feature flag because its support files and examples are meaningful only when the user needs music notation.
- Assets should start minimal; Rhythmdo's asset tree is too branded and content-specific to copy wholesale.
- Local `lib/` code in `rhythmdo-com` should not be a template source because Rhythmpress package source is the canonical implementation.

Files that must never become canonical templates:

- `_quarto-<lang>.yml`
- `_sidebar-<lang>.generated.conf`
- `_sidebar-<lang>.generated.yml`
- `_sidebar-<lang>.generated.md`
- `lang-switcher-ui.generated.mjs`
- generated article pages
- `.site*`
- `.quarto`
- copied framework code under `lib/`
- backups, drafts, local working files, and rendered binary outputs

Follow-up required:

- Run a hidden/ignored-file inventory for `rhythmdo-com` before finalizing the skeleton.
- Inspect `_quarto.yml`, `_rhythmpress.conf`, `_metadata-*.yml`, representative `master-<lang>.*` files, and hook files before turning this provenance graph into exact template variables.
- Confirm whether `en/index.qmd`, `ja/index.qmd`, `en/404.qmd`, and `ja/404.qmd` are authored source pages or generated/profile artifacts in the current project.

#### 20260505-163131 Pass 1b: Hidden And Ignored Inventory

Inventory commands used:

```sh
cd ~/rhythmdo-com && rg --files -uu
cd ~/rhythmdo-com && find . -name .article_dir -o -name .gitignore
cd ~/rhythmdo-com && find . -maxdepth 3 \( -name '_quarto-*.yml' -o -name '_sidebar-*.generated.*' -o -name '.quarto' -o -name '.site*' \)
```

Scope note:

- `rg --files -uu` reported a very broad inventory, including local dependencies and generated output roots such as `.venv`, `.quarto`, and `.site-en`.
- The targeted `find` commands provide the higher-signal result for sentinels and known generated artifacts.

Source-layer files confirmed:

- Article sentinel files are present and should be generated for starter article directories:
  - `about/.article_dir`
  - `contact/.article_dir`
  - `contact-form/.article_dir`
  - `cookies/.article_dir`
  - `disclaimer/.article_dir`
  - `dojo/.article_dir`
  - `influence-of-japanese-language-on-cognition/.article_dir`
  - `join/.article_dir`
  - `offbeat-count/.article_dir`
  - `offbeat-count-theory/.article_dir`
  - `privacy-policy/.article_dir`
  - `tatenori-theory/.article_dir`
- Article `.gitignore` files are present alongside the article sentinels and should be part of generated starter article directories.
- Root `.gitignore` and `.quartoignore` are source-layer project hygiene files and are likely needed in the generated skeleton.
- `.obsidianignore` and `.obsidian.vimrc` are editor/workspace source files, not Rhythmpress core files.
- `common-ly/.gitignore` is source-layer hygiene only when the LilyPond feature pack is enabled.

Generated artifacts confirmed:

- `_quarto-en.yml`
- `_quarto-ja.yml`
- `_sidebar-en.generated.conf`
- `_sidebar-ja.generated.conf`
- `_sidebar-en.generated.yml`
- `_sidebar-ja.generated.yml`
- `_sidebar-en.generated.md`
- `_sidebar-ja.generated.md`
- `attachments/_sidebar-en.generated.md`
- `.quarto`
- `.site-en`
- `.site-en/attachments/_sidebar-en.generated.md`

Regenerate/ignore classification additions:

- Regenerate:
  - `_quarto-<lang>.yml`
  - `_sidebar-<lang>.generated.conf`
  - `_sidebar-<lang>.generated.yml`
  - `_sidebar-<lang>.generated.md`
  - generated sidebar markdown under `attachments/`
  - `.quarto`
  - `.site-*`
- Ignore:
  - `.venv/`
  - `__pycache__/`
  - `.DS_Store`
  - `.obsidian/`
  - `.obsidian/.git/`
  - local editor files such as `.obsidian.vimrc`
  - package-internal `.gitignore` files under `.venv/`

Template implications:

- A generated project needs article `.article_dir` sentinels and article `.gitignore` files, even though normal visible inventory commands hide them.
- The root `.gitignore` should ignore Rhythmpress and Quarto generated outputs, including `_quarto-<lang>.yml`, `_sidebar-*.generated.*`, `.quarto`, and `.site*`.
- The core template should not emit `.venv`, `.obsidian`, `.DS_Store`, `__pycache__`, or rendered `.site-*` content.
- The existence of `_quarto-en.yml` and `_quarto-ja.yml` confirms language profiles are generated outputs in this reference project.
- The existence of generated sidebar YAML, Markdown, and conf files confirms sidebar artifacts should be regenerated rather than treated as template source.
- No `.github/` workflow file was identified in the high-signal hidden/generated inventory. GitHub Actions remains an optional feature pack to design from Rhythmpress deployment requirements, not from current visible `rhythmdo-com` evidence.

Follow-up required:

- Inspect article `.gitignore` contents during Pass 1c before defining the exact generated starter article ignore file.
- Inspect root `.gitignore` and `.quartoignore` before defining project hygiene templates.
- Inspect `_quarto.yml`, `_rhythmpress.conf`, sidebar before/after files, and representative masters to complete the source/generated classification.
- The status of `en/index.qmd`, `ja/index.qmd`, `en/404.qmd`, and `ja/404.qmd` is still unresolved until direct config inspection.

#### 20260505-163403 Pass 1c: Direct Config And Representative Master Inspection

Inventory commands used:

```sh
cd ~/rhythmdo-com && sed -n '1,260p' _quarto.yml
cd ~/rhythmdo-com && sed -n '1,260p' _rhythmpress.conf
cd ~/rhythmdo-com && sed -n '1,220p' _metadata-en.yml
cd ~/rhythmdo-com && sed -n '1,220p' _metadata-ja.yml
cd ~/rhythmdo-com && sed -n '1,220p' _sidebar-en.before.yml
cd ~/rhythmdo-com && sed -n '1,220p' _sidebar-en.after.yml
cd ~/rhythmdo-com && sed -n '1,220p' _sidebar-ja.before.yml
cd ~/rhythmdo-com && sed -n '1,220p' _sidebar-ja.after.yml
cd ~/rhythmdo-com && sed -n '1,160p' .gitignore
cd ~/rhythmdo-com && sed -n '1,160p' .quartoignore
cd ~/rhythmdo-com && sed -n '1,180p' index.qmd
cd ~/rhythmdo-com && sed -n '1,160p' en/index.qmd
cd ~/rhythmdo-com && sed -n '1,160p' ja/index.qmd
cd ~/rhythmdo-com && sed -n '1,180p' about/master-en.md
cd ~/rhythmdo-com && sed -n '1,180p' about/master-ja.md
cd ~/rhythmdo-com && sed -n '1,220p' offbeat-count/master-en.md
cd ~/rhythmdo-com && sed -n '1,220p' offbeat-count/master-ja.md
```

Core config findings:

- `_quarto.yml` is authored source and should be adapted, not copied.
- It owns the Quarto project identity, project type, output dir, preview port, render list, resource list, base website settings, global HTML format settings, global filters, include/header scripts, social-card settings, and a large site-specific `var` map.
- The template should generate a much smaller `_quarto.yml` and add optional sections only through feature flags.
- Generic core candidates in `_quarto.yml`:
  - `project.type: website`
  - `project.output-dir: .site`
  - a render list that avoids master files and generated/private content
  - `website.site-url`
  - language-switcher slot only when language-switcher support is enabled
  - `format.html.filters` only for selected support packs
  - minimal `format.html` settings needed by the generated project
- Site-specific or optional sections in `_quarto.yml`:
  - Rhythmdo title, branding, metadata variables, logos, GitHub ribbon, ad scripts, Cookiebot, Twitter/X widgets, custom assets, and social-card CSS
  - LilyPond resources and `metadata.lilypond-preamble`, unless `--with-lilypond` is enabled
  - social-card settings, unless social-card generation is enabled

Rhythmpress target config findings:

- `_rhythmpress.conf` is authored source and should be generated.
- In `rhythmdo-com`, it is a newline-delimited target list with commented-out targets.
- Enabled targets inspected:
  - `offbeat-count`
  - `join`
  - `dojo`
  - `about`
  - `disclaimer`
  - `contact`
  - `contact-form`
  - `privacy-policy`
  - `cookies`
- A generated project can start with a single starter article target.
- The command should treat `_rhythmpress.conf` as the canonical list of article directories for the build lifecycle.

Language metadata findings:

- `_metadata-en.yml` and `_metadata-ja.yml` are authored source and should be generated per requested language.
- They own language-specific values:
  - author
  - project title
  - website title and description
  - footer links
  - navbar logo and back-to-top text
  - sidebar logo/style defaults
  - theme and CSS choices
- The template parameter model should make these fields explicit rather than deriving them implicitly from `_quarto.yml`.
- The current metadata files are heavily branded and should be adapted structurally only.

Sidebar source findings:

- `_sidebar-en.before.yml` and `_sidebar-ja.before.yml` are authored source and currently contain an empty sidebar contents list.
- `_sidebar-en.after.yml` and `_sidebar-ja.after.yml` are empty in this reference project.
- A generated project should emit before/after sidebar source files per language, even if they are initially empty, because `render-sidebar` expects mergeable inputs.

Project hygiene findings:

- Root `.gitignore` is authored source and should be generated, but its current patterns need tightening before templating.
- Current `.gitignore` correctly ignores major generated outputs:
  - `.site`
  - `.site-*`
  - `.quarto`
  - `lang-switcher.generated.mjs`
  - `_freeze`
  - `*.generated.yml`
  - `*.generated.md`
  - `_quarto-*.yml`
  - `*.generated.conf`
- Current `.gitignore` also includes broad `_sidebar-*.yml`, which can match authored source files such as `_sidebar-en.before.yml` and `_sidebar-en.after.yml`.
- The generator should prefer narrower ignore patterns for generated sidebar artifacts, and should not hide authored sidebar before/after files.
- `.quartoignore` is authored source and should be generated with Quarto defaults plus Rhythmpress-specific generated outputs.

Root and language page findings:

- `index.qmd` is authored source, not a generated artifact.
- It calls `rhythmpress.create_runtime_root_entry("./_rhythmpress.conf", current_lang="en", strict=False)`.
- `en/index.qmd` and `ja/index.qmd` are authored language home pages, not article-generated pages.
- The language home pages call `rhythmpress.create_global_navigation("../_rhythmpress.conf", "<lang>", strict=False)`.
- Therefore, the minimum skeleton likely needs:
  - root `index.qmd`
  - one language home page per requested language
  - root/language page behavior parameterized by default language and language IDs

Representative master findings:

- `about/master-en.md` and `about/master-ja.md` use:
  - `rhythmpress-preproc: split`
  - `rhythmpress-preproc-args: ['--no-toc']`
  - `rhythmpress-preproc-sidebar: false`
- This pattern is useful for simple generated section pages that should not contribute to the sidebar.
- `offbeat-count/master-en.md` and `offbeat-count/master-ja.md` use:
  - `rhythmpress-preproc: split`
  - `rhythmpress-preproc-args: []`
  - default sidebar behavior
- This pattern proves the starter project should test sidebar contribution separately from no-sidebar pages.
- Both master patterns include `created` front matter, but Rhythmpress also injects dates from Git history. The empty-project Git-date policy remains unresolved.

Source/generated classification resolved in this pass:

- Source:
  - `_quarto.yml`
  - `_rhythmpress.conf`
  - `_metadata-<lang>.yml`
  - `_sidebar-<lang>.before.yml`
  - `_sidebar-<lang>.after.yml`
  - `.gitignore`
  - `.quartoignore`
  - `index.qmd`
  - `<lang>/index.qmd`
  - article `master-<lang>.md` and `master-<lang>.qmd`
  - article `.article_dir`
  - article `.gitignore`
- Generated:
  - `_quarto-<lang>.yml`
  - `_sidebar-<lang>.generated.conf`
  - `_sidebar-<lang>.generated.yml`
  - `_sidebar-<lang>.generated.md`
  - article output pages such as `about/rhythmdo/en/index.qmd`, `about/publisher/en/index.qmd`, `offbeat-count/<slug>/<lang>/index.qmd`
  - `.quarto`
  - `.site-*`
- Still unresolved:
  - `404.qmd`
  - `en/404.qmd`
  - `ja/404.qmd`
  - exact article `.gitignore` contents

Candidate minimum source tree from evidence:

```text
_quarto.yml
_rhythmpress.conf
_metadata-en.yml
_sidebar-en.before.yml
_sidebar-en.after.yml
.gitignore
.quartoignore
index.qmd
en/index.qmd
about/.article_dir
about/.gitignore
about/master-en.qmd
```

For multilingual generation, repeat language-owned files:

```text
_metadata-<lang>.yml
_sidebar-<lang>.before.yml
_sidebar-<lang>.after.yml
<lang>/index.qmd
about/master-<lang>.qmd
```

Optional feature pack source files:

- LilyPond:
  - `filters/lilypond.lua`
  - `common-ly/lilypond-preamble.ly`
  - selected `common-ly/*.ly` resources
- Softbreak behavior:
  - `filters/remove-softbreaks.lua`
- Date metadata:
  - `filters/meta-dates.lua`
- Include-file compatibility:
  - `filters/include-files.lua`
- Custom UI/assets:
  - `assets/`
  - `attachments/`
- Deploy/final artifact support:
  - `_redirects`
  - `Ads.txt`
  - `.github/workflows/*`, if designed later

Pass 1 conclusion:

- The minimum Rhythmpress project is not a copy of `rhythmdo-com`; it is a small authored source graph that lets Rhythmpress generate profiles, sidebars, language switcher files, article outputs, and render artifacts.
- `rhythmdo-com` confirms the core generator needs project config, language metadata, sidebar source hooks, root/language pages, an article target list, article sentinels, and starter masters.
- The next pass should map commands to these required inputs and outputs before implementation begins.

#### 20260505-165125 Pass 4: Minimal Skeleton Specification

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,260p' docs/findings-of-templating.md
cd ~/rhythmpress && sed -n '1,280p' docs/progress-tracker-for-template-engine.md
cd ~/rhythmpress && sed -n '1,220p' docs/concepts.md
cd ~/rhythmpress && sed -n '1,220p' docs/configuration.md
```

Scope note:

- This pass is a documentation-only skeleton reduction from the evidence gathered in Passes 1-3.
- No fixture directory was created, and no lifecycle command was run.
- The skeleton is therefore a target specification to validate in Pass 8, not a verified working fixture.

Minimum core source tree for one language:

```text
_quarto.yml
_rhythmpress.conf
_metadata-<lang>.yml
_sidebar-<lang>.before.yml
_sidebar-<lang>.after.yml
.gitignore
.quartoignore
index.qmd
<lang>/index.qmd
<starter-article>/.article_dir
<starter-article>/.gitignore
<starter-article>/master-<lang>.qmd
```

Minimum multilingual expansion:

```text
_metadata-<lang>.yml
_sidebar-<lang>.before.yml
_sidebar-<lang>.after.yml
<lang>/index.qmd
<starter-article>/master-<lang>.qmd
```

Recommended but not lifecycle-minimum source files:

```text
404.qmd
<lang>/404.qmd
requirements.txt
README.md
```

Core file responsibilities:

- `_quarto.yml`
  - Owns Quarto project type, output directory, render include/exclude rules, base website settings, and selected global format settings.
  - Must not contain Rhythmdo branding, ad scripts, Cookiebot, custom assets, or optional filters unless the relevant feature flag is enabled.
- `_rhythmpress.conf`
  - Owns the article target list.
  - Minimum content is one line naming `<starter-article>`.
- `_metadata-<lang>.yml`
  - Owns language-specific title, description, author, footer, navbar text, sidebar defaults, and optional language-specific theme/CSS choices.
- `_sidebar-<lang>.before.yml`
  - Minimum safe content:

```yml
website:
  sidebar:
    contents: []
```

- `_sidebar-<lang>.after.yml`
  - Minimum safe content should be a valid empty mapping:

```yml
{}
```

- `index.qmd`
  - Authored root entry page.
  - Should call the runtime root-entry helper with `_rhythmpress.conf` and the default language.
- `<lang>/index.qmd`
  - Authored language home page.
  - Should call the global navigation helper with `_rhythmpress.conf` and the current language.
- `<starter-article>/master-<lang>.qmd`
  - Authored starter content.
  - Should include front matter with `title`, starter date metadata, and a simple preproc mode.
  - Should not copy Rhythmdo prose.
- `<starter-article>/.article_dir`
  - Required sentinel for `preproc-clean`.
- `<starter-article>/.gitignore`
  - Required hygiene file so generated article output is not committed.

Minimum starter article mode:

- Use `rhythmpress-preproc: split` if the starter is meant to verify section-page generation and sidebar contribution.
- Use `rhythmpress-preproc: copy` if the starter is meant to be the smallest possible generated page.
- For the project generator, split mode is the better default test of the lifecycle because it exercises:
  - generated article language index
  - generated section page
  - generated per-article sidebar fragment
  - generated root sidebar conf
  - generated sidebar YAML/Markdown
  - generated `_quarto-<lang>.yml`

Minimum starter master shape:

```qmd
---
title: "About"
created: "<generator-datetime>"
rhythmpress-preproc: split
rhythmpress-preproc-args: []
---

Introductory text for the generated project.

## First Page {#first-page}

Starter content.
```

Notes:

- The `created` field alone does not satisfy current strict Git-date behavior.
- Pass 3 chose a future fallback-date policy for generated projects; until that is implemented, users must commit the starter master before running preprocessing.

Root `.gitignore` minimum:

```gitignore
/.site
/.site-*/
/.quarto/
/_freeze/
/lang-switcher.generated.mjs
/_quarto-*.yml
/_sidebar-*.generated.conf
/_sidebar-*.generated.yml
/_sidebar-*.generated.md
.DS_Store
.venv/
__pycache__/
```

Root `.quartoignore` minimum:

```gitignore
.quarto/
.site/
.site-*/
_site/
.ipynb_checkpoints/
.Rproj.user/
.Rhistory
.RData
.Ruserdata
_quarto-*.yml
_sidebar-*.generated.*
lang-switcher.generated.mjs
.venv/
```

Article `.gitignore` minimum:

```gitignore
*
!*/
!.article_dir
!.gitignore
!master-*.qmd
!master-*.md
!attachments*/
!attachments*/**
!attachments-src*/
!attachments-src*/**
```

Important distinction:

- The current `rhythmdo-com` root `.gitignore` includes `_sidebar-*.yml`, which can hide authored files such as `_sidebar-en.before.yml`.
- The generated project should use generated-artifact-specific patterns instead.

Files intentionally excluded from the minimum skeleton:

- `_quarto-<lang>.yml`
- `_sidebar-<lang>.generated.conf`
- `_sidebar-<lang>.generated.yml`
- `_sidebar-<lang>.generated.md`
- `lang-switcher.generated.mjs`
- generated article pages
- `.site`, `.site-*`, `.quarto`
- `filters/`
- `common-ly/`
- `assets/`
- `attachments/`
- `.github/workflows/`
- `_redirects`
- `Ads.txt`
- hook files

Open decisions carried to later passes:

- Default starter article name remains unresolved until Pass 6; use `<starter-article>` as the canonical placeholder.
- Whether 404 pages are core or `--with-404` remains a feature-pack decision for Pass 5.
- Whether language switcher support is core or optional should be decided in Pass 5.
- Exact implementation of fallback date policy remains an implementation task derived from Pass 3.

Pass 4 conclusion:

- The smallest source skeleton is now concrete enough to drive template inventory and parameter design.
- The skeleton should be validated by a golden fixture later; under the current scope, it is not yet runtime-proven.

#### 20260505-170304 Pass 5: Feature Pack Boundaries

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,280p' docs/progress-tracker-for-template-engine.md
cd ~/rhythmpress && sed -n '1,420p' docs/findings-of-templating.md
cd ~/rhythmpress && sed -n '1,260p' docs/tutorial-publish-github-cloudflare.md
cd ~/rhythmpress && sed -n '1,220p' docs/cloudflare-worker-router.md
cd ~/rhythmpress && sed -n '1,240p' examples/cloudflare-language-router/worker.mjs
cd ~/rhythmpress && sed -n '1,180p' examples/cloudflare-language-router/wrangler.toml
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_render_worker_router.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_render_lang_switcher_js.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_render_social_cards.py
cd ~/rhythmdo-com && sed -n '1,220p' filters/lilypond.lua
```

Scope note:

- This pass defines feature-pack boundaries for `rhythmpress project create`.
- It does not yet define final CLI parameter names; Pass 6 owns the parameter model.

Feature-pack contract table:

| Pack | Flag | Default | Source files emitted | Generated files excluded | Dependencies | Required parameters | Notes |
|---|---|---:|---|---|---|---|---|
| Core Rhythmpress project | implicit | on | `_quarto.yml`, `_rhythmpress.conf`, `_metadata-<lang>.yml`, `_sidebar-<lang>.before.yml`, `_sidebar-<lang>.after.yml`, `.gitignore`, `.quartoignore`, `index.qmd`, `<lang>/index.qmd`, starter article `.article_dir`, article `.gitignore`, `master-<lang>.qmd` | `_quarto-<lang>.yml`, `_sidebar-*.generated.*`, generated article pages, `.site*`, `.quarto` | Python, PyYAML, Quarto, Git, `yq`, `rsync` for full lifecycle | title, site URL, languages, default language, starter article name | Core should stay brand-neutral and asset-light |
| 404 pages | `--with-404` | on recommended | `404.qmd`, `<lang>/404.qmd` | rendered `404.html` | Quarto; runtime 404 helper for root page | languages, default language, localized titles/text | Useful for production sites, but not required for preprocessing/profile lifecycle |
| Language switcher | `--with-language-switcher` | on when more than one language | `_quarto.yml` navbar slot/include reference, generated language home/root pages compatible with runtime helpers | `lang-switcher.generated.mjs` | `rhythmpress render-lang-switcher-js` | languages, default language | Single-language projects should not need switcher UI by default |
| Multilingual support | implicit from `--langs` | on when more than one language | one `_metadata-<lang>.yml`, sidebar before/after, `<lang>/index.qmd`, and `master-<lang>.qmd` per language | `_quarto-<lang>.yml`, `.site-<lang>` | `LANG_ID` handling in build; Quarto profiles | languages, default language, per-language title/description optional | This is a core expansion, not a separate branded feature |
| LilyPond | `--with-lilypond` | off | `filters/lilypond.lua`, `common-ly/lilypond-preamble.ly`, optional `common-ly/*.ly`, `_quarto.yml` filter/resource metadata | `lilypond-out/`, rendered SVG cache outputs | `lilypond`; `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR`; Pandoc/Quarto filter runtime | none initially; optional preamble path | Real dependency and output cache make this opt-in |
| Softbreak cleanup | `--with-remove-softbreaks` | off or language-dependent | `filters/remove-softbreaks.lua`, `_quarto.yml` filter entry | none | Pandoc Lua filter runtime | none | Helpful for Japanese wrapping; risky for manually wrapped English prose |
| Metadata dates filter | `--with-meta-dates-filter` | on if current rendered pages require it | `filters/meta-dates.lua`, `_quarto.yml` filter entry | none | Pandoc Lua filter runtime | none | Separate from Git-date injection in preprocessing |
| Include-files filter | `--with-include-files` | off | `filters/include-files.lua`, `_quarto.yml` filter entry | none | Pandoc Lua filter runtime | none | No current authored usage found in `rhythmdo-com`; retain only for compatibility |
| Social cards | `--with-social-cards` | off | `_quarto.yml` `rhythmpress.social-cards` config; optional CSS selector config | social-card images and injected meta blocks in rendered HTML | Playwright, browser executable, rendered output dir, optional remote access | site URL, output dir optional | `finalize --skip-social-cards` should remain valid for minimal projects |
| GitHub Actions deployment | `--with-github-actions` | off | `.github/workflows/deploy.yml` | build artifacts, Pages branch output | GitHub Actions, full checkout history, Python, Quarto, `yq`, optional LilyPond, GitHub Pages action | GitHub branch, Python version, Quarto version, publish dir | Must use `fetch-depth: 0` because Git dates depend on history |
| Cloudflare worker/router | `--with-cloudflare-router` | off | worker/wrangler source or generated-source templates for language routing | `cloudflare-language-router.generated.mjs`, `wrangler.language-router.generated.toml` if generated by command | Cloudflare Workers, Wrangler, language IDs/default language | domain/zone route, languages, default language | Deployment pack, not site core; may depend on multilingual support |
| Custom CSS/assets | `--with-assets` or future theme flag | off/minimal | `assets/`, `attachments/`, optional CSS references in `_metadata-<lang>.yml` or `_quarto.yml` | optimized/rendered assets in `.site*` | none unless asset-specific | theme choice, logo paths optional | Rhythmdo assets are too branded to copy by default |
| Hook/custom sidebar patching | `--with-sidebar-hook` | off | `_rhythmpress.hook-after._sidebar-<lang>.generated.yml.py` templates only if explicitly requested | patched generated sidebar YAML | Python hook runtime during `render-sidebar` | language list | Powerful but site-specific; core should not need hooks |

Core vs optional decision:

- Core should include the minimum skeleton from Pass 4.
- 404 pages should be default-on for production-oriented projects, but treated as removable optional source because the lifecycle does not require them.
- Multilingual support is controlled by the language list; no separate flag is needed.
- Language switcher should be default-on only when the language list has more than one language.
- LilyPond, social cards, GitHub Actions, Cloudflare router, custom assets, and hooks must be opt-in.
- Softbreak cleanup should not be globally enabled by default because it can damage wrapped space-delimited prose.

Ordering and conflict notes:

- Multilingual support must be resolved before language switcher and Cloudflare router files are generated.
- Social cards depend on rendered `.site` output and should remain skippable in final verification.
- GitHub Actions must include full Git history checkout or generated projects will hit Git-date failures in CI.
- LilyPond requires project-root environment and external `lilypond`; it should also add generated cache/output patterns to ignores.
- Hook files should be generated only after the project has a concrete customization need.

Pass 5 conclusion:

- The core project can remain small and deterministic.
- Optional packs now have enough ownership boundaries to drive the parameter table in Pass 6.

#### 20260505-170513 Pass 6: Parameter Model

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,320p' docs/progress-tracker-for-template-engine.md
cd ~/rhythmpress && sed -n '/20260505-165125 Pass 4/,$p' docs/findings-of-templating.md
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/lang_ids.py
cd ~/rhythmpress && sed -n '1,240p' src/rhythmpress/lang_registry.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_render_worker_router.py
cd ~/rhythmpress && sed -n '1,180p' pyproject.toml
```

Scope note:

- This pass defines the parameter contract for `rhythmpress project create`.
- It does not implement CLI parsing.

Parameter table:

| Parameter | Required | Default | Validation | Canonical owner | Derived values to avoid storing twice |
|---|---:|---|---|---|---|
| positional `project_dir` | yes | none | path-like; target must not be an existing non-empty directory unless overwrite policy permits it | generator write policy | project slug may derive from basename if not supplied separately |
| `--title` | yes | none | non-empty string | `_quarto.yml` `project.title`; `_metadata-<lang>.yml` website title defaults | do not duplicate separate site title unless language-specific override is requested |
| `--site-url` | yes for production | none or `http://localhost/` for fixtures | absolute URL; normalize trailing slash | `_quarto.yml` `website.site-url`; finalize/deploy docs | sitemap/social-card site URL derives from this unless overridden at runtime |
| `--langs` | no | `en` | comma-separated unique language IDs; normalize `_` to `-`, lowercase; safe for filenames; should be accepted by `to_bcp47_lang_tag` | generator language model | `_metadata-<lang>.yml`, `<lang>/`, master filenames, profile names derive from this |
| `--default-lang` | no | first item in `--langs` | must be in normalized language list | root `index.qmd`; language switcher; Cloudflare router | default route and runtime current language derive from this |
| `--author` | no | empty or current package author only if explicitly chosen | string | `_metadata-<lang>.yml` `_author` | footer text should not invent author if omitted |
| `--description` | no | generic starter description | string | `_metadata-<lang>.yml` `website.description` | Open Graph/social-card descriptions derive from rendered pages later |
| `--copyright` | no | empty or generated from title/year if user opts in | string | `_metadata-<lang>.yml` footer | do not hard-code year ranges from Rhythmdo |
| `--starter-article` | no | `about` | safe relative directory name; no absolute path; no `..`; no spaces initially | `_rhythmpress.conf`; starter article directory | article target list entry derives from this |
| `--starter-title` | no | `About` | non-empty string | starter `master-<lang>.qmd` front matter and H2 text | sidebar labels derive from generated article outputs |
| `--starter-mode` | no | `split` | enum: `copy`, `split` | starter master front matter `rhythmpress-preproc` | output page layout derives from preproc mode |
| `--output-dir` | no | `.site` | relative path; should not equal project root; no parent traversal | `_quarto.yml` `project.output-dir` | `assemble` default and `finalize --output-dir` derive from this |
| `--preview-port` | no | unset or `5150` only if desired | integer 1-65535 | `_quarto.yml` `project.preview.port` | none |
| `--theme` | no | Quarto default or simple named theme | string or enum after implementation choice | `_metadata-<lang>.yml` `format.html.theme` | per-language theme files should not be generated unless assets pack exists |
| `--with-404` / `--no-404` | no | with 404 | boolean | 404 feature pack | language 404 pages derive from languages/default language |
| `--with-language-switcher` / `--no-language-switcher` | no | auto: on if multiple langs | boolean or auto | `_quarto.yml`; language switcher feature pack | `lang-switcher.generated.mjs` remains generated |
| `--with-lilypond` | no | false | boolean | LilyPond feature pack | filter/resource entries derive from flag |
| `--with-remove-softbreaks` | no | false | boolean | softbreak filter pack | filter entry derives from flag |
| `--with-meta-dates-filter` | no | true only if rendered metadata requires it | boolean | metadata dates filter pack | independent from Git-date preprocessing |
| `--with-include-files` | no | false | boolean | include-files filter pack | filter entry derives from flag |
| `--with-social-cards` | no | false | boolean | social-card feature pack | `finalize --skip-social-cards` remains valid regardless |
| `--with-github-actions` | no | false | boolean | GitHub Actions feature pack | workflow content derives from branch/tool version parameters |
| `--github-branch` | no | `main` or `production` after decision | branch-name-safe string | GitHub Actions workflow | trigger branch derives from this |
| `--python-version` | no | package-supported default such as `3.11` | supported Python version string | GitHub Actions workflow | do not duplicate outside workflow |
| `--quarto-version` | no | stable documented version or `latest` after decision | version string | GitHub Actions workflow | do not duplicate outside workflow |
| `--with-cloudflare-router` | no | false | boolean | Cloudflare router feature pack | router vars derive from language parameters |
| `--cloudflare-zone` | required only with router route generation | none | domain-like string | `wrangler.toml` or generated router config | route pattern derives from zone unless overridden |
| `--cloudflare-route` | no | `<zone>/*` if zone supplied | route pattern string | `wrangler.toml` | none |
| `--with-assets` | no | false | boolean | custom assets/CSS feature pack | CSS references derive from asset paths |
| `--logo` | no | none | relative path or URL | `_metadata-<lang>.yml` navbar/sidebar logo | per-language logo can override this |
| `--with-sidebar-hook` | no | false | boolean | hook feature pack | hook filenames derive from languages |
| `--dry-run` | no | false | boolean | generator execution policy | planned writes only; no source file owner |
| `--force` | no | false | boolean | generator overwrite policy | affects write behavior, not template content |

Language validation policy:

- Normalize language IDs with lowercase and `_` to `-`.
- Reject empty IDs, duplicates after normalization, path separators, whitespace, leading dots, and shell-special path characters.
- IDs must be safe in:
  - `master-<lang>.qmd`
  - `_metadata-<lang>.yml`
  - `_sidebar-<lang>.before.yml`
  - `<lang>/index.qmd`
  - `_quarto-<lang>.yml` generated later
- Use `to_bcp47_lang_tag` for Quarto `lang` values in generated profiles, but do not require every language to exist in the built-in registry.

Derived values:

- `_quarto-<lang>.yml` paths derive from language IDs and must never be generator source.
- `_sidebar-<lang>.generated.*` paths derive from language IDs and must never be generator source.
- `.site-<lang>` output directories derive from language IDs through `quarto-profile`.
- Runtime language switcher and Cloudflare router language lists derive from normalized `--langs`.
- Root and language home pages should receive default language and current language from the same normalized language model.

Canonical owner rules:

- `_quarto.yml` owns project-wide Quarto settings only.
- `_metadata-<lang>.yml` owns language-specific site metadata and presentation defaults.
- `_rhythmpress.conf` owns article targets and, if later supported, route metadata consumed by worker/router generation.
- Starter masters own starter article title, mode, and initial authored content.
- Feature flags own whether optional source files are emitted; generated artifacts are never stored as source parameters.

Pass 6 conclusion:

- The generator now has enough parameter structure to design CLI parsing and template rendering without duplicating values across files.
- Pass 7 should define safe writes around this parameter-owned source tree.

#### 20260505-170912 Pass 7: Idempotency And Overwrite Policy

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,340p' docs/progress-tracker-for-template-engine.md
cd ~/rhythmpress && sed -n '/20260505-165125 Pass 4/,$p' docs/findings-of-templating.md
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_create_page.py
cd ~/rhythmpress && rg -n "force|dry-run|overwrite|exists|write_if_changed|replace|unlink|rm -rf|manifest|generated" src/rhythmpress docs README.md
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_preproc_clean.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_sidebar_confs.py
cd ~/rhythmpress && sed -n '150,250p' src/rhythmpress/scripts/rhythmpress_quarto_profile.py
cd ~/rhythmpress && sed -n '1,125p' src/rhythmpress/scripts/rhythmpress_render_lang_switcher_js.py
cd ~/rhythmpress && sed -n '180,305p' src/rhythmpress/scripts/rhythmpress_render_worker_router.py
cd ~/rhythmpress && sed -n '60,110p' src/rhythmpress/scripts/rhythmpress_assemble.sh
cd ~/rhythmpress && sed -n '60,125p' src/rhythmpress/scripts/rhythmpress_render_sidebar.sh
cd ~/rhythmpress && sed -n '1280,1395p' src/rhythmpress/rhythmpress.py
date '+%Y%m%d-%H%M%S'
```

Scope note:

- This pass defines the future `project create` write contract.
- No implementation code was changed.
- The policy is intentionally stricter than existing generated-output commands because `project create` writes authored source files.

Existing Rhythmpress safety model observed:

- `create-page` is idempotent by writing only absent files through `_write_if_absent`; it has no `--dry-run` or `--force`.
- `quarto-profile`, `render-lang-switcher-js`, `render-worker-router`, and `render-nav` use write-if-changed helpers and atomic temp-file replacement for generated files.
- `sidebar-confs` has `--dry-run`, but writes generated conf files directly when not dry-running.
- `render-sidebar` intentionally overwrites generated sidebar YAML and Markdown files through shell redirection.
- `preproc-clean` is destructive only with `--apply`, requires `.article_dir`, and uses `--force` only to skip interactive confirmation.
- `assemble` deletes and recreates the final output directory with `rm -rf`, but that output is a build artifact, not source.

Create-project write policy:

- Default mode:
  - Accept a missing target directory.
  - Accept an existing empty target directory.
  - Refuse an existing non-empty target directory before writing anything.
  - Create only source-layer files selected by core and feature-pack parameters.
  - Never create generated artifacts such as `_quarto-<lang>.yml`, `_sidebar-*.generated.*`, `lang-switcher.generated.mjs`, `.site*`, or `.quarto`.
- `--dry-run`:
  - Normalize parameters and compute the same planned file set as a real run.
  - Print each planned path with an action: `create`, `keep`, `update-managed`, `conflict`, `blocked`, or `skip`.
  - Print summary counts.
  - Perform no writes, no directory creation, no manifest update, and no cleanup.
- `--force`:
  - Permit operation in a non-empty target directory.
  - Create missing planned files.
  - Keep byte-identical planned files.
  - Overwrite only files that are known template-owned and unmodified since the recorded template write.
  - Refuse to overwrite user-modified files, unmanaged files, symlinks, and file/directory type conflicts.
  - Never delete unknown files or generated artifacts.
- Future `--update-framework`:
  - Reserved for semantic migrations, feature-pack additions/removals, and possible three-way merges.
  - Should not be conflated with `--force`.

Conflict policy:

- A planned file that exists with different content is a conflict unless template ownership can be proven.
- Template ownership is proven by a manifest entry that records the path, feature pack, last template hash, and current managed status.
- If the file hash differs from the manifest hash, treat it as user-modified and refuse overwrite.
- If a planned file path is a directory, symlink, device, or other non-regular file, block the run.
- If an unknown file does not collide with a planned path, preserve it. In default mode the non-empty directory still blocks creation; in `--force` mode it may remain untouched.

Template ownership manifest concept:

- Emit a root manifest such as `.rhythmpress-template.json` during successful creation.
- Store at least:
  - manifest schema version
  - Rhythmpress version
  - normalized parameters that affect generated source shape
  - selected feature packs
  - one entry per managed path with feature pack, file kind, and content hash
- The manifest is not a Quarto/Rhythmpress generated artifact; it is generator metadata for safe future repair or update decisions.
- The manifest should be updated only after all planned writes succeed.

Overwrite matrix:

| Path class | Default if absent | Default if exists identical | Default if exists different | `--force` behavior | Notes |
|---|---|---|---|---|---|
| Target directory | create | allow only if empty | refuse non-empty before writes | allow non-empty but preserve unknown files | Missing parent handling should be conservative and explicit |
| `_quarto.yml` | create | keep | conflict | overwrite only if manifest-owned and unmodified | User-facing source; no blind replacement |
| `_rhythmpress.conf` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Article target list is user-editable after creation |
| `_metadata-<lang>.yml` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Per-language metadata is user-editable |
| `_sidebar-<lang>.before.yml` / `.after.yml` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Do not hide with broad `_sidebar-*.yml` ignore rules |
| `.gitignore` / `.quartoignore` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Future update mode may merge, but v1 should not |
| `index.qmd` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Root runtime entry is source |
| `<lang>/index.qmd` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Language home pages are source |
| `<starter-article>/.article_dir` | create empty file | keep if regular file | block if not a regular file | keep or create only | Sentinel must not be replaced with content |
| `<starter-article>/.gitignore` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Protects generated article output from VCS |
| `<starter-article>/master-<lang>.qmd` | create | keep | conflict | overwrite only if manifest-owned and unmodified | Starter content becomes user content immediately |
| 404 source files | create when selected | keep | conflict | overwrite only if manifest-owned and unmodified | Default-on recommended, but not lifecycle-minimum |
| Optional filter/support files | create when selected | keep | conflict | overwrite only if manifest-owned and unmodified | LilyPond/filter packs must own their own ignore additions |
| GitHub Actions workflow | create when selected | keep | conflict | overwrite only if manifest-owned and unmodified | Deployment files are user-editable after creation |
| Cloudflare router source/config | create when selected | keep | conflict | overwrite only if manifest-owned and unmodified | Generated router outputs remain excluded |
| Generated artifacts | do not create | ignore/report | ignore/report | never delete or overwrite | Owned by lifecycle commands, not `project create` |
| Unknown user files | do not touch | do not touch | do not touch | preserve | May block default mode only because target is non-empty |

Pass 7 conclusion:

- The implementation should separate initial creation, forced repair, and future framework updates.
- `--force` should not mean "replace the directory"; it should mean "apply the planned template writes where ownership and no-user-edit conditions allow it."
- A manifest is the cleanest single source of truth for template ownership and prevents drift between dry-run reporting, write behavior, and future update decisions.
- Pass 8 can now define a golden fixture plan that verifies this policy without relying on broad destructive behavior.

#### 20260505-171253 Pass 8: Golden Fixture Verification Plan

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,420p' docs/progress-tracker-for-template-engine.md
cd ~/rhythmpress && sed -n '/20260505-170912 Pass 7/,$p' docs/findings-of-templating.md
cd ~/rhythmpress && sed -n '1,360p' docs/commands.md
cd ~/rhythmpress && sed -n '1,260p' docs/workflows.md
date '+%Y%m%d-%H%M%S'
```

Scope note:

- This pass defines the golden fixture plan only.
- No fixture directory was created.
- No lifecycle command was executed.
- Actual fixture creation, Git operations, rendering, and final artifact checks require separate write/test approval.

Fixture tracks:

| Track | Purpose | Expected status before implementation |
|---|---|---|
| `core-en-min` | One-language minimum source skeleton, with optional 404 and language switcher disabled if those flags exist | Planned only |
| `core-en-ja` | Multilingual project with language switcher default-on and 404 default-on | Planned only |
| `write-policy` | Dry-run, non-empty target refusal, `--force`, manifest ownership, conflict handling | Planned only |
| `strict-git-current` | Current behavior where starter masters must be committed before preprocessing | Planned only |
| `uncommitted-starter-fallback` | Future behavior where generated starter masters can build before first commit using explicit fallback dates | Blocked until fallback implementation |
| `optional-packs` | LilyPond, GitHub Actions, social cards, Cloudflare router, assets, and hooks | Planned after core implementation |

Core fixture command shape:

```sh
rhythmpress project create core-en-min \
  --title "Fixture Site" \
  --site-url "https://example.test/" \
  --langs en \
  --default-lang en \
  --starter-article about \
  --starter-title "About" \
  --starter-mode split \
  --dry-run

rhythmpress project create core-en-min \
  --title "Fixture Site" \
  --site-url "https://example.test/" \
  --langs en \
  --default-lang en \
  --starter-article about \
  --starter-title "About" \
  --starter-mode split
```

Expected one-language source tree after creation:

```text
_quarto.yml
_rhythmpress.conf
_metadata-en.yml
_sidebar-en.before.yml
_sidebar-en.after.yml
.gitignore
.quartoignore
.rhythmpress-template.json
index.qmd
en/index.qmd
about/.article_dir
about/.gitignore
about/master-en.qmd
```

Expected multilingual additions for `--langs en,ja --default-lang en`:

```text
_metadata-ja.yml
_sidebar-ja.before.yml
_sidebar-ja.after.yml
ja/index.qmd
about/master-ja.qmd
```

Expected default-on production files, if `--with-404` remains default:

```text
404.qmd
en/404.qmd
ja/404.qmd
```

Files that must be absent immediately after `project create`:

```text
_quarto-en.yml
_quarto-ja.yml
_sidebar-en.generated.conf
_sidebar-ja.generated.conf
_sidebar-en.generated.yml
_sidebar-ja.generated.yml
_sidebar-en.generated.md
_sidebar-ja.generated.md
lang-switcher.generated.mjs
.site
.site-en
.site-ja
.quarto
about/en/index.qmd
about/ja/index.qmd
about/_sidebar-en.yml
about/_sidebar-ja.yml
```

Current strict-Git lifecycle fixture:

```sh
cd core-en-min
git init
git add .
git commit -m "Initialize Rhythmpress fixture"
eval "$(rhythmpress eval)"
rhythmpress build --dry-run
rhythmpress build --skip-clean
rhythmpress render-all
rhythmpress assemble
rhythmpress finalize --output-dir .site --site-url https://example.test/ --skip-social-cards
```

Expected files after `rhythmpress build --skip-clean`:

```text
_quarto-en.yml
_sidebar-en.generated.conf
_sidebar-en.generated.yml
_sidebar-en.generated.md
about/_sidebar-en.yml
about/en/index.qmd
about/<starter-section-slug>/en/index.qmd
```

Expected files after multilingual build:

```text
_quarto-en.yml
_quarto-ja.yml
_sidebar-en.generated.conf
_sidebar-ja.generated.conf
_sidebar-en.generated.yml
_sidebar-ja.generated.yml
_sidebar-en.generated.md
_sidebar-ja.generated.md
lang-switcher.generated.mjs
about/_sidebar-en.yml
about/_sidebar-ja.yml
about/en/index.qmd
about/ja/index.qmd
about/<starter-section-slug>/en/index.qmd
about/<starter-section-slug>/ja/index.qmd
```

Expected files after render, assemble, and finalize:

```text
.site-en/
.site/
```

Additional final-artifact checks:

- `render-all` must create one `.site-<lang>` directory per generated `_quarto-<lang>.yml`.
- `assemble` must merge `.site-*` into `.site`.
- `finalize --skip-social-cards` must succeed without requiring Playwright or browser setup.
- Social-card files are tested only in a separate optional-pack fixture.

Write-policy fixture checks:

- `--dry-run` must leave the target path absent when the target did not exist.
- Default create must refuse an existing non-empty target before writing any file.
- A second create with the same parameters must report identical managed files as `keep` or no-op.
- `--force` may create missing planned files in a non-empty target but must preserve unknown files.
- `--force` must refuse a changed managed file whose current hash differs from the manifest hash.
- Generated artifacts present in the target must be ignored or reported, not deleted.
- `.rhythmpress-template.json` must not list generated artifacts as managed source files.

Uncommitted starter fallback acceptance, after implementation:

- Create a fixture without `git init`.
- Run `eval "$(rhythmpress eval)"`.
- Run `rhythmpress build --skip-clean`.
- Build must succeed.
- Output must contain visible fallback-date warnings.
- Generated pages must receive `cdate` and `mdate` from starter front matter or generator timestamp.
- After `git init`, `git add`, and first commit, rerunning build should use Git dates automatically.

Optional-pack fixture checks:

- `--with-lilypond` should add LilyPond filter/source files and ignore generated LilyPond cache outputs.
- `--with-github-actions` should add a workflow with full Git history checkout.
- `--with-social-cards` should add config only; actual social-card rendering remains a rendered-output test.
- `--with-cloudflare-router` should add only source/config inputs, while generated worker/router outputs remain excluded unless produced by the router command.
- `--with-sidebar-hook` should create hook templates only when explicitly requested.

Pass 8 conclusion:

- The fixture plan now covers source generation, generated-artifact boundaries, lifecycle execution, write safety, and the known Git-date gap.
- The next pass should stop broad exploration and design the implementation patch: command/module layout, structured writers or templates, manifest model, CLI validation, and test entry points.

#### 20260505-173538 Pass 9: Generator Implementation Design

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,220p' pyproject.toml
cd ~/rhythmpress && sed -n '1,160p' src/rhythmpress/scripts/cli.py
cd ~/rhythmpress && sed -n '1280,1395p' src/rhythmpress/rhythmpress.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/lang_registry.py
cd ~/rhythmpress && rg -n "create-page|scripts|entry|rhythmpress_" src/rhythmpress pyproject.toml README.md docs
date '+%Y%m%d-%H%M%S'
```

Scope note:

- This pass designs the implementation patch.
- No implementation code was changed.

Command and module layout:

- Add `src/rhythmpress/scripts/rhythmpress_project.py`.
  - The existing dispatcher automatically discovers `rhythmpress_<command>.py` files, so `rhythmpress project ...` should be implemented as a grouped command whose first argument is a project subcommand.
  - Initial subcommand: `create`.
  - Future subcommands: `add-language`, `remove-language`, and possible `check`.
  - No new console entry point is required in `pyproject.toml`.
  - The script should stay thin: parse the grouped command, call the library module, print the plan/result, and return an exit code.
- Add a project lifecycle library module, such as `src/rhythmpress/project_lifecycle.py`.
  - Own the data model, validation, template rendering, write planning, manifest handling, and apply logic for project-level operations.
  - Keep this out of `rhythmpress.py`; that file already contains broad runtime helpers and should not absorb the full project generator.
- Add a verification script or focused test entry point after the library exists.
  - Existing repo convention includes `src/rhythmpress/scripts/verify_*.py` scripts.
  - First verification target should be `src/rhythmpress/scripts/verify_project_create.py` unless a formal test directory is introduced first.

Renderer strategy:

- Use structured data for YAML and JSON where possible.
  - `_quarto.yml`
  - `_metadata-<lang>.yml`
  - `_sidebar-<lang>.before.yml`
  - `_sidebar-<lang>.after.yml`
  - `.rhythmpress-template.json`
- Use small deterministic text renderers for source files that are naturally textual.
  - `.gitignore`
  - `.quartoignore`
  - `index.qmd`
  - `<lang>/index.qmd`
  - `404.qmd`
  - `<lang>/404.qmd`
  - starter `master-<lang>.qmd`
- Do not add a template-engine dependency such as Jinja for the first patch.
- Prefer one canonical project spec object over duplicated literals across rendering, dry-run output, and manifest entries.

Core data model:

- `ProjectSpec`:
  - target directory
  - title
  - site URL
  - normalized language IDs
  - default language
  - optional author/description/copyright
  - starter article path
  - starter title
  - starter mode
  - output dir
  - feature flags
  - generator timestamp
- `PlannedFile`:
  - relative path
  - file kind
  - feature pack
  - rendered bytes or text
  - executable bit, if ever needed later
  - source/generated classification
- `PlanAction`:
  - `create`
  - `keep`
  - `update-managed`
  - `conflict`
  - `blocked`
  - `skip`
- `ApplyResult`:
  - action counts
  - written paths
  - conflicts
  - blocked paths
  - manifest path

Manifest schema v1:

```json
{
  "schema": 1,
  "generator": "rhythmpress project create",
  "rhythmpress_version": "0.1.2",
  "created_at": "YYYYMMDD-HHMMSS",
  "parameters": {
    "title": "Fixture Site",
    "site_url": "https://example.test/",
    "langs": ["en"],
    "default_lang": "en",
    "starter_article": "about"
  },
  "feature_packs": ["core", "404"],
  "files": [
    {
      "path": "_quarto.yml",
      "kind": "source",
      "feature": "core",
      "sha256": "<hex>"
    }
  ]
}
```

Write planner flow:

1. Parse CLI arguments.
2. Normalize and validate parameters.
3. Build `ProjectSpec`.
4. Render all selected `PlannedFile` entries.
5. Validate that no planned entry is generated-layer output.
6. Load existing manifest if present.
7. Inspect target path state.
8. Assign one `PlanAction` per planned path.
9. If `--dry-run`, print actions and exit without creating the target directory.
10. If any conflict or blocked action exists, fail before writing.
11. Write files to temporary sibling files and replace regular files atomically where applicable.
12. Write or update `.rhythmpress-template.json` only after all planned writes succeed.

Validation flow:

- Target path:
  - Missing or empty is valid by default.
  - Existing non-empty requires `--force`.
  - Symlink target is blocked.
  - Existing file at project directory path is blocked.
- Language IDs:
  - Normalize lowercase and `_` to `-`.
  - Reject empty IDs, duplicates after normalization, path separators, whitespace, leading dots, and shell-special path characters.
  - Use `to_bcp47_lang_tag()` for Quarto `lang` output.
- Default language:
  - Must be in the normalized language list.
- Starter article:
  - Relative path only.
  - No `..`, absolute path, leading dot segment, whitespace, or shell-special characters.
- Site URL:
  - Absolute URL for production use.
  - Normalize trailing slash.
- Output dir:
  - Relative path.
  - No parent traversal.
  - Must not equal `.`.

First implementation patch scope:

- Implement core and default 404 source generation.
- Implement multilingual expansion from `--langs`.
- Implement language switcher source references only when multiple languages are requested; generated JS remains produced by `rhythmpress build`.
- Implement `.rhythmpress-template.json`.
- Implement `--dry-run` and `--force` according to Pass 7.
- Implement validation and deterministic rendering.
- Add a verification script covering:
  - dry-run creates no files
  - one-language project writes expected source files
  - multilingual project writes language-specific source files
  - generated artifacts are absent after creation
  - non-empty target refusal
  - conflict handling
  - manifest excludes generated artifacts

Deferred from first patch unless implementation remains small:

- Git-date fallback behavior for uncommitted starter masters.
- LilyPond feature pack.
- GitHub Actions feature pack.
- Social-card feature pack.
- Cloudflare router feature pack.
- Sidebar hook feature pack.
- Future `--update-framework` semantic migration mode.

Git-date fallback integration point:

- Current preprocessing calls Git-date helpers for generated `cdate` and `mdate`.
- The fallback should be implemented where master-file date resolution happens, not inside `project create` write logic.
- `project create` should emit explicit starter date metadata now so the future fallback has a source to read.
- The fallback should be gated by explicit generated-project metadata or a narrow front matter/project setting, preserving strict Git-date behavior for existing projects.

Pass 9 conclusion:

- The critical engineering boundary is to keep project generation as a deterministic write planner with a single source-of-truth spec and manifest.
- Runtime lifecycle behavior remains owned by existing Rhythmpress commands.
- The command name was revised after this pass: project creation belongs under the `rhythmpress project` command family.

#### 20260505-175902 Command Taxonomy Correction

Scope note:

- This correction updates the plan before coding.
- It reflects the project language-lifecycle concern and keeps the existing page scaffold command separate.
- It does not examine any additional concerns yet.

Corrected command taxonomy:

```sh
rhythmpress project create my-site --langs en,ja --default-lang en
rhythmpress project add-language fr
rhythmpress project remove-language fr --dry-run
rhythmpress project check
rhythmpress create-page my-topic --lang en
```

Dropped command shapes:

```sh
rhythmpress create-project
rhythmpress create page
```

Rationale:

- Project creation, language addition/removal, manifest inspection, and future update behavior are the same project-lifecycle domain.
- Therefore, project skeleton creation should be `rhythmpress project create`, not a flat `create-project` command.
- The existing `rhythmpress create-page` command already owns page/article directory scaffolding and should remain separate.
- No grouped `rhythmpress create page` command is planned.

Implementation correction:

- Use `src/rhythmpress/scripts/rhythmpress_project.py` as the grouped project command entry.
- Implement `create` first.
- Reserve `add-language`, `remove-language`, and `check` for later project lifecycle patches.
- Use a project lifecycle library module rather than a `create_project`-named command module.
- First implementation should not start until the command taxonomy and remaining concerns are reviewed.

### Command Design

#### 20260505-164041 Pass 2: Command Dependency Graph

Inspection commands used:

```sh
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_build.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_preproc_clean.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_preproc.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_preproc_copy.py
cd ~/rhythmpress && sed -n '1,320p' src/rhythmpress/scripts/rhythmpress_preproc_split.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_sidebar_confs.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_render_sidebar.sh
cd ~/rhythmpress && sed -n '1,320p' src/rhythmpress/scripts/rhythmpress_quarto_profile.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_render_toc.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_render_lang_switcher_js.py
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_render_all.sh
cd ~/rhythmpress && sed -n '1,220p' src/rhythmpress/scripts/rhythmpress_assemble.sh
cd ~/rhythmpress && sed -n '1,320p' src/rhythmpress/scripts/rhythmpress_finalize.py
```

Scope note:

- This pass maps command contracts from the inspected command wrappers and previously confirmed generated artifacts.
- Detailed internals of helper functions in `src/rhythmpress/rhythmpress.py` were not inspected in this pass.

Command dependency table:

| Command | Required inputs | Outputs | External tools/env | Template implication |
|---|---|---|---|---|
| `rhythmpress build` | `_rhythmpress.conf`; each listed article directory; article `master-<lang>.qmd` or `master-<lang>.md`; article `.article_dir` unless `--skip-clean` | Runs clean/preproc across targets; downstream generated sidebar/profile/language-switcher artifacts according to the build pipeline | `rhythmpress` executable; optional `LANG_ID`; current working directory or `--chdir` must be project root | Generated project must include `_rhythmpress.conf` and at least one valid article target |
| `rhythmpress preproc_clean` | target article directory; project root marker `.git` or `_quarto.yml`; `.article_dir` sentinel | Deletes generated article outputs; optionally purges `_sidebar-*.yml` and `_sidebar-*.generated.*` in the target directory | destructive unless omitted `--apply`; interactive confirmation unless `--force` | Starter articles must include `.article_dir`; article `.gitignore` should protect generated outputs from VCS |
| `rhythmpress preproc` | target article directory; `master-<lang>.qmd` or `.md`; optional `LANG_ID` | Delegates to `preproc_<handler>` selected by front matter | `LANG_ID` controls language selection; subprocess call to `rhythmpress preproc_<handler>` | Starter masters must include unambiguous language files or build must set `LANG_ID` |
| `rhythmpress preproc_copy` | article directory; master files detected by helper layer | `<article>/<lang>/index.qmd`; per-article sidebar YAML through helper layer | Python helper functions in package | Core starter can use `copy` for a minimal one-page article |
| `rhythmpress preproc_split` | article directory; master files with H2 sections | `<article>/<slug>/<lang>/index.qmd`; language article index; per-article sidebar YAML through helper layer | Python helper functions in package | Split mode is needed to prove documentation-style generation and sidebar contribution |
| `rhythmpress sidebar-confs` | `_rhythmpress.conf`; per-article `_sidebar-<lang>.yml` files | `_sidebar-<lang>.generated.conf` | None beyond Python stdlib | Generated project must include per-language `_sidebar-<lang>.before.yml` and `_sidebar-<lang>.after.yml` source files if sidebars are expected |
| `rhythmpress render-sidebar` | `_sidebar-<lang>.generated.conf` or supplied conf; YAML files listed inside it | `_sidebar-<lang>.generated.yml`; `_quarto-<lang>.yml`; `_sidebar-<lang>.generated.md` | `RHYTHMPRESS_ROOT`; `yq` v4; `python3`; `rhythmpress quarto-profile`; `rhythmpress render_toc`; optional hook file | Generator should document `eval "$(rhythmpress eval)"` or equivalent environment setup before sidebar rendering |
| `rhythmpress quarto-profile` | `_quarto.yml`; `_metadata-<lang>.yml`; `_sidebar-<lang>.generated.yml` | `_quarto-<lang>.yml` with generated-file notice | PyYAML; language registry; package merge helper | Template must create base config and metadata, but never create `_quarto-<lang>.yml` |
| `rhythmpress render_toc` | sidebar conf; sidebar YAML contents; referenced `.qmd`/`.md` files for title extraction | Markdown TOC to stdout, normally redirected into `_sidebar-<lang>.generated.md` | `RHYTHMPRESS_ROOT` unless `--root`; optional `ruamel.yaml`; optional PyYAML | Generated article pages must exist before TOC generation can resolve titles cleanly |
| `rhythmpress render-lang-switcher-js` | `_rhythmpress.conf`; current language hint | `lang-switcher.generated.mjs` or specified JS output | Python package runtime language switcher helpers | Language switcher JS is generated; root config and language home pages must provide enough runtime routing data |
| `rhythmpress render-all` | generated `_quarto-*.yml` profiles | `.site-<lang>` directories through `rhythmpress render --profile <lang>` | shell; `rhythmpress render`; Quarto through render command | `project create` verification must run build/profile generation before `render-all` |
| `rhythmpress assemble` | `.site-*` directories or explicit source dirs | merged `.site` by default | `rsync`; shell; deletes/recreates output dir | Generated project `.gitignore` must ignore `.site` and `.site-*` |
| `rhythmpress finalize` | rendered final output dir; optional site URL | sitemap and social-card artifacts unless skipped | `rhythmpress sitemap`; `rhythmpress render-social-cards`; `QUARTO_PROJECT_OUTPUT_DIR`; `SITE_URL`; `RHYTHMPRESS_SITE_URL`; Playwright/browser only if social cards enabled | Minimal verification can use `--skip-social-cards`; generator needs `site-url` parameter for production |

Command order implied by lifecycle:

```text
_rhythmpress.conf
  -> build target loop
     -> preproc_clean
     -> preproc
        -> preproc_copy or preproc_split
           -> generated article pages
           -> per-article _sidebar-<lang>.yml
  -> sidebar-confs
     -> _sidebar-<lang>.generated.conf
  -> render-sidebar
     -> _sidebar-<lang>.generated.yml
     -> quarto-profile
        -> _quarto-<lang>.yml
     -> render_toc
        -> _sidebar-<lang>.generated.md
  -> render-lang-switcher-js
     -> lang-switcher.generated.mjs
  -> render-all
     -> .site-<lang>
  -> assemble
     -> .site
  -> finalize
     -> sitemap and optional social-card artifacts
```

External dependencies:

- Required for normal lifecycle:
  - `rhythmpress`
  - Python 3
  - PyYAML
  - Quarto CLI through `rhythmpress render`
  - Git for date injection in preprocessing paths
  - `yq` v4 for sidebar YAML merging
  - `rsync` for `assemble`
- Optional or feature-dependent:
  - `ruamel.yaml` for better TOC warnings
  - Playwright/browser for social-card rendering
  - LilyPond if LilyPond filter examples are included and rendered

Environment dependencies:

- `LANG_ID`:
  - Forces `preproc` to select one `master-<lang>.*`.
  - `build` sets it per detected language when multiple masters exist.
- `RHYTHMPRESS_ROOT`:
  - Required by `render-sidebar`.
  - Used by `render_toc` unless `--root` is supplied.
  - Created by `eval "$(rhythmpress eval)"`.
- `QUARTO_PROJECT_OUTPUT_DIR`:
  - Set by `finalize` for downstream final artifact commands.
- `SITE_URL` and `RHYTHMPRESS_SITE_URL`:
  - Set by `finalize --site-url`.

Template engine requirements from Pass 2:

- Generate a project root that command wrappers can recognize through `_quarto.yml`.
- Generate `_rhythmpress.conf` with at least one article target.
- Generate article directories with `.article_dir`, `.gitignore`, and `master-<lang>.qmd`.
- Generate one `_metadata-<lang>.yml` per requested language.
- Generate `_sidebar-<lang>.before.yml` and `_sidebar-<lang>.after.yml` per requested language.
- Generate root `.gitignore` patterns for `_quarto-*.yml`, `_sidebar-*.generated.*`, `lang-switcher.generated.mjs`, `.quarto`, `.site`, and `.site-*`.
- Keep generated files out of template source and out of VCS by default.
- Include a verification path that runs at least:
  - `rhythmpress build --skip-clean`
  - `rhythmpress render-all`
  - `rhythmpress assemble`
  - `rhythmpress finalize --output-dir .site --skip-social-cards`

Risks affecting `project create`:

- `preproc_clean` refuses to operate without `.article_dir`; missing sentinels break normal build unless users use `--skip-clean`.
- `preproc` fails when multiple masters exist and `LANG_ID` is not set, but `build` mitigates this by building detected languages one by one.
- `render-sidebar` fails if `RHYTHMPRESS_ROOT` is unset or `yq` is missing.
- `quarto-profile` fails if `_metadata-<lang>.yml` or `_sidebar-<lang>.generated.yml` is missing.
- `render-all` fails if no `_quarto-*.yml` profiles have been generated.
- `assemble` fails if `rsync` is missing or no `.site-*` source directories exist.
- `finalize` fails if the output directory does not exist or if all final steps are skipped.
- A brand-new generated project may still fail preprocessing if Git-date injection requires committed files; this remains Pass 3.

### Implementation Risks

#### 20260505-164856 Pass 3: Empty-Project Build Problem

Inspection commands used:

```sh
cd ~/rhythmpress && rg -n "git|cdate|mdate|created|modified|preproc|date" src/rhythmpress docs README.md
cd ~/rhythmpress && sed -n '1,360p' src/rhythmpress/git_dates.py
cd ~/rhythmpress && sed -n '1,620p' src/rhythmpress/rhythmpress.py
cd ~/rhythmpress && sed -n '1,260p' src/rhythmpress/scripts/rhythmpress_create_page.py
cd ~/rhythmpress && sed -n '1,220p' docs/troubleshooting.md
cd ~/rhythmdo-com && sed -n '1,120p' about/.gitignore
cd ~/rhythmdo-com && sed -n '1,120p' offbeat-count/.gitignore
cd ~/rhythmdo-com && sed -n '1,140p' 404.qmd
cd ~/rhythmdo-com && sed -n '1,140p' en/404.qmd
cd ~/rhythmdo-com && sed -n '1,140p' ja/404.qmd
```

Current Git-date behavior:

- `src/rhythmpress/git_dates.py` is strict.
- `get_git_dates(path)` calls:
  - `git_first_commit_date(path)` for `cdate`
  - `git_last_commit_iso(path)` for `mdate`
- Git root discovery uses `git rev-parse --show-toplevel`.
- Files must exist, be tracked by `git ls-files --error-unmatch`, and have `git log --follow` history.
- If a master is outside Git, untracked, or has no commit history, preprocessing raises `GitDatesError`.
- `docs/troubleshooting.md` explicitly documents that brand-new masters fail until committed.

Observed create-page behavior:

- `rhythmpress create-page` creates:
  - `.article_dir`
  - `.gitignore`
  - `master-<lang>.qmd`
- The starter master includes a current `date:` field, but current preprocessing still uses Git history for generated `cdate` and `mdate`.
- Therefore, `create-page` output alone is not enough to guarantee successful preprocessing before the master is committed.

Empty generated project problem:

- A new `project create` command that only writes files will produce untracked starter masters.
- Under current behavior, `rhythmpress build` or `rhythmpress preproc` can fail on those masters because Git dates are unavailable.
- This conflicts with the goal that a generated starter project should run the standard lifecycle without extra framework wiring.

Policy options evaluated:

- Initialize Git and create an initial commit:
  - Pro: preserves current strict Git-date semantics.
  - Con: invasive; depends on Git user identity unless overridden; surprising because a generator would create repository history.
- Add a global `--no-git-dates` mode:
  - Pro: straightforward escape hatch.
  - Con: risks bifurcating output behavior and weakens date semantics unless narrowly scoped.
- Add fallback dates for uncommitted starter masters:
  - Pro: lets generated projects build immediately; avoids automatic commits.
  - Con: requires code changes and a clear opt-in policy to avoid changing existing project behavior unexpectedly.
- Document that first commit is required:
  - Pro: no code change.
  - Con: generated project is not immediately lifecycle-runnable; poor fit for `project create`.

Chosen policy for implementation planning:

- Do not auto-create Git commits by default.
- Preserve strict Git-date behavior for existing projects unless an explicit fallback policy is enabled.
- Add a future opt-in fallback date policy for generated starter projects.
- The fallback should prefer authored front matter date fields when Git dates are unavailable, then use a deterministic generator-provided timestamp if needed.
- `project create` should emit starter masters with explicit creation metadata and configure or invoke the fallback policy so the starter project can build before the first user commit.
- Documentation should still recommend committing generated starter files promptly, because Git history remains the canonical long-term source for `cdate` and `mdate`.

Proposed fallback contract:

- Default existing behavior:
  - Git dates are canonical and strict.
- Generated-project starter behavior:
  - If Git dates resolve, use them.
  - If Git dates fail because the file is untracked or has no commits, use starter front matter/generator timestamp.
  - Emit a visible warning so users know the output is using fallback dates.
  - After the first commit, Git dates take over automatically.

404 classification resolved:

- `404.qmd` is authored source.
- It is a root runtime 404 page and calls `rhythmpress.create_runtime_404_entry`.
- `en/404.qmd` and `ja/404.qmd` are authored language-specific 404 pages.
- 404 pages are not required for the minimum preprocessing/sidebar/profile lifecycle, but they are a recommended core-site feature or small optional `--with-404` feature.

Article `.gitignore` classification resolved:

- `about/.gitignore` and `offbeat-count/.gitignore` have the same pattern:

```gitignore
*
!*/
*/*
!attachments/
!attachments-src/
_quarto.index*
!master-*
```

- This is authored source and should be generated for starter article directories.
- The intent is to track masters while ignoring generated article output.
- Before implementation, tighten or test the attachment rules, because `!attachments/` may not be sufficient to unignore nested attachment files after `*/*`.

Pass 3 implications:

- The generator cannot be considered complete if users must discover Git-date failure by running `build`.
- Pass 4 should define a source skeleton that includes starter date metadata and article ignore files.
- Pass 8 verification must include a brand-new uncommitted fixture case once implementation exists.
- Until fallback policy is implemented, the documented workaround is:
  - generate project
  - `git init`
  - `git add`
  - initial commit
  - run lifecycle

### Verification Results

- Pending.
