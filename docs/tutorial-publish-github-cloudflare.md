# Publishing a Rhythmpress site with GitHub Pages + Cloudflare Proxy

This tutorial documents the “Rhythmpress + GitHub + Cloudflare” stack where:

* **Rhythmpress** (and Quarto) builds a static site locally or in CI.
* **GitHub Pages** hosts the built static files.
* **Cloudflare** sits in front as a **reverse proxy** (orange-cloud), giving you CDN / caching / WAF / analytics, while GitHub remains the origin.

This is **not** Cloudflare Pages. (Cloudflare Pages is a different hosting product; here you’re using Cloudflare’s proxy in front of GitHub Pages.)

---

## 1. Architecture (mental model)

Request flow:

Browser → **Cloudflare (proxy/CDN)** → **GitHub Pages (origin)** → static HTML/CSS/JS built by Rhythmpress/Quarto

Cloudflare calls a proxied record “**Proxied / orange-cloud**” and lists the benefits (protection, caching, optimization, etc.). ([Cloudflare Docs][1])

---

## 2. Prerequisites

* A GitHub repository containing your Rhythmpress/Quarto site sources.
* Your domain is using Cloudflare DNS (nameservers delegated to Cloudflare).
* Your site can build locally (or you can run the build in GitHub Actions).

---

## 3. Build locally (sanity check)

From your project root:

```bash
# activate venv and load env (your style)
. .venv/bin/activate
eval "$(rhythmpress eval)"

# build / preprocess (whatever your project uses)
rhythmpress build

# render site (typical Quarto)
quarto render
```

You should end up with a static output directory (commonly `_site/` for Quarto).

---

Absolutely — here’s a Section 4 you can paste into `docs/tutorial-publish-github-cloudflare.md` that matches your **real** `rhythmdo-com` workflow exactly (branch, tools, output dir, and the “vendor/rhythmpress” install pattern).

I’m also fixing one important mismatch: your workflow currently has `eval "$(rhythmpress env)"`, but in this codebase it should be `eval "$(rhythmpress eval)"` (or you can omit it entirely because you already set `RHYTHMPRESS_ROOT` explicitly in the job env).

---

## 4. Deploy with GitHub Actions (build with Rhythmpress, render with Quarto, publish to GitHub Pages)

This stack uses GitHub Actions to build the site on every push to the `production` branch, then publishes the generated static files to the `gh-pages` branch. Cloudflare sits in front as a proxy (DNS + CDN + SSL), but the hosting origin is GitHub Pages.

### 4.1 Workflow used by a real Rhythmpress website (example)

The following workflow is used in a production Rhythmpress website repository:

- Example website repo: `ats4u/rhythmdo-com`
- Rhythmpress engine repo (also used as a website itself): `ats4u/rhythmpress`

Create this file in your site repository:

`.github/workflows/deploy.yml`

```yml
name: Build & Deploy Rhythmpedia (rhythmpress)

on:
  push:
    branches: [production]
  pull_request:
    branches: [production]

jobs:
  build:
    runs-on: ubuntu-latest

    env:
      # Point rhythmpress to the site root
      RHYTHMPRESS_ROOT: ${{ github.workspace }}

    steps:
      - name: Checkout site repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0   # full history for per-file git dates

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install system deps (Quarto + yq + LilyPond + pandoc)
        run: |
          sudo apt-get update
          sudo apt-get install -y wget lilypond pandoc

      - name: Set up Quarto
        uses: quarto-dev/quarto-actions/setup@v2
        with:
          version: "1.7.31"

      - name: Install yq
        run: |
          YQ_VERSION=v4.47.1
          sudo wget -q https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64 -O /usr/local/bin/yq
          sudo chmod +x /usr/local/bin/yq
          yq --version

      # -------- rhythmpress: clone + install --------
      - name: Clone rhythmpress
        uses: actions/checkout@v4
        with:
          repository: ats4u/rhythmpress.git
          ref: master
          path: vendor/rhythmpress
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Install rhythmpress (pip install .)
        run: |
          python -m pip install --upgrade pip
          python -m pip install jupyter pyyaml
          pip install ./vendor/rhythmpress

      - name: Show tool versions
        run: |
          python --version
          pip --version
          rhythmpress --help | head -n 20
          quarto --version

      # -------- Build & Render --------
      - name: Build with rhythmpress
        run: |
          # Rhythmpress already has RHYTHMPRESS_ROOT from job env.
          # If you still want the env shim, use: eval "$(rhythmpress eval)"
          rhythmpress build

      - name: Render Quarto project
        env:
          QUARTO_PROJECT_DIR: ${{ github.workspace }}
        run: quarto render

      # -------- Deploy --------
      - name: Deploy to GitHub Pages
        if: github.event_name == 'push'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./.site
          publish_branch: gh-pages
````

### 4.2 Output directory must match

This workflow publishes `./.site` to GitHub Pages, so your Quarto project MUST render into `.site`.

In `_quarto.yml`, set:

```yml
project:
  type: website
  output-dir: .site
```

### 4.3 Why `fetch-depth: 0` matters (important)

Rhythmpress injects `cdate`/`mdate` using Git history. If Actions checks out only a shallow history, those dates may fail or become incorrect. Keeping `fetch-depth: 0` is the simplest reliable solution.

### 4.4 Note about `rhythmpress env` vs `rhythmpress eval`

Some scripts/messages historically used `rhythmpress env`, but in current Rhythmpress the activation command is:

```sh
eval "$(rhythmpress eval)"
```

In this workflow, you already export `RHYTHMPRESS_ROOT` at the job level, so you can safely omit the shim unless you specifically need its PATH/prompt behavior.

---

## 5. Add your custom domain in GitHub Pages settings

In **Settings → Pages → Custom domain**, enter your domain and save.

Two important details from GitHub’s docs:

* If you publish from a **custom GitHub Actions workflow**, GitHub does **not** require a `CNAME` file (and ignores it). ([GitHub Docs][3])
* GitHub notes DNS propagation can take **up to 24 hours**, and the “Enforce HTTPS” option can take time to become available. ([GitHub Docs][4])

---

## 6. Configure Cloudflare DNS for GitHub Pages

GitHub’s official guidance for DNS is:

### Apex domain (`example.com`)

Use either `ALIAS`/`ANAME` (pointing to your GitHub Pages default domain) **or** `A` records to GitHub Pages IPs:

* 185.199.108.153
* 185.199.109.153
* 185.199.110.153
* 185.199.111.153 ([GitHub Docs][4])

### `www` subdomain (`www.example.com`)

Create a **CNAME** pointing to your GitHub Pages default domain (`<user>.github.io`), without the repo name. ([GitHub Docs][4])

GitHub also recommends setting up `www` alongside the apex for HTTPS-friendly setups, and GitHub Pages can handle redirects between apex and `www` when configured correctly. ([GitHub Docs][4])

---

## 7. Cloudflare proxy (orange-cloud) and the HTTPS “gotcha”

Here’s the part that bites people:

When your DNS records are **proxied** (orange-cloud), GitHub sometimes can’t verify the DNS state it expects for issuing/enabling HTTPS for the **custom domain**. This is widely reported by both Cloudflare community and GitHub community discussions. ([Cloudflare Community][5])

A practical, reliable sequence is:

1. In Cloudflare DNS, set the relevant records (**apex** and/or **www**) to **DNS only** (grey cloud) temporarily.
2. In GitHub Pages settings, save the custom domain.
3. Wait until GitHub shows the domain as configured, then enable **Enforce HTTPS** (when it becomes available). GitHub notes this may take time. ([GitHub Docs][4])
4. After HTTPS is working, switch Cloudflare back to **Proxied** (orange-cloud) if you want Cloudflare in front.

Now set Cloudflare SSL/TLS mode:

* If GitHub has successfully issued HTTPS for your custom domain, you can use **Full (strict)**. Cloudflare defines Full (strict) as encrypting to origin and validating the origin cert. ([Cloudflare Docs][6])
* If GitHub **has not** issued a valid cert for the custom domain (but you still want Cloudflare proxy), you may need **Full** (not strict). Cloudflare’s Full mode encrypts to origin but does not require a publicly trusted/valid cert in the same way. ([Cloudflare Docs][7])

I’d treat **Full (strict)** as the “clean” target when possible, and use **Full** as the fallback when certificate validation becomes the blocker.

---

## 8. Verification (quick checks)

GitHub suggests verifying DNS with `dig`. For apex A records:

```bash
dig example.com +noall +answer -t A
```

You should see the GitHub Pages IPs. ([GitHub Docs][4])

Once Cloudflare proxy is enabled, your DNS answers will typically be Cloudflare edges (that’s expected), so for origin correctness you’ll rely more on “does the site load correctly” and GitHub Pages’ domain status.

---

## 9. Example: a Rhythmpress-based website repo

You asked to use the Rhythmpress repository itself as an example of a Rhythmpress website in this stack:

* Rhythmpress repo (example content + docs layout):
  [https://github.com/ats4u/rhythmpress/](https://github.com/ats4u/rhythmpress/)

And your “real” production site repo in the same general stack family (Rhythmpress build + GitHub hosting + Cloudflare proxy in front):

* rhythmdo-com:
  [https://github.com/ats4u/rhythmdo-com](https://github.com/ats4u/rhythmdo-com)


[1]: https://developers.cloudflare.com/dns/proxy-status/?utm_source=chatgpt.com "Proxy status · Cloudflare DNS docs"
[2]: https://github.com/actions/deploy-pages?utm_source=chatgpt.com "actions/deploy-pages"
[3]: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages "Troubleshooting custom domains and GitHub Pages - GitHub Docs"
[4]: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site "Managing a custom domain for your GitHub Pages site - GitHub Docs"
[5]: https://community.cloudflare.com/t/github-pages-require-disabling-cfs-http-proxy/147401?utm_source=chatgpt.com "GitHub Pages require disabling CF's HTTP Proxy"
[6]: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/?utm_source=chatgpt.com "Full (strict) - SSL/TLS encryption modes"
[7]: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full/?utm_source=chatgpt.com "Full - SSL/TLS encryption modes"

