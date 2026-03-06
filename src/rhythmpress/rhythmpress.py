def greet(name):
    return f"Hello, {name}! This is mymodule speaking."



# ===============================================================
# extract_junks_from_attr_block
# ADDED Thu, 23 Oct 2025 21:07:24 +0900
# ===============================================================
import re

# Matches: #id  (id = [Unicode word chars] + [- . ~] + %HH escapes)
_ID_TOKEN_RE = re.compile(
    r'#(?:\w|%[0-9A-Fa-f]{2})(?:[\w.\-~]|%[0-9A-Fa-f]{2})*',
    re.UNICODE
)

def extract_junks_from_attr_block(attr_block: str) -> list[str]:
    """
    Given a Quarto property block body like:
      '#foo .bar key=val #タイトル'
    return only the ID tokens (without '#'):
      ['foo', 'タイトル']
    """
    return [m.group(0)[1:] for m in _ID_TOKEN_RE.finditer(attr_block or "")]

# If you currently parse headers line-by-line, this convenience helps:
_HDR_ATTRS_RE = re.compile(r'^\s{0,3}#{1,6}\s.*?\{([^}]*)\}\s*$', re.UNICODE)

def extract_junks_from_header_line(line: str) -> list[str]:
    """
    From a full header line like:
      '## Title {#foo .x key=1 #タイトル}'
    return ['foo', 'タイトル'].
    """
    m = _HDR_ATTRS_RE.match(line)
    if not m:
        return []
    return extract_junks_from_attr_block(m.group(1))


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

def as_bool(v, default=True):
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"1","true","yes","on"}
    if isinstance(v, int):
        return v != 0
    return bool(v)


from typing import Any, Mapping
from pathlib import Path
from .lang_registry import format_language_label
from datetime import date, datetime

#------------------------------------------------
# Added on Mon, 01 Sep 2025 01:55:08 +0900
#------------------------------------------------
def dump_frontmatter(data: Mapping[str, Any] | None, *, line_ending: str = "\n", allow_empty: bool = False) -> str:
    """
    Serialize a front-matter object to a YAML front-matter block.

    Inverse of `parse_frontmatter`:

        parse_frontmatter(dump_frontmatter(M)) == M
        # and for non-mapping payloads:
        parse_frontmatter(dump_frontmatter({"_frontmatter": X})) == {"_frontmatter": X}

    Behavior:
    - If `data` is falsy (None or {}), returns "" unless `allow_empty=True`
      (then returns an empty front matter block).
    - If `data` is exactly {"_frontmatter": X}, emits a bare YAML document `X`
      (not wrapped in a mapping) to faithfully invert `parse_frontmatter`.

    Parameters:
      line_ending: "\n" by default. Use "\r\n" on Windows if you prefer.
      allow_empty: If True and data is falsy, emit:
                   "---\\n---\\n" (with your chosen line ending)
    """
    if not data:
        return f"---{line_ending}---{line_ending}" if allow_empty else ""

    try:
        import yaml
    except ModuleNotFoundError:
        raise RuntimeError(
            "PyYAML is required to dump front matter. "
            "Install it with: python -m pip install pyyaml"
        )

    # Use a custom SafeDumper that:
    # - preserves key order (sort_keys=False)
    # - avoids YAML anchors/aliases (ignore_aliases)
    # - formats multiline strings in block style (|)
    class _Dumper(yaml.SafeDumper):
        pass

    # Avoid anchors/aliases to keep FM clean
    _Dumper.ignore_aliases = lambda self, data: True  # type: ignore[method-assign]

    # Multiline strings -> block style (|)
    def _repr_str(dumper: yaml.SafeDumper, value: str):
        style = '|' if '\n' in value else None
        return dumper.represent_scalar('tag:yaml.org,2002:str', value, style=style)

    # Path -> string
    def _repr_path(dumper: yaml.SafeDumper, value: Path):
        return dumper.represent_scalar('tag:yaml.org,2002:str', str(value))

    # Dates/DateTimes -> ISO8601 (Quarto/Pandoc friendly)
    def _repr_date(dumper: yaml.SafeDumper, value: date):
        # date only (YYYY-MM-DD)
        return dumper.represent_scalar('tag:yaml.org,2002:timestamp', value.isoformat())

    def _repr_datetime(dumper: yaml.SafeDumper, value: datetime):
        # keep timezone info if present
        return dumper.represent_scalar('tag:yaml.org,2002:timestamp', value.isoformat())

    _Dumper.add_representer(str, _repr_str)
    _Dumper.add_representer(Path, _repr_path)
    _Dumper.add_representer(date, _repr_date)
    _Dumper.add_representer(datetime, _repr_datetime)

    # If the caller passed {"_frontmatter": X}, emit X as the root (bare document)
    payload: Any = data["_frontmatter"] if (isinstance(data, dict) and set(data.keys()) == {"_frontmatter"}) else data

    yaml_text = yaml.dump(
        payload,
        Dumper=_Dumper,
        default_flow_style=False,  # block style
        sort_keys=False,           # preserve insertion order
        allow_unicode=True
    )

    # Ensure trailing newline inside the block
    if not yaml_text.endswith(line_ending):
        yaml_text += line_ending

    return f"---{line_ending}{yaml_text}---{line_ending}"


# ======================
# version 1
# ======================

import sys
import subprocess
import re 
from pathlib import Path

def _interpolate_quarto_vars_in_text(text: str, basedir: str, lang: str) -> str:
    """Interpolate Quarto-style variables like {{<var foo.bar>}} and {{<var env:FOO>}}
    in a plain text blob. Mirrors the light-weight logic used in `proc_qmd_teasers`.
    Fails soft (returns the original text) if variables cannot be loaded.
    """
    try:
        from . import quarto_vars as _qv
        var_ctx = _qv.get_variables(cwd=str(basedir), lang=lang)
    except Exception:
        var_ctx = None

    import re, os
    VAR_SC = re.compile(r"\{\{<\s*var\s+([A-Za-z0-9_.:-]+)\s*>\}\}")

    def _deep_get(d, dotted):
        cur = d
        for p in dotted.split("."):
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
        return cur

    def repl(m):
        key = m.group(1)
        if key.startswith("env:"):
            return os.environ.get(key[4:], "")
        if isinstance(var_ctx, dict):
            val = _deep_get(var_ctx, key)
            return "" if val is None else str(val)
        return ""

    if not isinstance(text, str):
        return text
    text = VAR_SC.sub(repl, text)

    # Also: convert trailing HTML-commented header attributes into real Pandoc attributes.
    # e.g., "## Title <!-- {#id .class} -->"  ->  "## Title {#id .class}"
    import re as _re
    _HDR_ATTR = _re.compile(r"^(#{1,6}[^\n]*?)\s*<!--\s*\{([^}]+)\}\s*-->\s*$", _re.MULTILINE)
    text = _HDR_ATTR.sub(r"\1 {\2}", text)
    return text

def _create_toc_v1( input_md: Path, text: str, basedir: str, lang: str ):
    # Interpolate {{<var ...>}} placeholders before handing text to pandoc,
    # so TOC titles reflect the final rendered strings (matches _create_toc_v5 behavior).
    from pathlib import Path as _P
    import tempfile as _tempfile, os as _os
    interpolated_text = _interpolate_quarto_vars_in_text(text, basedir, lang)
    # Write a temporary file in the same directory to keep relative refs stable.
    tmp_dir = _P(basedir)
    with _tempfile.NamedTemporaryFile('w', suffix=input_md.suffix or '.qmd',
                                      prefix='._toc_v1_', dir=str(tmp_dir),
                                      delete=False, encoding='utf-8') as _tf:
        _tf.write(interpolated_text)
        tmp_input = _tf.name

    # Run pandoc to get TOC as Markdown (use absolute paths)

    # v3.2: input_md must be a Path to an existing file; template fixed at ./rhythmpress/templates/toc
    if not isinstance(input_md, Path):
        raise ValueError("input_md must be a pathlib.Path")
    if not input_md.is_file():
        raise FileNotFoundError(f"input_md not found: {input_md}")

    # Now create_toc_v1 also parse the current QMD. But we don't use its `link`
    # field yet; we will migrate `parse_qmd_teasers` fully in future.
    # Wed, 20 Aug 2025 19:05:52 +0900
    items = parse_qmd_teasers(
        text,
        min_level=2,
        max_level=6,
        strip_html_in_title=False,  # keep HTML to read <ruby> base
        normalize_ws=False,
        respect_frontmatter=True,
    )
    items = proc_qmd_teasers( items, basedir, lang )

    # Now it reads frontmatter in order to check its title
    frontmatter = parse_frontmatter(text)
    section_title = frontmatter.get("title") or "Untitled"

    h0s   = [it for it in items if int(it["level"]) == 0] # ADDED BY ATS Wed, 20 Aug 2025 19:06:14 +0900
    preamble = h0s[0] if 0 < len(h0s) else None # ADDED BY ATS Wed, 20 Aug 2025 19:06:26 +0900

    # resolve template path relative to this module (./rhythmpress/templates/toc)
    module_dir = Path(__file__).resolve().parent
    template = module_dir / "templates" / "toc.markdown"
    if not template.exists():
        raise FileNotFoundError(f"pandoc template not found: {template}")

    # ensure pandoc exists (no CWD dependence)
    import shutil  # local import to avoid reordering global imports
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc not found on PATH")

    # Run pandoc to get TOC as Markdown (use absolute paths)
    proc = subprocess.run(
        [
            "pandoc",
            str(tmp_input),
            "--toc",
            "--toc-depth=6",
            "--to=markdown",  # ← output pure Markdown TOC
            "--from=markdown+header_attributes",  # be explicit about header attr support
            f"--template={str(template)}"  # avoid front/back matter
        ],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        # ensure temp file is cleaned up even on failure
        try:
            _os.unlink(tmp_input)
        except Exception:
            pass
        raise RuntimeError(f"pandoc failed ({proc.returncode}): {proc.stderr.strip()}")

    toc_md = proc.stdout
    # cleanup temp file after successful run
    try:
        _os.unlink(tmp_input)
    except Exception:
        pass

    # Patch all links to include the HTML filename prefix
    # [Title](#section-id) → [Title](tatenori-theory/index.html#section-id)
    patched = re.sub(r'\]\(#', f']({basedir}/{lang}#', toc_md)

    # Add 2 extra spaces to every indented line
    shifted = '\n'.join(
        '  ' + line if re.match(r'^\s*- ', line) else line
        for line in patched.splitlines()
        if line.strip() != ''
    )

#    output = shifted
#    if preamble is not None:
#        link        : str = preamble["link"]
#        description : str = preamble["description"].rstrip()
#        title       : str = preamble["header_title"]
#
#        if link is not None:
#            output = f"### {title}\n- [**{title}**]({link})\n{description}\n\n" + output
#        else:
#            output = f"### {title}\n- [**{title}**](#)\n{description}\n\n" + output

    # Always emit the file header, even if there is no preamble text.
    output = shifted
    if preamble is not None:
        link        : str = preamble.get("link") or f"{basedir}/{lang}/"
        description : str = preamble.get("description", "").rstrip()
        title       : str = preamble.get("header_title") or section_title
    else:
        link        : str = f"{basedir}/{lang}/"
        description : str = ""
        title       : str = section_title

    header_block = f"## {title}\n- [**{title}**]({link})"
    if description:
        header_block += f"\n{description}"
    output = header_block + "\n\n" + output

    return output



# ======================
# version 2 and later
# ======================

import re
import html
from typing import List, Dict, Optional

HEADER_RE = re.compile(r'^(#{2,6})\s+(.*?)\s*(?:\{([^\}]+)\})?\s*$')
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
    Parse a QMD/Markdown document and return an ordered list of dicts describing
    the file-level teaser (level==0) and each section teaser (levels 2..6):

      {
        "header_title": str | None,   # frontmatter's ttile for master teaser
        "header_slug" : str | None,   # explicit {#id} if present (sections only)
        "description" : str,          # teaser text (trimmed/normalized)
        "level"       : int,          # 0 (file) or 2..6 (sections)
        "title_raw"   : str,          # original header text ("" for file-level)
        "section_start_line": int,    # first content line in teaser slice
        "section_end_line"  : int,    # first line after teaser slice
        "section_start_char": int,    # char offset of start
        "section_end_char"  : int,    # char offset of end
      }

    Rules
    - Skips YAML front matter at top (--- … --- or ...), if respect_frontmatter=True.
    - Recognizes ATX headers ##..###### only (not Setext).
    - Honors fenced code blocks (``` or ~~~ of any length ≥3) so we never split a fence.
    - The file-level “master teaser” spans from end of front matter to just before the
      first header (or EOF if no headers).
    - Each section’s teaser spans from the header line’s next line up to (but not
      including) the next header of level <= current level; teaser text stops early
      if any header is encountered before that (unless inside an open fence).

    Title normalization
    - If strip_html_in_title=True, header titles have HTML tags removed and are
      HTML-unescaped for display; raw header text is preserved in "title_raw".
    """

    frontmatter = parse_frontmatter(text)
    section_title = frontmatter.get("title") or "Untitled"
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

    # 2) Build a "master teaser": from after front matter to before first header
    out: List[Dict[str, str]] = []
    in_fence_mt = False
    fence_close_mt = None
    first_header_line = None
    j = start_idx
    while j < len(lines):
        ln = lines[j]
        if not in_fence_mt:
            m = FENCE_OPEN_RE.match(ln)
            if m:
                seq = m.group(1)
                fence_close_mt = FENCE_CLOSE_RE(seq[0], len(seq))
                in_fence_mt = True
                j += 1
                continue
            if HEADER_RE.match(ln):
                first_header_line = j
                break
            j += 1
        else:
            if fence_close_mt and fence_close_mt.match(ln):
                in_fence_mt = False
                fence_close_mt = None
            j += 1

    mt_end = first_header_line if first_header_line is not None else len(lines)
    master_block = "\n".join(lines[start_idx:mt_end])
    if normalize_ws:
        master_block = _normalize_ws(master_block)
    if max_description_chars is not None and len(master_block) > max_description_chars:
        master_block = master_block[:max_description_chars].rstrip()
    if master_block.strip():
        out.append({
            "header_title"      : section_title,
            "header_slug"       : None,
            "description"       : master_block,
            "level"             : 0,
            "title_raw"         : section_title,
            "section_start_line": start_idx,
            "section_end_line"  : mt_end,
            "section_start_char": sum(len(lines[i]) + 1 for i in range(start_idx)),
            "section_end_char"  : sum(len(lines[i]) + 1 for i in range(mt_end)),
        })

    # 3) Scan for headers while respecting fenced code blocks
    headers = []  # list of dicts with index, level, title_raw, slug, title_norm
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_close_re = None

    for i in range(mt_end, len(lines)):  # start after master teaser slice
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
                    # raw_title = hm.group(2).strip()
                    # slug = hm.group(3)
                    raw_title = hm.group(2).strip()
                    attr_block = hm.group(3)  # full contents inside {...} or None
                    ids = extract_junks_from_attr_block(attr_block or "")
                    slug = ids[0] if ids else None

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
            if fence_close_re and fence_close_re.match(line):
                in_fence = False
                fence_char = ""
                fence_len = 0
                fence_close_re = None
            continue

    # Early exit if no headers: return only the master teaser (if any)
    if not headers:
        return out

    # 4) Build teaser/description for each header
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
                if fence_close_re and fence_close_re.match(line):
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
            "level"             : h["level"],
            "title_raw"         : h["title_raw"],
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

def proc_qmd_teasers(
    items,
    basedir: str | Path,
    lang: str,
    link_prefix: str = "/",
    *,
    interpolate_vars: bool = True,
):
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

    If `interpolate_vars` is True (default), titles from ATL headers are first
    interpolated using Quarto-style variables (e.g. `${project.title}`,
    `${site_url}`, `${env:FOO}`) loaded via `rhythmpress.quarto_vars.get_variables`.
    Interpolation happens *before* slugging and link building, so sidebars and
    front-matter titles won’t leak raw placeholders.
    """
    # --- variable interpolation (title fields) -------------------------------
    # We do this once per call, then apply to every item prior to slugging.
    var_ctx = None
    if interpolate_vars:
        try:
            # Lazy import to avoid hard dependency in non-Quarto contexts
            from . import quarto_vars as _qv
            var_ctx = _qv.get_variables(cwd=str(basedir), lang=lang)
        except Exception:
            # If anything goes wrong loading variables, fail soft: just skip
            var_ctx = None

    # local, dependency-free interpolation that understands ${dot.paths} and ${env:FOO}
    import re, os
    VAR_SC = re.compile(r"\{\{<\s*var\s+([A-Za-z0-9_.:-]+)\s*>\}\}")

    def _deep_get(d, dotted: str):
        cur = d
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur

    def _interp(s: str) -> str:
        if not (interpolate_vars and var_ctx and isinstance(s, str)):
            return s
        def repl(m):
            key = m.group(1)
            if key.startswith("env:"):
                return os.environ.get(key[4:], "")
            val = _deep_get(var_ctx, key) if isinstance(var_ctx, dict) else None
            return "" if val is None else str(val)
        return VAR_SC.sub(repl, s)

    base      = Path(basedir)
    base_name = base.name  # safe for links
    if base_name in ("", ".", "/"):
        base_name = base.resolve().name

    # normalize link_prefix to end with one slash
    if link_prefix == "":
        link_prefix = "./"
    if not link_prefix.endswith("/"):
        link_prefix += "/"

    current_lv2_slug: Optional[str] = None

    for it in items:
        lvl: int = int(it["level"])
        # interpolate title fields first so slug/link reflect final text
        title_raw: str = _interp(it.get("title_raw", ""))
        if "title_raw" in it:
            it["title_raw"] = title_raw
        if "header_title" in it and isinstance(it["header_title"], str):
            it["header_title"] = _interp(it["header_title"])
        explicit: Optional[str] = it["header_slug"]

        slug = _slug_for_item(title_raw, explicit)
        it["base_name"] = base_name # the current directory name; this is safe for links
        it["slug"] = slug
        it["out_path"] = base / slug / lang / "index.qmd"
        # convenience: same for all items
        it["lang_index_path"] = base / lang / "index.qmd" 
        if lvl == 0:
            it["link"] = f"{link_prefix}{base_name}/{lang}/"
        elif lvl == 2:
            current_lv2_slug = slug
            it["link"] = f"{link_prefix}{base_name}/{slug}/{lang}/"
        else:
            ancestor = current_lv2_slug or slug
            it["link"] = f"{link_prefix}{base_name}/{ancestor}/{lang}/#{slug}"

    return items

#######################

from .strip_header_comments import strip_header_comments
def call_create_toc( create_toc, input_qmd, **kwargs ):
    p = Path(input_qmd)
    basedir = str( p.parent.name ) # directory path as string
    lang = _lang_id_from_filename(p)
    text = p.read_text(encoding="utf-8")
    text = strip_header_comments(text)
    return create_toc( input_qmd, text, basedir, lang, **kwargs )

#######################

def _create_toc_v3(input_qmd: Path, text: str, basedir: str, lang: str, **_) -> str:
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

def _create_toc_v4(input_qmd: Path, text: str, basedir: str, lang: str, **_) -> str:
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

# =========================================
# _create_toc_v5
# =========================================
# Added on Sun, 10 Aug 2025 19:20:03 +0900 by Ats
def _create_toc_v5(input_qmd: Path, text: str, basedir: str, lang: str, *, link_prefix: str = "/" ) -> str:
    items = parse_qmd_teasers(
        text,
        min_level=2,
        max_level=6,
        strip_html_in_title=False,  # keep HTML to read <ruby> base
        normalize_ws=False,
        respect_frontmatter=True,
    )
    items = proc_qmd_teasers( items, basedir, lang, link_prefix )

    lines_out = []

    for it in items:
        lvl         : int = it["level"]
        link        : str = it["link"]
        description : str = it["description"].strip()
        title       : str = it["header_title"]
        indent_level = " " * (2 * max(0, lvl - 2))

        if link is not None:
            if lvl == 0:
                lines_out.append("")
                lines_out.append( f"## {title}" )
                if description:
                    lines_out.append( "" )
                    lines_out.append( f"{indent_level}- [**{title}**]({link})" )
                    lines_out.append( "" )
                    lines_out.append( "<!-- -->" )
                    lines_out.append( description )
                    lines_out.append( "<!-- -->" )
                    lines_out.append( "" )

                lines_out.append( "<!-- -->" )
            elif lvl == 2:
                # description = dedent(description).strip()
                # description = indent(description, indent_level)
                lines_out.append("")
                lines_out.append( f"### {title}" )
                if description:
                    lines_out.append( "" )
                    lines_out.append( "<!-- -->" )
                    lines_out.append( description )
                    lines_out.append( "<!-- -->" )
                    lines_out.append( "" )
                    lines_out.append( "---" )
                    lines_out.append( "" )

                lines_out.append( "<!-- -->" )
                lines_out.append( f"{indent_level}- [{title}]({link})" )
            elif lvl == 3:
                lines_out.append( f"{indent_level}- [{title}]({link})" )


    return "\n".join(lines_out)



def create_toc_v1( input_qmd, **kwargs ):
    return call_create_toc( _create_toc_v1, input_qmd, **kwargs )

def create_toc_v3( input_qmd, **kwargs ):
    return call_create_toc( _create_toc_v3, input_qmd, **kwargs )

def create_toc_v4( input_qmd, **kwargs ):
    return call_create_toc( _create_toc_v4, input_qmd, **kwargs )

def create_toc_v5( input_qmd, **kwargs ):
    return call_create_toc( _create_toc_v5, input_qmd, **kwargs )


#######################
# Master QMD SPlitter
#######################

import pathlib
import os
from pathlib import Path

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));
sys.path.append(os.path.dirname(__file__))

import sys, pathlib;
from .strip_header_comments import strip_header_comments
from .git_dates import get_git_dates, GitDatesError  # add near other imports

def _hdr_start(text: str, it) -> int:
    # start of the header line (prev '\n' before section_start_char; -1→0)
    return text.rfind("\n", 0, int(it["section_start_char"])) + 1

def split_master_qmd(master_path: Path, *, toc: bool = True ) -> None:
    print(f"\n→ {master_path}")
    lang = _lang_id_from_filename(master_path)
    text = master_path.read_text(encoding="utf-8")
    text = strip_header_comments(text)

    frontmatter = parse_frontmatter(text)

    items = parse_qmd_teasers(
        text, min_level=2, max_level=6,
        strip_html_in_title=False, normalize_ws=False, respect_frontmatter=True
    )
    if not items: print("  (no headers)"); return

    items = proc_qmd_teasers(items, str(master_path.parent), lang)
    h0s   = [it for it in items if int(it["level"]) == 0] # ADDED BY ATS Wed, 20 Aug 2025 17:48:44 +0900
    h2s   = [it for it in items if int(it["level"]) == 2]
    if not h2s: print("  (no H2)"); return

    # preamble (everything before earliest H2 header)
    # preamble = text[:min(_hdr_start(text, it) for it in h2s)]
    preamble = h0s[0] if 0 < len(h0s) else None # ADDED BY ATS Wed, 20 Aug 2025 18:02:26 +0900

    # Resolve dates once per master (policy: all sections inherit master’s Git dates)
    try:
        _cdate, _mdate = get_git_dates(str(master_path))
    except GitDatesError as e:
        raise GitDatesError(
            f"Failed to resolve git dates for master file: {master_path}\n{e}"
        ) from e

    # 3-liner per section: slice → mkdir → write (H2 only per spec)
    for it in h2s:
        beg, end = _hdr_start(text, it), int(it["section_end_char"])
        section = text[beg:end]
        title_raw = it["title_raw"]

        # Inject cdate/mdate into section front matter via the serializer
        fm = dump_frontmatter({
            **frontmatter,   # shallow copy all keys/values
            "title": title_raw,
            "cdate": _cdate,   # assume already YYYY-MM-DD or ISO8601 strings
            "mdate": _mdate,
        })

        # ensure exactly one blank line after FM
        if not fm.endswith("\n\n"):
            fm = fm.rstrip("\n") + "\n\n"

        if toc:
            # {{< include /_sidebar.generated.md >}}
            footer =  f"\n{{{{< include /_sidebar-{lang}.generated.md >}}}}\n"
        else:
            footer =  ''

        p: Path = it["out_path"]
        sub_text = fm + section + footer
        if not p.exists() or p.read_text(encoding="utf-8") != sub_text:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(sub_text, encoding="utf-8")
            print(f"  ✅ {p}")
        else:
            print(f"  ✅ {p} skipped")

    # (rest of function unchanged…)

    # Language index via create_toc_v5 (absolute links)
    idx: Path = h2s[0]["lang_index_path"]
    toc_md = create_toc_v5(str(master_path), link_prefix="/")

    # Only use the TOC output. It already includes the master teaser (level==0)
    # with the headline, so we avoid duplicating the teaser here.
    # idx_lines: List[str] = [toc_md]
    # idx_text = "\n".join(idx_lines).rstrip() + "\n"

    # Provide a page title so the banner shows text.
    page_title = (
        (preamble.get("header_title") if isinstance(preamble, dict) else None)
        or h2s[0].get("title")
        or h2s[0].get("header_title")
        or Path(master_path).parent.name
    )
    fm = f"---\ntitle: {page_title}\n---\n\n"
    idx_text = fm + (toc_md if toc_md.endswith("\n") else toc_md + "\n")

    if not idx.exists() or idx.read_text(encoding="utf-8") != idx_text:
        idx.parent.mkdir(parents=True, exist_ok=True)
        idx.write_text(idx_text, encoding="utf-8")
        print(f"  ✅ SUB INDEX {idx}")
    else:
        print(f"  ✅ SUB INDEX {idx} skipped")

    # section_title = ""
    # yml_lang_path = master_path.parent / f"_quarto-{lang}.yml"
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


    # --- NEW: per-language YAML include: _sidebar.index.<lang>.yml ---
    section_title = frontmatter.get("title") or "Untitled"
    yml_lang_path = master_path.parent / f"_sidebar-{lang}.yml"

    # yml_lang_lines = [
    #     "website:",
    #     "  sidebar:",
    #     "    contents:",
    #     f"      - section: \"{section_title}\"",
    #     "        contents:",
    # ]


    # Build a per-language sidebar section. Previously the section node had no
    # `href`, which made the section title non-clickable in Quarto's sidebar UI
    # even when it represented a real directory with its own index page.
    # We now point the section itself to the directory index:
    #   <dir>/<lang>/index.qmd
    base_name = master_path.parent.name
    section_href = f"{base_name}/{lang}/index.qmd"
    yml_lang_lines = [
        "website:",
        "  sidebar:",
        "    contents:",
        f"      - section: \"{section_title}\"",
        f"        href: {section_href}",
        "        contents:",
    ]

    for it in h2s:
        base_name = it["base_name"]
        slug      = it["slug"]
        href      = f"{base_name}/{slug}/{lang}/index.qmd"
        yml_lang_lines.append(f"          - {href}")

    sidebar = as_bool( frontmatter.get("rhythmpress-preproc-sidebar", None), default=True )
    print(f"[DEBUG] {yml_lang_path} sidebar = {sidebar}")

    if sidebar:

        yml_text = "\n".join(yml_lang_lines) + "\n"
        if not yml_lang_path.exists() or yml_lang_path.read_text(encoding="utf-8") != yml_text:
            yml_lang_path.write_text(yml_text, encoding="utf-8")
            print(f"  ✅ {yml_lang_path}")
        else:
            print(f"  =  {yml_lang_path} (unchanged)")
    else:
        print(f"  = {yml_lang_path} (suppressed)")


# --- new: copy master-<lang>.qmd -> ./<lang>/index.qmd using split_all_masters ---
#######################
# Master QMD SPlitter
# Added by Ats on Mon, 11 Aug 2025 23:13:20 +0900
#######################

from pathlib import Path
import shutil
from .strip_header_comments import strip_header_comments
from .git_dates import get_git_dates, GitDatesError  # add near other imports

def copy_lang_qmd(master_path: Path, *, toc: bool = True ) -> None:
    """
    Copy ./master-<lang>.qmd -> ./<lang>/index.qmd and emit
    ./_sidebar-<lang>.yml with a single contents entry.
    Touch files only when content changed (prevents preview loops).
    """
    print(f"\n→ {master_path}")
    lang = _lang_id_from_filename(master_path)
    dst  = master_path.parent / lang / "index.qmd"

    # Copy master -> <lang>/index.qmd (idempotent) & read front matter
    src_text = master_path.read_text(encoding="utf-8")
    src_text = strip_header_comments(src_text)

    frontmatter = parse_frontmatter(src_text)

    # Follow front matter flag (default True, explicit false suppresses YAML)
    sidebar = as_bool( frontmatter.get("rhythmpress-preproc-sidebar", None), default=True )
    print(f"[DEBUG] {dst} sidebar = {sidebar}")

    # Resolve dates from Git (single source of truth)
    try:
        _cdate, _mdate = get_git_dates(str(master_path))
    except GitDatesError as e:
        raise GitDatesError(
            f"Failed to resolve git dates for master file: {master_path}\n{e}"
        ) from e

    # Parse and update/insert YAML front matter
    m = _FM_RE.match(src_text)
    if m:
        body = src_text[m.end():]
    else:
        body = src_text

    if "title" not in frontmatter:
        frontmatter[ "title" ] = "Untitled"

    # Inject cdate/mdate into section front matter via the serializer
    new_yaml = dump_frontmatter({
        **frontmatter,   # shallow copy all keys/values
        # "title": title_raw,
        "cdate": _cdate,   # assume already YYYY-MM-DD or ISO8601 strings
        "mdate": _mdate,
    })

    # ensure exactly one blank line after FM
    if not new_yaml.endswith("\n\n"):
        new_yaml = new_yaml.rstrip("\n") + "\n\n"

    new_text = new_yaml + body



    # Optionally append sidebar include as a TOC block (preserve existing behavior)
    if toc:
        new_text = new_text + f"\n{{{{< include /_sidebar-{lang}.generated.md >}}}}\n"

    if not dst.exists() or dst.read_text(encoding="utf-8") != new_text:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(new_text, encoding="utf-8")
        print(f"  ✅ {dst}")
    else:
        print(f"  =  {dst} (unchanged)")

    # (rest of function unchanged…)



    base_name = str(master_path.parent.name)

    # Minimal sidebar include: no 'section', just the file path.
    yml_path = master_path.parent / f"_sidebar-{lang}.yml"
    if sidebar:
        yml_text = f"website:\n  sidebar:\n    contents:\n      - {base_name}/{lang}/index.qmd\n"
        if not yml_path.exists() or yml_path.read_text(encoding="utf-8") != yml_text:
            yml_path.write_text(yml_text, encoding="utf-8")
            print(f"  ✅ {yml_path}")
        else:
            print(f"  =  {yml_path} (unchanged)")
    else:
        print(f"  =  {yml_path} (suppressed)")


def clean_directories_except_attachments_qmd( root: Path ):
    # v3.2: require Path; explicit; root must be an existing directory (error if file/nonexistent)
    if not isinstance(root, Path):
        raise ValueError("root must be a pathlib.Path")
    if not root.exists():
        raise ValueError(f"root must exist: {root}")
    if root.is_file() or not root.is_dir():
        raise ValueError(f"root must be a directory, not a file: {root}")

    base = root
    for item in base.iterdir():
        if item.is_dir():
            if item.name.startswith("attachments"):
                print(f"🛡️  Skipping: {item}")
                continue
            print(f"🧹 Removing: {item}")
            shutil.rmtree(item)


import traceback

def qmd_all_masters( qmd_splitter, root: Path, *args, **kwargs) -> None:

    # v3.2: require Path; explicit; root must be an existing directory (error if file/nonexistent)
    if not isinstance(root, Path):
        raise ValueError("root must be a pathlib.Path")
    if not root.exists():
        raise ValueError(f"root must exist: {root}")
    if root.is_file() or not root.is_dir():
        raise ValueError(f"root must be a directory: {root}")

    # # Include both Quarto and Markdown masters; prefer .qmd if both exist.
    # masters = {}
    # for pat in ("master-*.qmd", "master-*.md"):
    #     for pth in root.glob(pat):
    #         key = (pth.parent, pth.stem)  # e.g., (dir, "master-ja")
    #         masters.setdefault(key, pth)  # .qmd wins because it’s added first

    # v3.3: If LANG_ID is set, process only that language’s master file.
    # This prevents duplicate work when the outer build loop iterates per-language.
    forced_lang = (os.environ.get("LANG_ID") or "").strip()
    if forced_lang:
        preferred = [
            root / f"master-{forced_lang}.qmd",
            root / f"master-{forced_lang}.md",
        ]
        chosen = next((p for p in preferred if p.exists()), None)
        if not chosen:
            existing = sorted([*root.glob("master-*.qmd"), *root.glob("master-*.md")])
            names = ", ".join(p.name for p in existing) or "none"
            raise ValueError(
                f"LANG_ID={forced_lang!r} but no master-{forced_lang}.qmd/md under {root}. Existing: {names}"
            )
        masters = {(chosen.parent, chosen.stem): chosen}
    else:
        # Include both Quarto and Markdown masters; prefer .qmd if both exist.
        masters = {}
        for pat in ("master-*.qmd", "master-*.md"):
            for pth in root.glob(pat):
                key = (pth.parent, pth.stem)  # e.g., (dir, "master-ja")
                masters.setdefault(key, pth)  # .qmd wins because it’s added first

    for p in sorted(masters.values()):
        try:
            qmd_splitter(p, *args, **kwargs)
        except Exception as e:
            print(f"  ✗ {p.name}: {e}")
            traceback.print_exc()


# def create_toc( input_qmd ):
#     p = Path(input_qmd)
#     basedir = str( p.parent ) # directory path as string
#     lang = _lang_id_from_filename(p)
#     text = p.read_text(encoding="utf-8")
#     return _create_toc_v4(text, basedir, lang)


# =========================================
# Article page scaffolder (idempotent)
# =========================================
from datetime import datetime

def _write_if_absent(path: Path, content: str) -> bool:
    """
    Write text to path only if the file does not exist.
    Returns True if the file was created, False if it already existed.
    """
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def create_article_page(target: Path, *, lang: str = "ja") -> list[Path]:
    """
    Create a new article directory with:
      - an empty sentinel file `.article_dir`
      - a `.gitignore`
      - a starter master file: `master-{lang}.qmd` (default: ja)

    * Idempotent: existing files are left untouched.
    * Safe: refuses to operate on project root; target must be inside the project.

    Returns a list of paths that now exist (created or pre-existing).
    """
    if not isinstance(target, Path):
        raise ValueError("target must be a pathlib.Path")

    target = target if target.is_absolute() else Path.cwd() / target
    target = target.resolve()

    # Find project root (git or Quarto)
    proj = target
    found_root = None
    for p in [proj, *proj.parents]:
        if (p / ".git").exists() or (p / "_quarto.yml").exists():
            found_root = p
            break
    if found_root is None:
        raise RuntimeError("Not inside a recognized project (no .git or _quarto.yml found).")
    try:
        target.relative_to(found_root)
    except ValueError:
        raise RuntimeError("Target must be inside the project root.")

    if target == found_root:
        raise RuntimeError("Refusing to operate on the project root; specify a subdirectory.")

    created_paths: list[Path] = []

    # Ensure directory exists
    target.mkdir(parents=True, exist_ok=True)

    # 1) .article_dir (empty)
    sentinel = target / ".article_dir"
    if _write_if_absent(sentinel, ""):
        created_paths.append(sentinel)

    # 2) .gitignore (basic)
    gi = target / ".gitignore"
    gi_body = "\n".join([
        "# Project-local ignores",
        ".DS_Store",
        ".quarto/",
        ".site/",
        "*/",
        "!attachments*/",
        "_sidebar-*",
        "",
    ]) + "\n"
    if _write_if_absent(gi, gi_body):
        created_paths.append(gi)

    # 3) master-{lang}.qmd (starter)
    master = target / f"master-{lang}.qmd"
    today = datetime.now().strftime("%Y-%m-%d")
    qmd = "\n".join([
        "---",
        f'title: "Untitled"',
        f'date: {today}',
        f'lang: {lang}',
        "format:",
        "  html:",
        "    toc: true",
        "---",
        "",
        "> Draft. Replace this with your content.",
        "",
        "## Overview",
        "",
        "Write your section intro here.",
        "",
    ]) + "\n"
    if _write_if_absent(master, qmd):
        created_paths.append(master)

    # Always return the canonical set of paths (for clarity), whether created or not
    return [sentinel, gi, master]

# Public stable alias requested by Ats
def create_page(target: Path, *, lang: str = "ja") -> list[Path]:
    """Thin alias for create_article_page for script callers."""
    return create_article_page(target, lang=lang)


# =========================================
# Global Navigation Generator 
# ADDED Thu, 21 Aug 2025 02:22:13 +0900
# =========================================
#
import os, sys

from typing import List, Tuple

def create_global_navigation(input_conf, lang_id: str, *, strict: bool = True, logger=None) -> str:
    """
    Assemble a single Markdown navigation by concatenating TOCs from each
    article directory listed in `input_conf`.

    For each directory:
      - Pick master-{lang_id}.qmd (preferred) or master-{lang_id}.md.
      - Read front matter key `rhythmpress-preproc`:
          "split" -> use create_toc_v5 (split layout)
          "copy"  -> use create_toc_v1 (copy-as-is layout)
        If the key is absent, default to "copy".

    Parameters
    ----------
    input_conf : str | os.PathLike
        Path to a conf file with one directory per line. Lines may contain
        inline comments after '#' and blank lines are ignored. Order is
        preserved and defines output order.
    lang_id : str
        Language id used to choose the master file (mandatory).
    strict : bool, default True
        If True, unknown/invalid lines, YAML entries, missing dirs/masters,
        and unknown preproc values raise. If False, they are warned and
        skipped when possible.
    logger : logging.Logger | None
        Optional logger to emit info/warning/debug messages.

    Returns
    -------
    str
        Concatenated Markdown suitable for direct inclusion (e.g., in a Quarto page).
    """
    from pathlib import Path
    import re

    def _log(level: str, msg: str):
        if logger is not None:
            getattr(logger, level, logger.info)(msg)
        #else:
        #    import sys
        #    # print(f"[{level.upper()}] {msg}", file=sys.stderr)

    conf_path = Path(input_conf).expanduser().resolve()
    if not conf_path.exists():
        raise FileNotFoundError(f"conf not found: {conf_path}")
    if not conf_path.is_file():
        raise ValueError(f"conf is not a file: {conf_path}")
    conf_dir = conf_path.parent

    # Parse lines (sed 's/#.*//' style): strip inline comments and blanks
    entries: List[Tuple[int, str]] = []
    for i, raw_line in enumerate(conf_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = re.sub(r"#.*$", "", raw_line).strip()
        if line:
            entries.append((i, line))

    out_parts: List[str] = []
    seen_dirs = set()

    for lineno, rel in entries:
        # Directories only — YAML entries are errors
        low = rel.lower()
        if low.endswith(".yml") or low.endswith(".yaml"):
            msg = f"{conf_path.name}:{lineno}: expected a directory path, got a YAML file: {rel}"
            if strict:
                raise ValueError(msg)
            _log("warning", msg)
            continue

        d = (conf_dir / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
        if not d.exists() or not d.is_dir():
            msg = f"{conf_path.name}:{lineno}: not a directory: {rel} -> {d}"
            if strict:
                raise FileNotFoundError(msg)
            _log("warning", msg)
            continue

        # Deduplicate directories while preserving first occurrence
        key = str(d)
        if key in seen_dirs:
            _log("warning", f"{conf_path.name}:{lineno}: duplicate directory ignored: {d}")
            continue
        seen_dirs.add(key)

        # Choose master for lang_id
        qmd = d / f"master-{lang_id}.qmd"
        md  = d / f"master-{lang_id}.md"
        master = qmd if qmd.exists() else (md if md.exists() else None)
        if master is None:
            msg = f"{d}: master file not found (tried {qmd.name} and {md.name})"
            if strict:
                raise FileNotFoundError(msg)
            _log("warning", msg)
            continue

        # Decide mode from front matter (default: copy)
        text = master.read_text(encoding="utf-8")
        fm = parse_frontmatter(text) if text else {}

        # Respect per-article sidebar opt-out
        # If front matter has: rhythmpress-preproc-sidebar: false → skip this directory
        sidebar_opt = fm.get("rhythmpress-preproc-sidebar", None)
        if sidebar_opt is False:
            _log("info", f"[{d.name}] {master.name} → sidebar=false (skipped)")
            continue

        raw_mode = fm.get("rhythmpress-preproc", None)
        if isinstance(raw_mode, bool):
            mode = "split" if raw_mode else "copy"
        elif isinstance(raw_mode, str):
            mode = raw_mode.strip().lower()
        else:
            mode = "copy"

        if mode not in {"copy", "split"}:
            msg = f"{d.name}: unknown rhythmpress-preproc='{raw_mode}'; falling back to 'copy'"
            if strict:
                raise ValueError(msg)
            _log("warning", msg)
            mode = "copy"

        _log("info", f"[{d.name}] {master.name} → mode={mode}")

        # Delegate
        try:
            block = create_toc_v5(master) if mode == "split" else create_toc_v1(master)
        except Exception as e:
            if strict:
                raise
            _log("warning", f"{d.name}: TOC generation failed: {e}")
            continue

        block = (block or "").rstrip()
        if block:
            out_parts.append(block)

    return "\n\n<!-- -->\n\n".join(out_parts) + ("\n" if out_parts else "")


def _router_noop_output(msg: str) -> str:
    return (
        f"<!-- rhythmpress router warning: {msg} -->\n"
        "<script>(function(){})();</script>\n"
    )


def _normalize_route_path(raw: str | None, lang: str) -> str:
    path = (raw or "").strip()
    if not path:
        path = f"/{lang}/"
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path


def _parse_runtime_router_conf(conf_path: Path) -> tuple[str | None, dict[str, str]]:
    """
    Parse optional router settings from _rhythmpress.conf.

    Supported keys:
      - default_lang=ja
      - default-language=ja
      - lang_path.ja=/ja/
      - route.en=/en/
    """
    default_lang: str | None = None
    lang_paths: dict[str, str] = {}

    for raw in conf_path.read_text(encoding="utf-8").splitlines():
        line = re.sub(r"#.*$", "", raw).strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            continue

        key_norm = key.lower().replace("-", "_")
        if key_norm in {"default_lang", "default_language", "default"}:
            default_lang = val
            continue

        for prefix in ("lang_path.", "langpath.", "route."):
            if key_norm.startswith(prefix):
                lang = key[len(prefix):].strip()
                if lang:
                    lang_paths[lang] = val
                break

    return default_lang, lang_paths


def _resolve_runtime_conf_path(input_conf: str, current_lang: str) -> Path:
    conf_path = Path(input_conf).expanduser()
    if not conf_path.is_absolute():
        candidates: list[Path] = []
        project_roots: list[Path] = []

        for env_key in ("QUARTO_PROJECT_DIR", "RHYTHMPRESS_ROOT"):
            raw = os.environ.get(env_key, "").strip()
            if not raw:
                continue
            root = Path(raw).expanduser()
            if root not in project_roots:
                project_roots.append(root)

        for root in project_roots:
            candidates.append((root / conf_path).resolve())
            if current_lang:
                candidates.append((root / current_lang / conf_path).resolve())

        candidates.append((Path.cwd() / conf_path).resolve())

        existing = next((p for p in candidates if p.exists()), None)
        conf_path = existing if existing is not None else candidates[0]
    return conf_path


def _load_runtime_language_context(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool,
) -> tuple[list[str], str, dict[str, str]]:
    from .lang_ids import detect_language_ids

    conf_path = _resolve_runtime_conf_path(input_conf, current_lang)
    if not conf_path.exists():
        msg = f"conf not found: {conf_path}"
        if strict:
            raise FileNotFoundError(msg)
        raise ValueError(msg)
    if not conf_path.is_file():
        msg = f"conf is not a file: {conf_path}"
        if strict:
            raise ValueError(msg)
        raise ValueError(msg)

    project_root = conf_path.parent
    lang_ids = detect_language_ids(project_root)

    if not lang_ids:
        msg = f"no language ids found near {project_root}"
        if strict:
            raise ValueError(msg)
        raise ValueError(msg)

    bcp47 = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
    valid_lang_ids = [x for x in lang_ids if bcp47.match(x)]
    if not valid_lang_ids:
        msg = "all detected language ids are invalid (not IETF-like tags)"
        if strict:
            raise ValueError(msg)
        raise ValueError(msg)

    dropped = sorted(set(lang_ids) - set(valid_lang_ids))
    if dropped and strict:
        raise ValueError(f"invalid language ids: {', '.join(dropped)}")

    detected_default, conf_paths = _parse_runtime_router_conf(conf_path)
    default_lang = (detected_default or current_lang or "").strip()
    if default_lang not in valid_lang_ids:
        if strict:
            raise ValueError(
                f"default language '{default_lang}' is not in detected languages {valid_lang_ids}"
            )
        default_lang = valid_lang_ids[0]

    route_map: dict[str, str] = {}
    for lang in valid_lang_ids:
        route_map[lang] = _normalize_route_path(conf_paths.get(lang), lang)

    return valid_lang_ids, default_lang, route_map


def create_runtime_language_router(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Return asis-ready HTML/JS for root-entry language routing.
    """
    import json

    try:
        valid_lang_ids, default_lang, route_map = _load_runtime_language_context(
            input_conf, current_lang, strict=strict
        )
    except Exception as e:
        if strict:
            raise
        return _router_noop_output(str(e))

    lang_ids_json = json.dumps(valid_lang_ids, ensure_ascii=False)
    route_map_json = json.dumps(route_map, ensure_ascii=False, sort_keys=True)
    default_json = json.dumps(default_lang, ensure_ascii=False)

    return (
        "<script>\n"
        "(function () {\n"
        f"  const AVAILABLE = {lang_ids_json};\n"
        f"  const ROUTES = {route_map_json};\n"
        f"  const DEFAULT_LANG = {default_json};\n"
        "  const PATH = window.location.pathname || \"/\";\n"
        "  const isRootEntry = PATH === \"/\" || PATH === \"/index.html\";\n"
        "  if (!isRootEntry) return;\n"
        "\n"
        "  const lowerToCanonical = Object.create(null);\n"
        "  for (const x of AVAILABLE) lowerToCanonical[String(x).toLowerCase()] = x;\n"
        "\n"
        "  function canonicalize(candidate) {\n"
        "    if (!candidate) return null;\n"
        "    const c = String(candidate).trim().toLowerCase();\n"
        "    if (!c) return null;\n"
        "    if (lowerToCanonical[c]) return lowerToCanonical[c];\n"
        "    const base = c.split('-')[0];\n"
        "    if (lowerToCanonical[base]) return lowerToCanonical[base];\n"
        "    return null;\n"
        "  }\n"
        "\n"
        "  function readCookie(name) {\n"
        "    const m = document.cookie.match(new RegExp('(?:^|;\\\\s*)' + name + '=([^;]+)'));\n"
        "    return m ? decodeURIComponent(m[1]) : null;\n"
        "  }\n"
        "\n"
        "  let preferred = null;\n"
        "  try { preferred = canonicalize(localStorage.getItem('rhythmpress_lang')); } catch (_) {}\n"
        "  if (!preferred) preferred = canonicalize(readCookie('rhythmpress_lang'));\n"
        "  if (!preferred) preferred = canonicalize(readCookie('lang'));\n"
        "  if (!preferred) {\n"
        "    const nav = navigator.languages || [];\n"
        "    for (const n of nav) {\n"
        "      preferred = canonicalize(n);\n"
        "      if (preferred) break;\n"
        "    }\n"
        "  }\n"
        "  if (!preferred) preferred = DEFAULT_LANG;\n"
        "\n"
        "  const target = ROUTES[preferred] || ROUTES[DEFAULT_LANG];\n"
        "  if (!target) return;\n"
        "\n"
        "  const normalizedPath = PATH.endsWith('/') ? PATH : (PATH + '/');\n"
        "  if (normalizedPath === target) return;\n"
        "  window.location.replace(target);\n"
        "})();\n"
        "</script>\n"
    )


def create_runtime_language_switcher(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Return asis-ready HTML/JS for a current-page language switcher.
    """
    import json

    try:
        valid_lang_ids, default_lang, route_map = _load_runtime_language_context(
            input_conf, current_lang, strict=strict
        )
    except Exception as e:
        if strict:
            raise
        return _router_noop_output(str(e))

    canonical_current = current_lang if current_lang in valid_lang_ids else default_lang
    options_html = "".join(
        [
            f'<option value="{lang}"{" selected" if lang == canonical_current else ""}>{format_language_label(lang)}</option>'
            for lang in valid_lang_ids
        ]
    )

    route_map_json = json.dumps(route_map, ensure_ascii=False, sort_keys=True)
    current_json = json.dumps(canonical_current, ensure_ascii=False)

    return (
        '<label for="rhythmpress-lang-switcher">Language</label>\n'
        '<select id="rhythmpress-lang-switcher">'
        f"{options_html}"
        "</select>\n"
        "<script>\n"
        "(function () {\n"
        f"  const ROUTES = {route_map_json};\n"
        f"  const CURRENT_LANG = {current_json};\n"
        "  const el = document.getElementById('rhythmpress-lang-switcher');\n"
        "  if (!el) return;\n"
        "  function writeChoice(lang) {\n"
        "    try { localStorage.setItem('rhythmpress_lang', lang); } catch (_) {}\n"
        "    document.cookie = 'rhythmpress_lang=' + encodeURIComponent(lang) + '; path=/; max-age=31536000; SameSite=Lax';\n"
        "  }\n"
        "  function persistCurrentSelection() {\n"
        "    const selected = String(el.value || '').trim();\n"
        "    if (!selected || !ROUTES[selected]) return;\n"
        "    writeChoice(selected);\n"
        "  }\n"
        "  function replaceCurrentLangPath(path, fromLang, toLang) {\n"
        "    const token = '/' + fromLang + '/';\n"
        "    const idx = path.lastIndexOf(token);\n"
        "    if (idx >= 0) return path.slice(0, idx) + '/' + toLang + '/' + path.slice(idx + token.length);\n"
        "    if (path === '/' + fromLang || path === '/' + fromLang + '/' || path === '/' + fromLang + '/index.html') {\n"
        "      return ROUTES[toLang] || path;\n"
        "    }\n"
        "    return ROUTES[toLang] || path;\n"
        "  }\n"
        "  el.addEventListener('change', function () {\n"
        "    const targetLang = String(el.value || '').trim();\n"
        "    if (!targetLang || !ROUTES[targetLang]) return;\n"
        "    writeChoice(targetLang);\n"
        "    const p = window.location.pathname || '/';\n"
        "    const targetPath = replaceCurrentLangPath(p, CURRENT_LANG, targetLang);\n"
        "    const targetUrl = targetPath + (window.location.search || '') + (window.location.hash || '');\n"
        "    if (targetUrl === window.location.pathname + window.location.search + window.location.hash) return;\n"
        "    window.location.assign(targetUrl);\n"
        "  });\n"
        "  el.addEventListener('click', function () { setTimeout(persistCurrentSelection, 0); });\n"
        "  const initialLang = String(CURRENT_LANG || '').trim();\n"
        "  if (initialLang && ROUTES[initialLang]) writeChoice(initialLang);\n"
        "})();\n"
        "</script>\n"
    )


def create_runtime_language_switcher_links(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Return asis-ready HTML/JS for a link-based language switcher.

    This variant renders one clickable language link per line.
    """
    try:
        valid_lang_ids, default_lang, route_map = _load_runtime_language_context(
            input_conf, current_lang, strict=strict
        )
    except Exception as e:
        if strict:
            raise
        return _router_noop_output(str(e))

    canonical_current = current_lang if current_lang in valid_lang_ids else default_lang
    links: list[str] = []
    for lang in valid_lang_ids:
        href = route_map.get(lang) or "/"
        label = format_language_label(lang)
        aria = ' aria-current="page"' if lang == canonical_current else ""
        text = f"<strong>{label}</strong>" if lang == canonical_current else label
        links.append(
            f'<a href="{href}" class="rhythmpress-lang-anchor" data-lang="{lang}"{aria}>{text}</a>'
        )
    links_html = "<br>\n".join(links)

    return (
        '<nav class="rhythmpress-lang-switcher-links" aria-label="Language switcher">\n'
        f"{links_html}\n"
        "</nav>\n"
        "<script>\n"
        "(function () {\n"
        "  function writeChoice(lang) {\n"
        "    try { localStorage.setItem('rhythmpress_lang', lang); } catch (_) {}\n"
        "    document.cookie = 'rhythmpress_lang=' + encodeURIComponent(lang) + '; path=/; max-age=31536000; SameSite=Lax';\n"
        "  }\n"
        "  const nodes = document.querySelectorAll('a.rhythmpress-lang-anchor[data-lang]');\n"
        "  for (const node of nodes) {\n"
        "    node.addEventListener('click', function () {\n"
        "      const lang = String(node.getAttribute('data-lang') || '').trim();\n"
        "      if (!lang) return;\n"
        "      writeChoice(lang);\n"
        "    });\n"
        "  }\n"
        "})();\n"
        "</script>\n"
    )


def create_runtime_language_switcher_data_js(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Return JS source that sets global runtime language-switcher data.
    """
    import json

    try:
        valid_lang_ids, default_lang, route_map = _load_runtime_language_context(
            input_conf, current_lang, strict=strict
        )
    except Exception as e:
        if strict:
            raise
        msg = json.dumps(str(e), ensure_ascii=False)
        return (
            "/* rhythmpress router warning: generated no-op switcher */\n"
            f"console.warn({msg});\n"
        )

    canonical_current = current_lang if current_lang in valid_lang_ids else default_lang
    lang_ids_json = json.dumps(valid_lang_ids, ensure_ascii=False)
    route_map_json = json.dumps(route_map, ensure_ascii=False, sort_keys=True)
    current_json = json.dumps(canonical_current, ensure_ascii=False)
    default_json = json.dumps(default_lang, ensure_ascii=False)
    labels_json = json.dumps(
        {lang: format_language_label(lang) for lang in valid_lang_ids},
        ensure_ascii=False,
        sort_keys=True,
    )

    return (
        "(function () {\n"
        "  globalThis.RHYTHMPRESS_LANG_SWITCHER = {\n"
        f"    available: {lang_ids_json},\n"
        f"    routes: {route_map_json},\n"
        f"    labels: {labels_json},\n"
        f"    currentHint: {current_json},\n"
        f"    defaultLang: {default_json}\n"
        "  };\n"
        "})();\n"
    )


def create_runtime_language_switcher_ui_js() -> str:
    """
    Return JS source that renders toolbar switcher from RHYTHMPRESS_LANG_SWITCHER.
    """
    return (
        "(function () {\n"
        "  const DATA = globalThis.RHYTHMPRESS_LANG_SWITCHER;\n"
        "  if (!DATA || !Array.isArray(DATA.available) || !DATA.routes) return;\n"
        "  const AVAILABLE = DATA.available;\n"
        "  const ROUTES = DATA.routes;\n"
        "  const LABELS = DATA.labels || {};\n"
        "  const CURRENT_HINT = DATA.currentHint;\n"
        "  const DEFAULT_LANG = DATA.defaultLang;\n"
        "\n"
        "  function canonicalize(candidate) {\n"
        "    if (!candidate) return null;\n"
        "    const c = String(candidate).trim().toLowerCase();\n"
        "    if (!c) return null;\n"
        "    for (const x of AVAILABLE) {\n"
        "      const lx = String(x).toLowerCase();\n"
        "      if (c === lx || c.split('-')[0] === lx.split('-')[0]) return x;\n"
        "    }\n"
        "    return null;\n"
        "  }\n"
        "\n"
        "  function detectCurrentLang(pathname) {\n"
        "    const p = pathname || '/';\n"
        "    for (const lang of AVAILABLE) {\n"
        "      const token = '/' + lang + '/';\n"
        "      if (p.includes(token) || p === '/' + lang || p === '/' + lang + '/index.html') return lang;\n"
        "    }\n"
        "    return canonicalize(CURRENT_HINT) || canonicalize(DEFAULT_LANG) || AVAILABLE[0] || null;\n"
        "  }\n"
        "\n"
        "  function writeChoice(lang) {\n"
        "    try { localStorage.setItem('rhythmpress_lang', lang); } catch (_) {}\n"
        "    document.cookie = 'rhythmpress_lang=' + encodeURIComponent(lang) + '; path=/; max-age=31536000; SameSite=Lax';\n"
        "  }\n"
        "  function persistCurrentSelection(select) {\n"
        "    const targetLang = canonicalize(select.value);\n"
        "    if (!targetLang || !ROUTES[targetLang]) return;\n"
        "    writeChoice(targetLang);\n"
        "  }\n"
        "\n"
        "  function replaceCurrentLangPath(path, fromLang, toLang) {\n"
        "    if (!fromLang) return ROUTES[toLang] || path;\n"
        "    const token = '/' + fromLang + '/';\n"
        "    const idx = path.lastIndexOf(token);\n"
        "    if (idx >= 0) return path.slice(0, idx) + '/' + toLang + '/' + path.slice(idx + token.length);\n"
        "    if (path === '/' + fromLang || path === '/' + fromLang + '/' || path === '/' + fromLang + '/index.html') {\n"
        "      return ROUTES[toLang] || path;\n"
        "    }\n"
        "    return ROUTES[toLang] || path;\n"
        "  }\n"
        "\n"
        "  function mount() {\n"
        "    const existing = document.getElementById('rhythmpress-lang-switcher');\n"
        "    if (existing) return;\n"
        "    const currentLang = detectCurrentLang(window.location.pathname || '/');\n"
        "\n"
        "    const box = document.createElement('div');\n"
        "    box.className = 'rp-lang-switcher-toolbar d-flex align-items-center';\n"
        "    box.style.marginLeft = '0.75rem';\n"
        "\n"
        "    const dropdown = document.createElement('div');\n"
        "    dropdown.className = 'dropdown rp-lang-switcher-dropdown';\n"
        "\n"
        "    const toggle = document.createElement('button');\n"
        "    toggle.id = 'rhythmpress-lang-switcher';\n"
        "    toggle.type = 'button';\n"
        "    toggle.className = 'btn btn-sm dropdown-toggle';\n"
        "    toggle.setAttribute('data-bs-toggle', 'dropdown');\n"
        "    toggle.setAttribute('aria-expanded', 'false');\n"
        "    toggle.textContent = LABELS[currentLang] || String(currentLang || 'Language');\n"
        "\n"
        "    const menu = document.createElement('ul');\n"
        "    menu.className = 'dropdown-menu dropdown-menu-end';\n"
        "\n"
        "    toggle.classList.add('btn-outline-secondary');\n"
        "    toggle.style.backgroundColor = 'transparent';\n"
        "\n"
        "    function withAlpha(rgb, alpha) {\n"
        "      const m = String(rgb || '').match(/^\\s*rgba?\\(\\s*([0-9.]+)\\s*,\\s*([0-9.]+)\\s*,\\s*([0-9.]+)(?:\\s*,\\s*([0-9.]+))?\\s*\\)\\s*$/i);\n"
        "      if (!m) return null;\n"
        "      const r = Math.max(0, Math.min(255, Math.round(Number(m[1]))));\n"
        "      const g = Math.max(0, Math.min(255, Math.round(Number(m[2]))));\n"
        "      const b = Math.max(0, Math.min(255, Math.round(Number(m[3]))));\n"
        "      return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';\n"
        "    }\n"
        "\n"
        "    function applyToggleTone() {\n"
        "      const navbar = document.querySelector('.navbar');\n"
        "      if (!navbar) return;\n"
        "      const navStyle = window.getComputedStyle(navbar);\n"
        "      const navColor = navStyle && navStyle.color ? navStyle.color : '';\n"
        "      if (!navColor) return;\n"
        "      toggle.style.color = navColor;\n"
        "      toggle.style.borderColor = withAlpha(navColor, 0.6) || navColor;\n"
        "    }\n"
        "\n"
        "    applyToggleTone();\n"
        "\n"
        "    function navigateToLang(targetLang) {\n"
        "      if (!targetLang || !ROUTES[targetLang]) return;\n"
        "      writeChoice(targetLang);\n"
        "      const p = window.location.pathname || '/';\n"
        "      const nextPath = replaceCurrentLangPath(p, currentLang, targetLang);\n"
        "      const targetUrl = nextPath + (window.location.search || '') + (window.location.hash || '');\n"
        "      if (targetUrl === window.location.pathname + window.location.search + window.location.hash) return;\n"
        "      window.location.assign(targetUrl);\n"
        "    }\n"
        "\n"
        "    for (const lang of AVAILABLE) {\n"
        "      const li = document.createElement('li');\n"
        "      const item = document.createElement('button');\n"
        "      item.type = 'button';\n"
        "      item.className = 'dropdown-item';\n"
        "      if (lang === currentLang) item.classList.add('active');\n"
        "      item.textContent = LABELS[lang] || String(lang);\n"
        "      item.addEventListener('click', function () {\n"
        "        const targetLang = canonicalize(lang);\n"
        "        if (!targetLang) return;\n"
        "        navigateToLang(targetLang);\n"
        "      });\n"
        "      li.appendChild(item);\n"
        "      menu.appendChild(li);\n"
        "    }\n"
        "\n"
        "    dropdown.appendChild(toggle);\n"
        "    dropdown.appendChild(menu);\n"
        "    if (currentLang && ROUTES[currentLang]) writeChoice(currentLang);\n"
        "\n"
        "    const MOBILE_QUERY = '(max-width: 991.98px)';\n"
        "    const media = window.matchMedia ? window.matchMedia(MOBILE_QUERY) : null;\n"
        "    let toolsWrap = null;\n"
        "\n"
        "    function ensureToolsWrap(tools) {\n"
        "      if (!tools) return null;\n"
        "      if (!toolsWrap || !toolsWrap.isConnected || toolsWrap.parentElement !== tools) {\n"
        "        const wrap = document.createElement('span');\n"
        "        wrap.className = 'rp-switcher-tools-inline';\n"
        "        wrap.style.display = 'inline-flex';\n"
        "        wrap.style.alignItems = 'center';\n"
        "        wrap.style.marginRight = '0.5rem';\n"
        "        tools.insertBefore(wrap, tools.firstChild);\n"
        "        toolsWrap = wrap;\n"
        "      }\n"
        "      return toolsWrap;\n"
        "    }\n"
        "\n"
        "    function placeSwitcher() {\n"
        "      applyToggleTone();\n"
        "      const slot = document.getElementById('rhythmpress-lang-switcher-slot');\n"
        "      const tools = document.querySelector('.navbar .quarto-navbar-tools');\n"
        "      const isMobile = !!(media ? media.matches : (window.innerWidth <= 991.98));\n"
        "      const slotInCollapsedNav = !!(slot && slot.closest('.navbar-collapse'));\n"
        "\n"
        "      if (slot && !(isMobile && slotInCollapsedNav)) {\n"
        "        while (slot.firstChild) slot.removeChild(slot.firstChild);\n"
        "        slot.appendChild(dropdown);\n"
        "        if (toolsWrap && !toolsWrap.hasChildNodes() && toolsWrap.parentNode) toolsWrap.parentNode.removeChild(toolsWrap);\n"
        "        toolsWrap = null;\n"
        "        return;\n"
        "      }\n"
        "\n"
        "      if (tools) {\n"
        "        const wrap = ensureToolsWrap(tools);\n"
        "        if (wrap && dropdown.parentElement !== wrap) {\n"
        "          wrap.appendChild(dropdown);\n"
        "        }\n"
        "        return;\n"
        "      }\n"
        "\n"
        "      const host =\n"
        "        document.querySelector('.navbar .navbar-nav.ms-auto') ||\n"
        "        document.querySelector('.navbar .navbar-nav') ||\n"
        "        document.querySelector('.navbar .navbar-collapse');\n"
        "      if (!host) return;\n"
        "\n"
        "      if (dropdown.parentElement !== box) {\n"
        "        while (box.firstChild) box.removeChild(box.firstChild);\n"
        "        box.appendChild(dropdown);\n"
        "      }\n"
        "      if (box.parentElement !== host) {\n"
        "        host.appendChild(box);\n"
        "      }\n"
        "    }\n"
        "\n"
        "    placeSwitcher();\n"
        "    window.addEventListener('resize', placeSwitcher);\n"
        "    if (media && media.addEventListener) {\n"
        "      media.addEventListener('change', placeSwitcher);\n"
        "    } else if (media && media.addListener) {\n"
        "      media.addListener(placeSwitcher);\n"
        "    }\n"
        "  }\n"
        "\n"
        "  if (document.readyState === 'loading') {\n"
        "    document.addEventListener('DOMContentLoaded', mount);\n"
        "  } else {\n"
        "    mount();\n"
        "  }\n"
        "})();\n"
    )


def create_runtime_language_switcher_js(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Backward-compatible combined JS (data bootstrap + UI mount).
    """
    data_js = create_runtime_language_switcher_data_js(
        input_conf=input_conf,
        current_lang=current_lang,
        strict=strict,
    )
    ui_js = create_runtime_language_switcher_ui_js()
    if data_js.endswith("\n"):
        return data_js + ui_js
    return data_js + "\n" + ui_js


def create_runtime_root_entry(
    input_conf: str,
    current_lang: str,
    *,
    strict: bool = False,
) -> str:
    """
    Return ASIS content for root entry pages.

    Behavior:
      - If `RHYTHMPRESS_PREVIEW` is set (truthy), return line-break anchored language links.
      - Otherwise, return root redirect router script.
    """
    raw = os.environ.get("RHYTHMPRESS_PREVIEW", "").strip().lower()
    is_preview = raw not in {"", "0", "false", "no", "off"}
    if is_preview:
        return create_runtime_language_switcher_links(
            input_conf=input_conf,
            current_lang=current_lang,
            strict=strict,
        )
    return create_runtime_language_router(
        input_conf=input_conf,
        current_lang=current_lang,
        strict=strict,
    )
