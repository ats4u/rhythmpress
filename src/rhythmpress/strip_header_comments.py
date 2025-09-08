import re

_FENCE_OPEN_RE = re.compile(r'^(\s*)(`{3,}|~{3,})')      # ``` or ~~~ (len ≥ 3)
_ATX_RE        = re.compile(r'^\s{0,3}#{1,6}\s+')        # ATX headers
_SETEXT_RE     = re.compile(r'^\s{0,3}(=+|-+)\s*$')      # Setext underlines
_UNWRAP_RE     = re.compile(r'<!--\s*(.*?)\s*-->')       # capture inner, no DOTALL

def strip_header_comments(text: str) -> str:
    """
    Unwrap HTML comments ONLY in Markdown headers, returning a new string.
      - ATX:    "# Title <!-- {#id} -->" → "# Title {#id}"
      - Setext: "Title <!-- {.x} -->" + "-----" → "Title {.x}" + "-----"
    Leaves everything else (including non-header comments) unchanged.
    Skips fenced code blocks (```/~~~) and YAML front matter at top.
    """
    lines = text.splitlines(keepends=True)

    out: list[str] = []
    in_fence = False
    fence_char = None
    fence_len = 0
    in_front_matter = False
    at_file_start = True
    prev_line: str | None = None  # buffer to detect Setext titles

    def flush_prev():
        nonlocal prev_line
        if prev_line is not None:
            out.append(prev_line)
            prev_line = None

    for line in lines:
        # YAML front matter only at very start
        if at_file_start:
            at_file_start = False
            if line.strip() == '---':
                in_front_matter = True
                out.append(line)
                continue

        if in_front_matter:
            out.append(line)
            if line.strip() in ('---', '...'):
                in_front_matter = False
            continue

        # Fenced code blocks
        if in_fence:
            stripped = line.lstrip()
            if stripped and fence_char:
                i = 0
                while i < len(stripped) and stripped[i] == fence_char:
                    i += 1
                if i >= fence_len:
                    in_fence = False
                    fence_char = None
                    fence_len = 0
            out.append(line)
            continue
        else:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                flush_prev()
                in_fence = True
                fence_char = m.group(2)[0]
                fence_len = len(m.group(2))
                out.append(line)
                continue

        # Resolve any buffered Setext candidate with current line
        if prev_line is not None:
            if _SETEXT_RE.match(line):
                cleaned = _UNWRAP_RE.sub(r'\1', prev_line)
                cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned).rstrip() + '\n'
                out.append(cleaned)
                out.append(line)
                prev_line = None
                continue
            else:
                flush_prev()

        # ATX: unwrap inline
        if _ATX_RE.match(line):
            cleaned = _UNWRAP_RE.sub(r'\1', line)
            cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned).rstrip() + '\n'
            out.append(cleaned)
            continue

        # Potential Setext title line (buffer and inspect next line)
        if line.strip() and not line.lstrip().startswith('#') and not _FENCE_OPEN_RE.match(line):
            prev_line = line
            continue

        out.append(line)

    if prev_line is not None:
        out.append(prev_line)

    return ''.join(out)

