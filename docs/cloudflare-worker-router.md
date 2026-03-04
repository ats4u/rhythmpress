# Cloudflare Worker Language Router

This example adds edge-side language routing for the root entry:

- Intercept `/` and `/index.html`
- Choose language by:
  - cookie (`rhythmpress_lang`, then `lang`)
  - `Accept-Language`
  - default language
- Redirect to language root (`/en/`, `/ja/`, ...)

Use files in:

- `examples/cloudflare-language-router/worker.mjs`
- `examples/cloudflare-language-router/wrangler.toml`

## Why use this

- Deterministic root routing before HTML is served.
- Good for SEO/crawl consistency at root.
- Works even if client-side JS is blocked.

## Quick start

1. Copy the example directory into your deployment repo (or use it in place).
2. Edit `wrangler.toml`:
   - set `name`
   - set `routes` for your zone
   - set `LANG_IDS`, `DEFAULT_LANG`
   - optional: `LANG_ROUTE_MAP`
3. Deploy:

```bash
wrangler deploy
```

## Config variables

- `LANG_IDS`: comma list, example: `en,ja,fr`
- `DEFAULT_LANG`: fallback language, example: `en`
- `LANG_ROUTE_MAP`: optional JSON object for custom paths
  - example: `{"en":"/en/","ja":"/ja/"}`
  - when omitted, fallback route is `/<lang>/`

## Notes

- Redirect response uses `302` with:
  - `Cache-Control: no-store`
  - `Vary: Cookie, Accept-Language`
- Only root paths are rewritten. All other requests are passed through.

