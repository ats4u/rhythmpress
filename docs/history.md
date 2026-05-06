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

