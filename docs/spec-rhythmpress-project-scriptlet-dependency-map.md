# Rhythmpress Project Scriptlet Dependency Map

Created: 20260506-142202

Status: evidence specification.

## Purpose

Record the dependency map recovered from the current `rhythmdo-com` scriptlets so `rhythmpress project create` does not copy accumulated CSS, JavaScript, filters, and hooks as an undifferentiated bundle.

This document is the evidence output of the scriptlet audit. The companion design document is [Plugin Feature Packs](spec-rhythmpress-project-plugin-feature-packs.md).

## Audit Scope

Read-only audit inputs:

- `~/rhythmdo-com/_quarto.yml`
- `~/rhythmdo-com/_metadata-en.yml`
- `~/rhythmdo-com/_metadata-ja.yml`
- `~/rhythmdo-com/filters/`
- `~/rhythmdo-com/assets/`
- `~/rhythmdo-com/.assets/`
- `~/rhythmdo-com/.project-lilypond/`, formerly `~/rhythmdo-com/common-ly/`
- `~/rhythmdo-com/templates/`
- selected authored QMD and `master-*` content references
- `~/rhythmdo-com/_rhythmpress.hook-after.*.py`
- existing generated-file and ignore-pattern evidence

Important scope correction: `.assets/websites/*.scss` is part of the current scriptlet/theme surface. `rhythmdo-com` README documents copying `.assets/` beside `filters/` and `assets/`, and both `_metadata-*.yml` files reference `.assets/websites/theme*.scss`.

## High-Signal Evidence

- `_quarto.yml` globally loads `filters/meta-dates.lua`, `filters/include-files.lua`, `filters/lilypond.lua`, and `filters/remove-softbreaks.lua`.
- `_quarto.yml` contains a disabled `filters/obsidian-image-dimensions.lua` entry.
- `_quarto.yml` globally injects Twitter/X, language switcher, Groovespace, TOC, Cookiebot, AdSense, and Cookiebot settings scripts.
- `_metadata-en.yml` and `_metadata-ja.yml` load `.assets/websites/theme.scss`, `.assets/websites/theme-light.scss`, `.assets/websites/theme-dark.scss`, and `assets/styles.css`.
- Active `offbeat-count` masters contain 112 `.lilypond-file` blocks and 10 inline `.lilypond` blocks.
- Active index/offbeat content contains 102 `ats4u-twitter-video` markers.
- Active offbeat masters contain 32 Groovespace perspective/table markers.
- `dojo/master-ja.md` imports `/assets/dojo.css` 5 times.
- Authored source contains 6 `cdate:` and 6 `mdate:` entries.
- No authored include-block use was found, except a draft command line mentioning `--shift-heading-level-by`.
- No Obsidian image dimension syntax was found.
- TOC runtime targets are currently commented out in active masters; `toc-ul.mjs` is still loaded globally and is the right basis for a visible starter-project helper.
- `toc-generator.mjs` is a console-oriented developer aid and should not be installed as-is by default.
- Existing `.gitignore` excludes many generated files but not `lilypond-out/`.

## Dependency Table

| File or Surface | Referenced From | Requires | Produces or Mutates | Solves | Generic? | Candidate | Default | Migrate |
|---|---|---|---|---|---|---|---|---|
| `lang-switcher.generated.mjs` reference | `_quarto.yml` header include; `website.navbar` slot | `rhythmpress build` or `render-lang-switcher-js`; `_rhythmpress.conf`; multilingual routes | Generated runtime JS; browser DOM; `localStorage` and cookie preference | Language switching and root-route preference persistence | Yes | `language-switcher` | auto when multi-lang | yes, as core multilingual pack; generated JS remains excluded |
| `filters/meta-dates.lua` | `_quarto.yml` filter list; pages with `cdate`/`mdate` | Pandoc Lua filter runtime | Adds HTML header metadata for created/modified dates | Social/search metadata from explicit front matter dates | Yes | `filter-meta-dates` | opt-in | yes |
| `filters/include-files.lua` | `_quarto.yml` filter list | Pandoc 2.12+; `pandoc.path`; `pandoc.system`; include code blocks | Transcludes Markdown files; rewrites relative images and include paths | Source-level Markdown include composition | Yes, but unused here | `filter-include-files` | off | later only |
| `filters/lilypond.lua` | `_quarto.yml` filter list; `.lilypond` and `.lilypond-file` blocks | `lilypond`; `RHYTHMPRESS_ROOT` or `QUARTO_PROJECT_DIR`; `realpath`; `.project-lilypond`; Pandoc SHA1 | Writes `lilypond-out/ly-*.ly` and SVGs; injects image blocks; appends watched resources | Renders music notation from source | Yes, but heavy | `filter-lilypond` | opt-in | yes |
| `.project-lilypond/lilypond-preamble.ly` | `_quarto.yml` `metadata.lilypond-preamble`; LilyPond snippets | `.project-lilypond/chromatic-solfege.ly`; LilyPond include path rooted at project | Preamble content prepended into rendered LilyPond temp files | Shared LilyPond setup | Mixed | `filter-lilypond` | opt-in | yes, minimal generic preamble only |
| `.project-lilypond/shared/*.ly` | `.lilypond-file` blocks | `lilypond-book-preamble.ly` in many files; project-root include path; site-specific musical vocabulary | Rendered notation cache via `lilypond-out/` | Rhythmdo notation examples | Site-specific | content pack, not generic | no | no default migration |
| `filters/remove-softbreaks.lua` | `_quarto.yml` filter list | Pandoc Lua filter runtime | Replaces soft breaks with empty strings | Japanese/manual line wrapping cleanup | Mixed | `filter-remove-softbreaks` | off | yes, opt-in with warning |
| `filters/obsidian-image-dimensions.lua` | Disabled `_quarto.yml` entry | Pandoc Lua filter runtime; Obsidian-style caption syntax | Mutates image width/height; prints debug output | Obsidian image dimensions | Generic idea, current file not clean | `filter-obsidian-image-dimensions` | off | no for first implementation |
| `assets/ats4u-twitter-video.mjs` | `_quarto.yml` header include; `.ats4u-twitter-video` content markers | Browser DOM; `window.twttr.widgets.load`; Twitter widgets script | Converts placeholder divs to `blockquote.twitter-tweet` | Stable authoring shorthand for Twitter/X embeds | Generic after rename | `asset-twitter-video` | opt-in | yes, renamed/generalized |
| External Twitter widgets script | `_quarto.yml` header include | Remote `https://platform.twitter.com/widgets.js`; network and privacy implications | Loads embedded tweet renderer | Third-party embed rendering | Generic but external | `asset-twitter-video` | opt-in | yes, declared dependency |
| `assets/cookie-settings.mjs` | `_quarto.yml` header include; footer links with `#cookie-settings` | Cookiebot or IAB TCF API; configured Cookiebot script and ID | Opens consent UI; attaches click handler | Cookie consent settings link | Generic pattern, site config required | `asset-cookie-settings` | opt-in | yes, config-required |
| Cookiebot script block | `_quarto.yml` header include | Remote Cookiebot script; `data-cbid`; policy pages | Creates CMP globals and consent state | Consent management | Config-specific | `asset-cookie-settings` | opt-in | yes, template only |
| AdSense script blocks | `_quarto.yml` header include | Remote Google AdSense; publisher ID; consent mode | Loads ads and marketing script | Monetization | Site-specific/config-specific | `asset-adsense` | off | later only |
| `assets/toc-ul.mjs` | `_quarto.yml` header include; commented `#toc` targets | Browser DOM; headings; starter page `#toc` target | Adds IDs; injects nested TOC into `#toc`; logs HTML | Visible runtime TOC for new projects | Yes after cleanup | `toc-helper` | core default | yes, as cleaned helper |
| `assets/toc-generator.mjs` | No active include; self auto-runs | Browser DOM; console | Logs Markdown and YAML TOC | Developer aid for TOC generation | Dev-only | none | no | no |
| `assets/groovespace.mjs` | `_quarto.yml` header include; `.perspwrap` markers | Browser layout; `.perspinner`; resize/load events | Mutates wrapper height and transforms child table | Perspective table presentation | Domain-specific | `asset-groovespace` | off | no default migration |
| `assets/groovespace.css` | `_quarto.yml` header include; `.divisions`, `.persptable`, `.perspwrap` content | Matching classes from content and `lib/groovespace.py` | Visual table styling | Groovespace visual system | Domain-specific | `asset-groovespace` | off | no default migration |
| `lib/groovespace.py` | Python snippets in masters import it | Python execution in Quarto source cells; matching CSS classes | Emits HTML tables with class names | Groovespace table generation | Domain-specific | `asset-groovespace` | off | no default migration |
| `assets/dojo.css` | `dojo/master-ja.md` imports it | Page-level CSS import; `.rdo-header`; ruby classes | Page-specific layout and typography | Dojo page formatting | Site/content-specific | custom content asset | off | no |
| `assets/styles.css` | `_metadata-*.yml` `format.html.css` | Quarto HTML classes; LilyPond image class; Twitter caption class; content table classes | Global site styling | Mixed catch-all site CSS | Mixed | split across packs | no as-is | split before migration |
| `.assets/websites/theme.scss` | `_metadata-*.yml` theme list | Quarto SCSS pipeline; remote Google Fonts; Rhythmdo logo attachments; Quarto DOM classes | Theme variables and rules; logo replacement; typography; Quarto workarounds | Branded theme and Quarto fixes | Mixed/site-specific | `theme-custom` plus possible core fixes | off | split before migration |
| `.assets/websites/theme-light.scss` | `_metadata-*.yml` theme list | Quarto SCSS pipeline | Empty/default light theme | Light theme placeholder | Generic placeholder | `theme-custom` | off | later |
| `.assets/websites/theme-dark.scss` | `_metadata-*.yml` theme list | Quarto SCSS pipeline; Quarto dark-mode classes | Dark color overrides | Dark theme styling | Generic idea, site choices | `theme-custom` | off | later |
| `templates/*.md` | Authoring templates only | Obsidian/Templater syntax | Creates authoring notes, not Rhythmpress runtime files | Personal authoring workflow | Site/personal | none | no | no |
| `templates/ai-attribution-footer.html` | Duplicates `_quarto.yml` include-after-body content | Rhythmdo branding and canonical URL | Footer attribution block | Site policy text | Site-specific | none | no | no |
| `_rhythmpress.hook-after._sidebar-*.generated.yml.py` | `render-sidebar` hook protocol | Python; PyYAML; generated sidebar YAML filename | Mutates generated sidebar `collapse-level` | Post-merge sidebar override | Generic hook mechanism, site-specific hook body | `sidebar-hook` | off | later |
| `rhythmpress.social-cards` config | `_quarto.yml`; `render-social-cards` implementation | Playwright; browser; rendered output; optional JS/remote; CSS selectors | Screenshots pages; writes social images; patches rendered HTML head | Social cards | Generic | `social-cards` | opt-in | yes, config-only |
| GitHub ribbon HTML | `_quarto.yml` include-after-body | External image URL; fixed position CSS | Adds visible GitHub fork ribbon | Repository promotion | Site-specific | none | no | no |
| Attribution footer HTML | `_quarto.yml` include-after-body; template copy | Rhythmdo URL and policy text | Adds page footer note | Site-specific attribution policy | Site-specific | none | no | no |

## CSS Split Required Before Migration

Current CSS is not separable by file:

- `assets/styles.css` contains content table styles, Twitter caption styles, LilyPond image behavior, iframe sizing, and miscellaneous site CSS.
- `.assets/websites/theme.scss` contains Quarto fixes, logo replacement, external fonts, content typography, navbar/sidebar overrides, and Rhythmdo branding.
- `assets/groovespace.css` is already a coherent domain-specific pack.
- `assets/dojo.css` is already a coherent content-specific pack.

Therefore `project create` must not copy `assets/styles.css` or `.assets/websites/theme.scss` as generic defaults. Feature packs must own smaller CSS fragments.

Minimum CSS ownership split:

| CSS Concern | Owner |
|---|---|
| `img.lilypond` sizing and dark-mode inversion | `filter-lilypond` |
| `.ats4u-twitter-video-caption` after rename | `asset-twitter-video` |
| `table.offbeat-onbeat-table` | Rhythmdo content pack, not generic |
| `.rhythmpedia-iframe` | custom content asset |
| logo replacement and Rhythmdo attachments | site-specific theme |
| Quarto sidebar/nav/font-size fixes | possible future generic theme utility |
| Google Fonts imports | theme pack with explicit external dependency |
| `.divisions`, `.perspwrap`, `.persptable` | `asset-groovespace` |
| `.rdo-header`, inline ruby tweaks in dojo page | custom content asset |

## Generated Artifact Boundary

Never treat these as project template source:

- `_quarto-<lang>.yml`
- `_sidebar-*.generated.conf`
- `_sidebar-*.generated.yml`
- `_sidebar-*.generated.md`
- `lang-switcher.generated.mjs`
- `lang-switcher-ui.generated.mjs`
- `.site`, `.site-*`
- `.quarto`
- `lilypond-out/`
- rendered social-card images under rendered output

The generated language switcher is produced by Rhythmpress commands. The source contract is the `_quarto.yml` script reference plus `_rhythmpress.conf` language route data.

## Migration Decisions

Migrate in first feature-pack design:

- `language-switcher` as core multilingual behavior, with generated JS excluded.
- `toc-helper` as a default core helper, based on cleaned `toc-ul.mjs` behavior and paired with a starter `#toc` target.
- `filter-meta-dates` as opt-in.
- `filter-remove-softbreaks` as opt-in with explicit warning.
- `filter-lilypond` as opt-in, with minimal generic preamble and `lilypond-out/` ignore support.
- `asset-twitter-video` as opt-in, renamed/generalized and dependent on the external Twitter widgets script.
- `asset-cookie-settings` as opt-in, requiring CMP provider config.
- `social-cards` as opt-in config only; rendering remains a final artifact command.

Do not migrate by default:

- `include-files` despite being loaded in `rhythmdo-com`; no active authored include-block dependency was found.
- `obsidian-image-dimensions`; disabled and debug-printing.
- `toc-generator.mjs` as-is; it is console/dev output. Useful logic can be merged into the cleaned TOC helper later.
- Groovespace, Dojo, Rhythmdo branded theme/logo, AdSense, GitHub ribbon, attribution footer, and personal authoring templates.

## Open Risks

- Many `.project-lilypond/shared/*.ly` files include `lilypond-book-preamble.ly`, which was not present in the searched source tree. This may rely on LilyPond include behavior or local environment. The generic LilyPond pack must not assume Rhythmdo's full shared library is portable.
- `remove-softbreaks` is globally active in `rhythmdo-com`, but it can join wrapped English prose. It must remain explicit opt-in.
- Cookiebot and AdSense are legally and operationally sensitive. They require project-specific IDs and should never appear in a default skeleton.
- The hook mechanism is powerful but can hide post-generation mutations. First implementation should keep hooks opt-in and visibly declared.
