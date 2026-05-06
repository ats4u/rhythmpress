# Rhythmpress History

Created: 20260507-004547

## 20260507-004547 Rhythmdo Legacy Rhythmpedia Cleanup

`rhythmdo-com` removed local legacy Rhythmpedia files:

- `lib/rhythmpedia.py`
- `create_toc_v2_specification.md`

These files were removed from `rhythmdo-com` because the active implementation authority now lives in `rhythmpress`, and the local Rhythmdo copies were obsolete project-local remnants.

The TOC template was intentionally not removed from `rhythmdo-com`:

- `lib/templates/toc.markdown`

Reason: `toc.markdown` is still an active Rhythmpress concept. The canonical active copy is:

- `src/rhythmpress/templates/toc.markdown`

The active Rhythmpress code references that template from:

- `src/rhythmpress/rhythmpress.py`

Relevant history anchors:

- `a04c2b31ada2735470438309701518f85ab65b98` in `rhythmpress`: `lib/rhythmpedia.py` existed before the module-layout reorganization.
- `4c0868bb263c1a1922518149f542af3bc7eefe43` in `rhythmpress`: `create_toc_v2_specification.md` existed in history.
- `64037f3f2459bcdbfd8bf3cc847b2ecc85047dfe` in `rhythmpress`: early module-directory history also contains `create_toc_v2_specification.md`.
- `b1539339b6be574164b2191107d48b4bd9081818` in `rhythmdo-com`: removed archived `lib/doc` Rhythmpedia legacy docs after copying them to the Rhythmpress archive.

Classification:

- `rhythmdo-com/lib/rhythmpedia.py`: obsolete local implementation copy.
- `rhythmdo-com/create_toc_v2_specification.md`: obsolete historical specification, recoverable from git history.
- `rhythmdo-com/lib/templates/toc.markdown`: retained local file, not deleted in this cleanup.
- `rhythmpress/src/rhythmpress/templates/toc.markdown`: canonical active Rhythmpress template.

## 20260507-015723 TOC Caption Ownership Clarification

The `toc.markdown` template name made it easy to assume the template owned the whole generated TOC block, including captions such as `目次`.

Verified behavior:

- `rhythmpress/src/rhythmpress/templates/toc.markdown` contains only `$toc$`.
- That template controls the Pandoc-generated TOC body used by `create_toc_v1`.
- It does not inject the generated sidebar caption.
- It does not inject Quarto's right-margin page TOC title.

Caption ownership:

- Rhythmpress writes the generated sidebar Markdown caption, for example `**目次**`, in `rhythmpress render-sidebar`.
- That label is resolved by `resolve_sidebar_toc_label`.
- The Rhythmpress override key is `rhythmpress.toc-label`.
- Quarto writes the right-margin page TOC title, for example `<h2 id="toc-title">目次</h2>`.
- The Quarto override key is `format.html.toc-title`.
