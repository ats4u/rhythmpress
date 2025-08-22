import re
from typing import Iterable

_FENCE_OPEN_RE = re.compile(r'^(\s*)(`{3,}|~{3,})')      # ``` or ~~~ (len ≥ 3), any info string allowed
_ATX_RE        = re.compile(r'^\s{0,3}#{1,6}\s+')        # #..###### + space
_SETEXT_RE     = re.compile(r'^\s{0,3}(=+|-+)\s*$')      # ===... or ---...
_COMMENT_RE    = re.compile(r'<!--.*?-->', re.DOTALL)    # HTML comments (non-greedy)

def strip_header_comments(text: str) -> str:
    """
    Remove HTML comments ONLY from Markdown headers, returning the transformed text.

    Rules:
      - Strip comments in ATX headers (`# ...`) and Setext headers (title line + underline).
      - Do NOT touch anything inside fenced code blocks (``` / ~~~).
      - Pass YAML front matter at the very top through untouched (--- ... --- or ...).
      - Leave all other comments unchanged.

    Parameters
    ----------
    text : str
        Input Markdown.

    Returns
    -------
    str
        Output Markdown with header-only comments removed.
    """
    lines = text.splitlines(keepends=True)

    out: list[str] = []
    in_fence = False
    fence_char = None
    fence_len = 0

    in_front_matter = False
    at_file_start = True

    prev_line: str | None = None  # buffer to detect Setext header

    def flush_prev():
        nonlocal prev_line
        if prev_line is not None:
            out.append(prev_line)
            prev_line = None

    for line in lines:
        # Detect YAML front matter only at the very start
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

        # Inside a fenced code block → pass through until fence closes
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
            # Maybe entering a fenced code block
            m = _FENCE_OPEN_RE.match(line)
            if m:
                flush_prev()  # any buffered Setext candidate must be emitted before entering a fence
                in_fence = True
                fence_char = m.group(2)[0]
                fence_len = len(m.group(2))
                out.append(line)
                continue

        # If we buffered a potential Setext title line, decide based on current line
        if prev_line is not None:
            if _SETEXT_RE.match(line):
                cleaned = _COMMENT_RE.sub('', prev_line).rstrip() + '\n'
                out.append(cleaned)
                out.append(line)
                prev_line = None
                continue
            else:
                flush_prev()

        # ATX headers: strip comments inline
        if _ATX_RE.match(line):
            cleaned = _COMMENT_RE.sub('', line).rstrip() + '\n'
            out.append(cleaned)
            continue

        # Potential Setext header text line: buffer to check next line for ===/---
        if line.strip() and not line.lstrip().startswith('#') and not _FENCE_OPEN_RE.match(line):
            prev_line = line
            continue

        # Everything else (including blank lines)
        out.append(line)

    # End of file: flush leftover buffered line (not a Setext header)
    if prev_line is not None:
        out.append(prev_line)

    return ''.join(out)

