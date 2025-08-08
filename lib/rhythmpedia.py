
def greet(name):
    return f"Hello, {name}! This is mymodule speaking."

import re
import html
from typing import List, Dict, Optional

HEADER_RE = re.compile(r'^(#{2,6})\s+(.*?)\s*(?:\{#([^\}]+)\})?\s*$')
# FENCE_OPEN_RE = re.compile(r'^[ \t]{0,3}([`~]{3,})(.*)$')  # backticks or tildes
# FENCE_CLOSE_RE = lambda ch, n: re.compile(r'^[ \t]{0,3}' + re.escape(ch * n) + r'\s*$')
FENCE_OPEN_RE  = re.compile(r'^[ \t]*([`~]{3,})(.*)$')
FENCE_CLOSE_RE = lambda ch, n: re.compile(r'^[ \t]*' + re.escape(ch * n) + r'\s*$')
HTML_TAG_RE = re.compile(r'<[^>]*>')

def parse_qmd_teasers(
    text: str,
    *,
    min_level: int = 2,
    max_level: int = 6,
    strip_html_in_title: bool = True,
    normalize_ws: bool = True,
    respect_frontmatter: bool = True,
    max_description_chars: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Parse a QMD/Markdown document and return an ordered list of dicts:
      { "header_title": str, "header_slug": str|None, "description": str }
    - Matches ATX headers ##..###### only (not Setext).
    - Ignores headers inside fenced code blocks and YAML front matter (optional).
    - The description is the leading run of content after the header until
      the first subsequent header line; does not cut through a code fence.

    I want a simple QMD parser function:

    1. Match each header using:
       ```python
       match = re.match(r'^(#{2,6})\\s+(.*?)\\s*(?:\\{#([^\\}]+)\\})?\\s*$', header_line)
       ```
    2. For each match, get the header title, the optional slug (if present),
       and the first part of the section — from the line after the header
       until the first child header if it exists, otherwise until the next
       sibling header.
    3. Create a dictionary:

       ```python
       {
            "header_title": header_title,
            "header_slug" : header_slug,
            "description" : first_part_of_section 
       }
       ```
    4. Append each dictionary to a list.
    5. Return the list.

    **Summary:**
    Scan QMD for level-2+ headers, extract each title, optional slug, and the
    section’s opening content until the first child or sibling header, and
    return them as a list of dictionaries.
    """
    lines = text.splitlines()

    # 1) Skip YAML front matter at file head (--- ... --- or ...)
    start_idx = 0
    if respect_frontmatter and lines and lines[0].strip() == "---":
        end = None
        for i in range(1, len(lines)):
            s = lines[i].strip()
            if s == "---" or s == "...":
                end = i
                break
        if end is not None:
            start_idx = end + 1

    # 2) Scan for headers while respecting fenced code blocks
    headers = []  # list of dicts with index, level, title_raw, slug, title_norm
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_close_re = None

    for i in range(start_idx, len(lines)):
        line = lines[i]

        # Fence open/close detection
        if not in_fence:
            m = FENCE_OPEN_RE.match(line)
            if m:
                seq = m.group(1)
                fence_char = seq[0]
                fence_len = len(seq)
                fence_close_re = FENCE_CLOSE_RE(fence_char, fence_len)
                in_fence = True
                continue
            # Only match headers when not in a fence
            hm = HEADER_RE.match(line)
            if hm:
                level = len(hm.group(1))
                if min_level <= level <= max_level:
                    raw_title = hm.group(2).strip()
                    slug = hm.group(3)
                    title_norm = _normalize_title(raw_title, strip_html_in_title)
                    headers.append({
                        "index": i,
                        "level": level,
                        "title_raw": raw_title,
                        "title_norm": title_norm,
                        "slug": slug,
                    })
                continue
        else:
            # inside fence; look for closing fence of same kind/length
            if fence_close_re.match(line):
                in_fence = False
                fence_char = ""
                fence_len = 0
                fence_close_re = None
            continue

    # Early exit if no headers
    if not headers:
        return []

    # 3) Build teaser/description for each header
    out: List[Dict[str, str]] = []
    total_lines = len(lines)

    for idx, h in enumerate(headers):
        h_idx = h["index"]
        h_level = h["level"]

        # Section starts after this header line
        section_start = h_idx + 1

        # End of this section is before the next header with level <= h.level,
        # or EOF if none.
        next_bound = total_lines
        for k in range(idx + 1, len(headers)):
            if headers[k]["level"] <= h_level:
                next_bound = headers[k]["index"]
                break

        # Teaser ends at the very first header encountered after section_start,
        # regardless of its level; but we must not cut through a code fence.
        teaser_lines = []
        in_fence = False
        fence_char = ""
        fence_len = 0
        fence_close_re = None

        j = section_start
        while j < next_bound:
            line = lines[j]

            # Handle fences so we never stop in the middle
            if not in_fence:
                m = FENCE_OPEN_RE.match(line)
                if m:
                    seq = m.group(1)
                    fence_char = seq[0]
                    fence_len = len(seq)
                    fence_close_re = FENCE_CLOSE_RE(fence_char, fence_len)
                    in_fence = True
                    teaser_lines.append(line)
                    j += 1
                    continue

                # If we hit any header and we're not in a fence, stop teaser
                if HEADER_RE.match(line):
                    break

                teaser_lines.append(line)
                j += 1
            else:
                teaser_lines.append(line)
                if fence_close_re.match(line):
                    in_fence = False
                    fence_char = ""
                    fence_len = 0
                    fence_close_re = None
                j += 1

        description = "\n".join(teaser_lines)
        if normalize_ws:
            description = _normalize_ws(description)

        if max_description_chars is not None and len(description) > max_description_chars:
            # Guard: avoid chopping an open fence. We'll truncate only if not inside an unmatched fence.
            description = description[:max_description_chars].rstrip()

        out.append({
            "header_title": h["title_norm"],
            "header_slug": h["slug"],  # explicit only; may be None
            "description": description,
            "level": h["level"],          # ← add
            "title_raw": h["title_raw"],  # ← add
        })

    return out


def _normalize_title(raw: str, strip_html_in_title: bool) -> str:
    s = raw.strip()
    if strip_html_in_title:
        s = HTML_TAG_RE.sub("", s)
        s = html.unescape(s)
    return s.strip()


def _normalize_ws(block: str) -> str:
    # Trim leading/trailing blank lines; collapse 2+ blank lines to one.
    lines = block.splitlines()
    # strip leading blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    # strip trailing blanks
    while lines and not lines[-1].strip():
        lines.pop()
    # collapse
    out = []
    blank = False
    for ln in lines:
        if ln.strip():
            out.append(ln.rstrip())
            blank = False
        else:
            if not blank:
                out.append("")
                blank = True
    return "\n".join(out)


#############

import re
from pathlib import Path
from typing import List, Optional, Tuple

# import your shared parser
# from your_shared_module import parse_qmd_teasers

RUBY_RE = re.compile(r"<ruby>(.*?)</ruby>", re.DOTALL | re.IGNORECASE)
RT_RE   = re.compile(r"<rt>.*?</rt>", re.DOTALL | re.IGNORECASE)
TAG_RE  = re.compile(r"<[^>]+>")

def _lang_id_from_filename(p: Path) -> str:
    stem = p.stem  # e.g., "master-ja"
    if "-" not in stem:
        raise ValueError(f"Filename must be master-<lang>.qmd: {p.name}")
    prefix, lang = stem.split("-", 1)
    if prefix != "master" or not lang:
        raise ValueError(f"Filename must be master-<lang>.qmd: {p.name}")
    return lang

def _ruby_base_or_none(title_html: str) -> Optional[str]:
    m = RUBY_RE.search(title_html)
    if not m:
        return None
    inner = m.group(1)
    base = RT_RE.sub("", inner)     # drop <rt>…</rt>
    base = TAG_RE.sub("", base).strip()
    return base or None

def _slugify_unicode(text: str) -> str:
    s = text.strip()
    s = TAG_RE.sub("", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[：・()（）［］「」、,\.‧·]+", "", s)
    return s.strip("-")

def _slug_for_item(title_raw: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    rb = _ruby_base_or_none(title_raw)
    return _slugify_unicode(rb if rb else title_raw)


def _create_toc_v3(text: str, basedir: str, lang: str) -> None:
    """
    Print a nested Markdown TOC from master-<lang>.qmd.

    - Level-2 →  ./<basedir>/<slug>/<lang-id>/
    - Level-3+ → ./<basedir>/<parent-slug>/<lang-id>/#<sub-slug>
    - Indent: 0 spaces at level-2, +2 spaces per deeper level
    """
    items = parse_qmd_teasers(
        text,
        min_level=2,
        max_level=6,
        strip_html_in_title=False,  # keep HTML to read <ruby> base
        normalize_ws=False,
        respect_frontmatter=True,
    )
    if not items:
        return

    current_lv2_slug: Optional[str] = None
    stack: List[Tuple[int, str]] = []

    lines_out = []

    for it in items:
        lvl: int = it["level"]           # provided by your parser
        title: str = it["header_title"]
        title_raw: str = it["title_raw"] # provided by your parser
        explicit: Optional[str] = it["header_slug"]

        slug = _slug_for_item(title_raw, explicit)

        if lvl == 2:
            current_lv2_slug = slug
            link = f"./{basedir}/{slug}/{lang}/"
        elif lvl ==3:
            ancestor = current_lv2_slug or slug
            link = f"./{basedir}/{ancestor}/{lang}/#{slug}"
        else:
            ancestor = current_lv2_slug or slug
            link = None

        while stack and stack[-1][0] >= lvl:
            stack.pop()

        stack.append((lvl, slug))

        if link is not None:
            indent = " " * (2 * max(0, lvl - 2))
            lines_out.append(f"{indent}- [{title}]({link})")

            description = it["description"].strip()
            if description and lvl == 2:
                lines_out.append(f"{indent}{description}")
                lines_out.append( "" )

    return "\n".join(lines_out)

def create_toc( input_qmd ):
    p = Path(input_qmd)
    basedir = str( p.parent ) # directory path as string
    lang = _lang_id_from_filename(p)
    text = p.read_text(encoding="utf-8")
    return _create_toc_v3(text, basedir, lang)


