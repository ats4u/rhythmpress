#!/usr/bin/env python3
from __future__ import annotations

from pathlib import PurePosixPath

from rhythmpress.scripts import rhythmpress_render_social_cards as social


def main() -> int:
    root = PurePosixPath("index.html")
    nested = PurePosixPath("contact/en/index.html")
    plain = PurePosixPath("robots.html")

    ns = social.parse_args([])
    if ns.render_mode != "mobile-page":
        raise AssertionError("mobile-page should be the default social-card render mode")
    if ns.viewport != "800x600":
        raise AssertionError("800x600 should be the default mobile viewport")
    if ns.allow_remote:
        raise AssertionError("remote requests should be blocked by default")
    remote_ns = social.parse_args(["--allow-remote"])
    if not remote_ns.allow_remote:
        raise AssertionError("--allow-remote should opt in to remote requests")
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
