#!/usr/bin/env python3
from __future__ import annotations

from pathlib import PurePosixPath

from rhythmpress.scripts import rhythmpress_render_social_cards as social


def main() -> int:
    root = PurePosixPath("index.html")
    nested = PurePosixPath("contact/en/index.html")
    plain = PurePosixPath("robots.html")

    ns = social.parse_args([])
    default_options = social.resolve_social_card_options(ns, {})
    if default_options.render_mode != "mobile-page":
        raise AssertionError("mobile-page should be the default social-card render mode")
    if default_options.viewport != "800x600":
        raise AssertionError("800x600 should be the default mobile viewport")
    if default_options.allow_remote:
        raise AssertionError("remote requests should be blocked by default")
    if default_options.enable_javascript:
        raise AssertionError("JavaScript should be disabled by default")
    if default_options.wait_ms != 0:
        raise AssertionError("post-load wait should default to zero")
    remote_options = social.resolve_social_card_options(
        social.parse_args(["--allow-remote"]),
        {"rhythmpress": {"social-cards": {"allow-remote": False}}},
    )
    if not remote_options.allow_remote:
        raise AssertionError("--allow-remote should opt in to remote requests")
    blocked_options = social.resolve_social_card_options(
        social.parse_args(["--no-allow-remote"]),
        {"rhythmpress": {"social-cards": {"allow-remote": True}}},
    )
    if blocked_options.allow_remote:
        raise AssertionError("--no-allow-remote should override config")
    javascript_options = social.resolve_social_card_options(
        social.parse_args(["--enable-javascript"]),
        {"rhythmpress": {"social-cards": {"enable-javascript": False}}},
    )
    if not javascript_options.enable_javascript:
        raise AssertionError("--enable-javascript should opt in to page JavaScript")
    no_javascript_options = social.resolve_social_card_options(
        social.parse_args(["--disable-javascript"]),
        {"rhythmpress": {"social-cards": {"enable-javascript": True}}},
    )
    if no_javascript_options.enable_javascript:
        raise AssertionError("--disable-javascript should override config")
    css_ns = social.parse_args(
        [
            "--css",
            "main { margin-top: 0 !important; }",
            "--css",
            "@media screen { body { background: white; } }",
        ]
    )
    if len(css_ns.css) != 2:
        raise AssertionError("--css should be repeatable")
    config_options = social.resolve_social_card_options(
        social.parse_args([]),
        {
            "rhythmpress": {
                "social-cards": {
                    "allow-remote": True,
                    "browser-executable": "/tmp/chrome",
                    "css": ["main { margin-top: 0 !important; }"],
                    "default-hide-selectors": False,
                    "enable-javascript": True,
                    "hide-selector": [".config-hide"],
                    "crop-selector": ["main.content"],
                    "render-mode": "template",
                    "screenshot-size": "1280x630",
                    "viewport": "640x600",
                    "wait-ms": 1200,
                }
            }
        },
    )
    if not config_options.allow_remote:
        raise AssertionError("config should enable remote access")
    if config_options.browser_executable != "/tmp/chrome":
        raise AssertionError("config should set browser executable")
    if config_options.css != ["main { margin-top: 0 !important; }"]:
        raise AssertionError("config should set CSS overrides")
    if config_options.default_hide_selectors:
        raise AssertionError("config should disable default hide selectors")
    if not config_options.enable_javascript:
        raise AssertionError("config should enable JavaScript")
    if config_options.hide_selector != [".config-hide"]:
        raise AssertionError("config should set hide selectors")
    if config_options.crop_selector != ["main.content"]:
        raise AssertionError("config should set crop selector fallback order")
    if config_options.render_mode != "template":
        raise AssertionError("config should set render mode")
    if config_options.screenshot_size != "1280x630":
        raise AssertionError("config should set screenshot size")
    if config_options.viewport != "640x600":
        raise AssertionError("config should set viewport")
    if config_options.wait_ms != 1200:
        raise AssertionError("config should set post-load wait")
    override_options = social.resolve_social_card_options(
        social.parse_args(
            [
                "--css",
                "body { color: black; }",
                "--crop-selector",
                "article",
                "--default-hide-selectors",
                "--hide-selector",
                ".cli-hide",
                "--render-mode",
                "mobile-page",
                "--screenshot-size",
                "1200x630",
                "--viewport",
                "800x600",
                "--wait-ms",
                "250",
            ]
        ),
        {
            "rhythmpress": {
                "social-cards": {
                    "css": ["main { margin-top: 0 !important; }"],
                    "default-hide-selectors": False,
                    "hide-selector": [".config-hide"],
                    "crop-selector": ["main.content"],
                    "render-mode": "template",
                    "screenshot-size": "1280x630",
                    "viewport": "640x600",
                    "wait-ms": 1200,
                }
            }
        },
    )
    if override_options.css != [
        "main { margin-top: 0 !important; }",
        "body { color: black; }",
    ]:
        raise AssertionError("CLI CSS should be appended after config CSS")
    if override_options.hide_selector != [".config-hide", ".cli-hide"]:
        raise AssertionError("CLI hide selectors should be appended after config selectors")
    if override_options.crop_selector != ["article"]:
        raise AssertionError("CLI crop selectors should replace config crop selectors")
    if not override_options.default_hide_selectors:
        raise AssertionError("CLI should override config default hide selector setting")
    if override_options.render_mode != "mobile-page":
        raise AssertionError("CLI should override config render mode")
    if override_options.screenshot_size != "1200x630":
        raise AssertionError("CLI should override config screenshot size")
    if override_options.viewport != "800x600":
        raise AssertionError("CLI should override config viewport")
    if override_options.wait_ms != 250:
        raise AssertionError("CLI should override config post-load wait")
    if social.parse_size("800x600", label="test") != (800, 600):
        raise AssertionError("size parser should accept WIDTHxHEIGHT values")
    if social.mobile_device_scale_factor((800, 600), (1200, 630)) != 1.5:
        raise AssertionError("mobile device scale should derive from output width and viewport width")

    default_crop = social.resolve_crop_selectors([])
    if default_crop[0] != "main#quarto-document-content":
        raise AssertionError("default crop selectors should prefer article content")
    explicit_crop = social.resolve_crop_selectors([" main.content ", "#fallback"])
    if explicit_crop != ["main.content", "#fallback"]:
        raise AssertionError("repeated crop selectors should preserve fallback order")
    comma_crop = social.resolve_crop_selectors(["main#primary, main.content"])
    if comma_crop != ["main#primary, main.content"]:
        raise AssertionError("commas in crop selectors should remain CSS selector-group syntax")

    selectors = social.resolve_hide_selectors([".extra"], use_defaults=True)
    if ".navbar" not in selectors or ".extra" not in selectors:
        raise AssertionError("hide selector resolution should combine defaults and extras")
    comma_selectors = social.resolve_hide_selectors(
        ["#id1, #id2, .class1, .class2", "  "],
        use_defaults=False,
    )
    if comma_selectors != ["#id1, #id2, .class1, .class2"]:
        raise AssertionError("comma-separated selector lists should be preserved")
    descendant_selector = social.resolve_hide_selectors(
        ["#id1 #id2 .class1 .class2"],
        use_defaults=False,
    )
    if descendant_selector != ["#id1 #id2 .class1 .class2"]:
        raise AssertionError("whitespace should remain part of CSS selector syntax")
    hide_css = social.build_hide_css(selectors)
    if ".navbar" not in hide_css or "display: none" not in hide_css:
        raise AssertionError("hide CSS should hide selected page chrome")
    comma_css = social.build_hide_css(comma_selectors)
    if "#id1, #id2, .class1, .class2" not in comma_css:
        raise AssertionError("hide CSS should preserve comma-separated selector lists")
    css_overrides = social.resolve_css_overrides(
        [
            " main { margin-top: 0 !important; } ",
            "  ",
            "@media screen { body { color: black; } }",
        ]
    )
    if css_overrides != [
        "main { margin-top: 0 !important; }",
        "@media screen { body { color: black; } }",
    ]:
        raise AssertionError("CSS overrides should trim blanks and preserve raw CSS blocks")
    screenshot_css = social.build_screenshot_css([".hidden"], css_overrides)
    if screenshot_css.index(".hidden") > screenshot_css.index("main { margin-top"):
        raise AssertionError("CSS overrides should be injected after generated hide rules")
    if "@media screen" not in screenshot_css:
        raise AssertionError("CSS overrides should preserve full raw CSS syntax")
    if "rhythmpress-social-card-hide-css" not in social._INJECT_HIDE_CSS_JS:
        raise AssertionError("hide CSS injection should use the managed style element")
    if "querySelectorAll" not in social._VALIDATE_SELECTORS_JS:
        raise AssertionError("hide selector validation should use browser CSS parsing")

    if social.social_image_rel_path(root) != PurePosixPath("attachments/social/index.png"):
        raise AssertionError("root social image path mapping changed unexpectedly")
    if social.social_image_rel_path(nested) != PurePosixPath(
        "attachments/social/contact/en/index.png"
    ):
        raise AssertionError("nested social image path mapping changed unexpectedly")
    if social.social_image_rel_path(plain) != PurePosixPath("attachments/social/robots.png"):
        raise AssertionError("plain html file path mapping changed unexpectedly")

    if social.local_http_page_url("http://127.0.0.1:1234/", nested) != (
        "http://127.0.0.1:1234/contact/en/index.html"
    ):
        raise AssertionError("local HTTP page URL mapping changed unexpectedly")
    spaced = PurePosixPath("folder with space/index.html")
    if social.local_http_page_url("http://127.0.0.1:1234", spaced) != (
        "http://127.0.0.1:1234/folder%20with%20space/index.html"
    ):
        raise AssertionError("local HTTP page URL should quote unsafe path characters")
    if not social._is_local_http_url("http://127.0.0.1:1234/index.html"):
        raise AssertionError("localhost HTTP should be treated as local")
    if not social._is_local_http_url("http://localhost:1234/index.html"):
        raise AssertionError("localhost hostname should be treated as local")
    if social._is_local_http_url("https://example.com/index.html"):
        raise AssertionError("external HTTP should not be treated as local")

    if social.page_url("https://example.com/", root) != "https://example.com/":
        raise AssertionError("root page url mapping changed unexpectedly")
    if social.page_url("https://example.com/", nested) != "https://example.com/contact/en/":
        raise AssertionError("nested index page url mapping changed unexpectedly")
    if social.page_url("https://example.com/", plain) != "https://example.com/robots.html":
        raise AssertionError("plain html page url mapping changed unexpectedly")

    meta_block = social.build_social_meta_block(
        title="Contact",
        description="A short rendered opening excerpt.",
        page_url_value="https://example.com/contact/en/",
        image_url_value="https://example.com/attachments/social/contact/en/index.png",
        site_name="Rhythmdo",
    )
    if 'property="og:image"' not in meta_block:
        raise AssertionError("meta block should include og:image")
    if 'name="twitter:card"' not in meta_block:
        raise AssertionError("meta block should include twitter:card")

    html_text = "<html><head><title>Example</title></head><body>Hello</body></html>"
    patched = social.upsert_social_meta_block(html_text, meta_block)
    if social.SOCIAL_MARKER_BEGIN not in patched:
        raise AssertionError("meta block should be inserted into the document head")
    if patched.count(social.SOCIAL_MARKER_BEGIN) != 1:
        raise AssertionError("meta block should be inserted exactly once")

    replaced = social.upsert_social_meta_block(
        patched,
        meta_block.replace("Contact", "Contact Updated"),
    )
    if replaced.count(social.SOCIAL_MARKER_BEGIN) != 1:
        raise AssertionError("meta block replacement should remain idempotent")
    if "Contact Updated" not in replaced:
        raise AssertionError("meta block replacement should update tag content")

    card_html = social.build_card_html(
        title="Contact",
        blocks=[
            {"tag": "h2", "text": "Contact"},
            {
                "tag": "p",
                "text": "For questions, comments, or feedback, please use one of the following methods.",
            },
        ],
        rel_html=nested,
        site_label="Rhythmdo",
        lang="en",
    )
    if "Rendered opening excerpt" not in card_html:
        raise AssertionError("card html should include the explanatory eyebrow")
    if "/contact/en/index.html" not in card_html:
        raise AssertionError("card html should include the source page path")

    print("OK: render-social-cards helpers verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
