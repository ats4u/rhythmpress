#!/usr/bin/env python3
from __future__ import annotations

from pathlib import PurePosixPath

from rhythmpress.scripts import rhythmpress_render_social_cards as social


def main() -> int:
    root = PurePosixPath("index.html")
    nested = PurePosixPath("contact/en/index.html")
    plain = PurePosixPath("robots.html")

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

    replaced = social.upsert_social_meta_block(patched, meta_block.replace("Contact", "Contact Updated"))
    if replaced.count(social.SOCIAL_MARKER_BEGIN) != 1:
        raise AssertionError("meta block replacement should remain idempotent")
    if "Contact Updated" not in replaced:
        raise AssertionError("meta block replacement should update tag content")

    card_html = social.build_card_html(
        title="Contact",
        blocks=[
            {"tag": "h2", "text": "Contact"},
            {"tag": "p", "text": "For questions, comments, or feedback, please use one of the following methods."},
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
