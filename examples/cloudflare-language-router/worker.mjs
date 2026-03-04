/**
 * Cloudflare Worker: root language router
 *
 * Behavior:
 * - Intercepts only "/" and "/index.html" on GET/HEAD.
 * - Chooses target language with precedence:
 *   1) cookie (rhythmpress_lang, then lang)
 *   2) Accept-Language header
 *   3) DEFAULT_LANG
 * - Redirects to "/<lang>/" (or route from LANG_ROUTE_MAP).
 * - Passes through all other requests.
 */

function parseCookieHeader(raw) {
  const out = Object.create(null);
  if (!raw) return out;
  const parts = raw.split(";");
  for (const part of parts) {
    const idx = part.indexOf("=");
    if (idx <= 0) continue;
    const key = part.slice(0, idx).trim();
    const value = part.slice(idx + 1).trim();
    if (!key) continue;
    out[key] = decodeURIComponent(value);
  }
  return out;
}

function parseAcceptLanguage(header) {
  if (!header) return [];
  return header
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean)
    .map((x) => {
      const m = x.match(/^([A-Za-z0-9-]+)(?:;q=([0-9.]+))?$/);
      if (!m) return null;
      const tag = m[1].toLowerCase();
      const q = m[2] ? Number(m[2]) : 1;
      return Number.isFinite(q) ? { tag, q } : null;
    })
    .filter(Boolean)
    .sort((a, b) => b.q - a.q)
    .map((x) => x.tag);
}

function canonicalize(tag, available) {
  if (!tag) return null;
  const t = String(tag).trim().toLowerCase();
  if (!t) return null;
  if (available.has(t)) return t;
  const base = t.split("-")[0];
  if (available.has(base)) return base;
  return null;
}

function parseRouteMap(raw) {
  if (!raw) return Object.create(null);
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return Object.create(null);
    const out = Object.create(null);
    for (const [k, v] of Object.entries(parsed)) {
      if (typeof v !== "string") continue;
      const lang = String(k).trim().toLowerCase();
      if (!lang) continue;
      let path = v.trim();
      if (!path.startsWith("/")) path = "/" + path;
      if (!path.endsWith("/")) path += "/";
      out[lang] = path;
    }
    return out;
  } catch {
    return Object.create(null);
  }
}

function noStoreRedirect(url) {
  return new Response(null, {
    status: 302,
    headers: {
      Location: url,
      "Cache-Control": "no-store",
      Vary: "Cookie, Accept-Language",
    },
  });
}

export default {
  async fetch(request, env) {
    const method = request.method.toUpperCase();
    if (method !== "GET" && method !== "HEAD") {
      return fetch(request);
    }

    const url = new URL(request.url);
    if (!(url.pathname === "/" || url.pathname === "/index.html")) {
      return fetch(request);
    }

    const langIds = String(env.LANG_IDS || "en,ja")
      .split(",")
      .map((x) => x.trim().toLowerCase())
      .filter(Boolean);
    const available = new Set(langIds);
    if (available.size === 0) {
      return fetch(request);
    }

    let defaultLang = String(env.DEFAULT_LANG || "").trim().toLowerCase();
    if (!available.has(defaultLang)) {
      defaultLang = langIds[0];
    }

    const routeMap = parseRouteMap(env.LANG_ROUTE_MAP);
    const routeFor = (lang) => routeMap[lang] || `/${lang}/`;

    const cookies = parseCookieHeader(request.headers.get("Cookie"));
    const cookieCandidate = canonicalize(
      cookies.rhythmpress_lang || cookies.lang || "",
      available
    );

    let preferred = cookieCandidate;
    if (!preferred) {
      const langs = parseAcceptLanguage(request.headers.get("Accept-Language"));
      for (const tag of langs) {
        const c = canonicalize(tag, available);
        if (c) {
          preferred = c;
          break;
        }
      }
    }
    if (!preferred) preferred = defaultLang;

    const targetPath = routeFor(preferred);
    const absoluteTarget = new URL(targetPath, url.origin).toString();

    return noStoreRedirect(absoluteTarget);
  },
};
