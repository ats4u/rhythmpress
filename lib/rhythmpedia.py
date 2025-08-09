
def greet(name):
    return f"Hello, {name}! This is mymodule speaking."

# ===============================================================
# compact front matter + wrapper 
# ===============================================================
import re
from typing import Any, Dict

_FM_RE = re.compile(r'^\ufeff?---\s*\n(.*?)\n(?:---|\.\.\.)\s*(?:\n|$)', re.DOTALL)

def parse_frontmatter(text: str) -> Dict[str, Any]:
    m = _FM_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    try:
        import yaml  # full YAML parser
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {"_frontmatter": data}
    except ModuleNotFoundError:
        raise RuntimeError(
            "PyYAML is required to parse front matter. "
            "Install it with: python -m pip install pyyaml"
        )
    except Exception as e:
        raise RuntimeError(f"Error parsing YAML front matter: {e}")


# ======================
# version 1
# ======================

import sys
import subprocess
import re 
from pathlib import Path

def create_toc_v1( input_md, link_target_md ):
    # Run pandoc to get TOC as Markdown
    toc_md = subprocess.run(
        [
            "pandoc",
            input_md,
            "--toc",
            "--toc-depth=6",
            "--to=markdown",  # ← output pure Markdown TOC
            "--template=templates/toc"  # optional: avoids front/back matter
        ],
        capture_output=True,
        text=True
    ).stdout

    # Patch all links to include the HTML filename prefix
    # [Title](#section-id) → [Title](tatenori-theory/index.html#section-id)
    patched = re.sub(r'\]\(#', f']({link_target_md}#', toc_md)

    # Add 2 extra spaces to every indented line
    shifted = '\n'.join(
        '  ' + line if re.match(r'^\s*- ', line) else line
        for line in patched.splitlines()
        if line.strip() != ''
    )
    return shifted

# ======================
# version 2 and later
# ======================

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

        # Compute character offsets in the original text
        section_start_char = sum(len(lines[i]) + 1 for i in range(section_start))
        section_end_char   = sum(len(lines[i]) + 1 for i in range(next_bound))

        out.append({
            "header_title"      : h["title_norm"],
            "header_slug"       : h["slug"],           # explicit only; may be None
            "description"       : description,
            "level"             : h["level"],          # ← add
            "title_raw"         : h["title_raw"],      # ← add
            "section_start_line": section_start,       # first content line after header
            "section_end_line"  : next_bound,          # first line after section
            "section_start_char": section_start_char,  # char offset of section_start
            "section_end_char"  : section_end_char,    # char offset of section_end
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
from textwrap import dedent, indent

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

def proc_qmd_teasers(items, basedir: str | Path, lang: str):
    """
    Decorate parsed heading items with file/link metadata.

    Adds:
      - it["slug"]            : final slug (explicit {#id} wins; else ruby-aware)
      - it["link"]            : H2 → ./<dir>/<slug>/<lang>/ ; H3+ → ./<dir>/<h2>/<lang>/#<slug>
      - it["out_path"]        : target file path for this heading (future-ready, all levels)
                                <base>/<slug>/<lang>/index.qmd   [flat by slug]
      - it["lang_index_path"] : <base>/<lang>/index.qmd

    Notes:
      - This function only annotates; callers may choose to write H2 only (current spec).
      - Links use the directory name (Path(basedir).name) to avoid absolute paths.
      - No de-duplication: ensure slugs are globally unique if you keep the flat layout.
    """
    base      = Path(basedir)
    base_name = base.name  # safe for links
    if base_name in ("", ".", "/"):
        base_name = base.resolve().name

    current_lv2_slug: Optional[str] = None

    for it in items:
        lvl: int = int(it["level"])
        title_raw: str = it["title_raw"]
        explicit: Optional[str] = it["header_slug"]

        slug = _slug_for_item(title_raw, explicit)
        it["base_name"] = base_name # the current directory name; this is safe for links
        it["slug"] = slug
        it["out_path"] = base / slug / lang / "index.qmd"
        # convenience: same for all items
        it["lang_index_path"] = base / lang / "index.qmd" 
        if lvl == 2:
            current_lv2_slug = slug
            it["link"] = f"./{base_name}/{slug}/{lang}/"
        else:
            ancestor = current_lv2_slug or slug
            it["link"] = f"./{base_name}/{ancestor}/{lang}/#{slug}"

    return items

#######################

def call_create_toc( input_qmd, create_toc ):
    p = Path(input_qmd)
    basedir = str( p.parent ) # directory path as string
    lang = _lang_id_from_filename(p)
    text = p.read_text(encoding="utf-8")
    return create_toc(text, basedir, lang)

#######################

def _create_toc_v3(text: str, basedir: str, lang: str) -> None:
    items = parse_qmd_teasers(
        text,
        min_level=2,
        max_level=6,
        strip_html_in_title=False,  # keep HTML to read <ruby> base
        normalize_ws=False,
        respect_frontmatter=True,
    )
    items = proc_qmd_teasers( items, basedir, lang )
    lines_out = []
    for it in items:
        lvl         : int = it["level"]
        link        : str = it["link"]
        description : str = it["description"].strip()
        title       : str = it["header_title"]

        indent_level = " " * (4 * max(0, lvl - 1))
        lines_out.append( f"{indent_level}- [{title}]({link})" )

    return "\n".join(lines_out)

def _create_toc_v4(text: str, basedir: str, lang: str) -> None:
    items = parse_qmd_teasers(
        text,
        min_level=2,
        max_level=6,
        strip_html_in_title=False,  # keep HTML to read <ruby> base
        normalize_ws=False,
        respect_frontmatter=True,
    )
    items = proc_qmd_teasers( items, basedir, lang )

    lines_out = []
    for it in items:
        lvl         : int = it["level"]
        link        : str = it["link"]
        description : str = it["description"].strip()
        title       : str = it["header_title"]

        if link is not None:
            indent_level = " " * (2 * max(0, lvl - 3))
            lines_out.append( f"{indent_level}- [{title}]({link})" )
            lines_out.append("")

            if description and lvl == 2:
                description = dedent(description).strip()
                description = indent(description, indent_level)
                lines_out.append(description)
                lines_out.append("")

    return "\n".join(lines_out)


def create_toc_v3( input_qmd ):
    return call_create_toc( input_qmd, _create_toc_v3 )

def create_toc_v4( input_qmd ):
    return call_create_toc( input_qmd, _create_toc_v4 )


#######################
# Master QMD SPlitter
#######################

from pathlib import Path
import sys, pathlib;
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));

def _hdr_start(text: str, it) -> int:
    # start of the header line (prev '\n' before section_start_char; -1→0)
    return text.rfind("\n", 0, int(it["section_start_char"])) + 1

def split_master_qmd(master_path: Path) -> None:
    print(f"\n→ {master_path}")
    lang = _lang_id_from_filename(master_path)
    text = master_path.read_text(encoding="utf-8")

    frontmatter = parse_frontmatter(text)

    items = parse_qmd_teasers(
        text, min_level=2, max_level=6,
        strip_html_in_title=False, normalize_ws=False, respect_frontmatter=True
    )
    if not items: print("  (no headers)"); return

    items = proc_qmd_teasers(items, str(master_path.parent), lang)
    h2s   = [it for it in items if int(it["level"]) == 2]
    if not h2s: print("  (no H2)"); return

    # preamble (everything before earliest H2 header)
    preamble = text[:min(_hdr_start(text, it) for it in h2s)]

    # 3-liner per section: slice → mkdir → write (H2 only per spec)
    for it in h2s:
        beg, end = _hdr_start(text, it), int(it["section_end_char"])
        section = text[beg:end]
        title_raw = it["title_raw"]
        # title_clean = TAG_RE.sub("", it["title_raw"]).strip()
        fm = f"---\ntitle: \"{title_raw}\"\n---\n\n"
        p: Path = it["out_path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(fm + section, encoding="utf-8")
        print(f"  ✅ {p}")

    # language index
    idx: Path = h2s[0]["lang_index_path"]
    lines = []
    if preamble.strip(): lines += [preamble.rstrip(), ""]
    lines += ["## Contents", ""]
    for it in h2s:
        base_name = it["base_name"]
        title = it["header_title"]
        slug  = it["slug"]
        desc  = (it["description"] or "").strip()
        # href  = f"../{slug}/{lang}/"   # <-- lang at the end
        href  = f"/{base_name}/{slug}/{lang}/"   # <-- lang at the end

        lines.append(f"### [{title}]({href})")

        if desc: lines.append(desc)
        lines.append("")

    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"  ✅ {idx}")


    # section_title = ""
    # yml_lang_path = master_path.parent / f"_quarto.index.{lang}.yml"
    # yml_lang_lines = [
    #     "website:",
    #     "  sidebar:",
    #     "    contents:",
    #     f"      - section: \"{section_title}\"",
    #     "        contents:",
    # ]
    # for it in h2s:
    #     slug = it["slug"]
    #     # project-relative path (no leading slash)
    #     yml_lang_lines.append(f"          - {slug}/{lang}/index.qmd")

    # yml_lang_path.write_text("\n".join(yml_lang_lines) + "\n", encoding="utf-8")
    # print(f"  ✅ {yml_lang_path}")


    # --- NEW: per-language YAML include: _quarto.index.<lang>.yml ---
    section_title = frontmatter.get("title") or "untitled"
    yml_lang_path = master_path.parent / f"_quarto.index.{lang}.yml"
    yml_lang_lines = [
        "website:",
        "  sidebar:",
        "    contents:",
        f"      - section: \"{section_title}\"",
        "        contents:",
    ]
    for it in h2s:
        base_name = it["base_name"]
        slug      = it["slug"]
        href      = f"{base_name}/{slug}/{lang}/index.qmd"
        yml_lang_lines.append(f"          - {href}")
    yml_lang_path.write_text("\n".join(yml_lang_lines) + "\n", encoding="utf-8")
    print(f"  ✅ {yml_lang_path}")





def split_all_masters( qmd_splitter , root: str | Path = ".") -> None:
    for p in sorted(Path(root).glob("master-*.qmd")):
        try: qmd_splitter(p)
        except Exception as e: print(f"  ✗ {p.name}: {e}")


# def create_toc( input_qmd ):
#     p = Path(input_qmd)
#     basedir = str( p.parent ) # directory path as string
#     lang = _lang_id_from_filename(p)
#     text = p.read_text(encoding="utf-8")
#     return _create_toc_v4(text, basedir, lang)
