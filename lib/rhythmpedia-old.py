
#| output: asis
import re
import os

def extract_slug_and_title(header_line: str):
    match = re.match(r'^(#{2,6})\s+(.*?)\s*(?:\{#([^\}]+)\})?\s*$', header_line)
    if not match:
        return None

    level = len(match.group(1))
    raw_title = match.group(2).strip()
    explicit_slug = match.group(3)

    display_title = re.sub(r'<.*?>', '', raw_title).strip()

    if explicit_slug:
        slug = explicit_slug
    else:
        ruby_match = re.search(r'<ruby>([^<]+)</ruby>', raw_title)
        if ruby_match:
            slug = ruby_match.group(1)
        else:
            slug = re.sub(r'\s+', '-', display_title)
            slug = re.sub(r'[：・()（）［］「」、,.]', '', slug)
            slug = slug.strip('-')

    return level, display_title, slug


def extract_lang_id(input_md: str) -> str:
    """Extracts <lang-id> from 'master-<lang-id>.qmd'"""
    base = os.path.basename(input_md)
    match = re.match(r'master-([^.]+)\.qmd$', base)
    if not match:
        raise ValueError(f"Invalid input filename format: {input_md}")
    return match.group(1)


def create_toc_v2(input_md, link_target_md='.'):
    toc_lines = []
    current_top_slug = None
    lang_id = extract_lang_id( input_md )

    with open(input_md, encoding='utf-8') as f:
        for line in f:
            parsed = extract_slug_and_title(line)
            if not parsed:
                continue

            level, title, slug = parsed

            if level == 2:
                current_top_slug = slug
                link = f'{link_target_md}/{slug}/{lang_id}/'
            elif level > 2:
                if not current_top_slug:
                    continue
                link = f'{link_target_md}/{current_top_slug}/{lang_id}/#{slug}'
            else:
                continue

            indent = '  ' * (level - 2)
            toc_lines.append(f'{indent}- [{title}]({link})')

    print('\n'.join(toc_lines))

# ```{python}
# #| output: asis
# input_md    = "beat-orientation/master-ja.qmd"
# link_target_md  = "beat-orientation"
# create_toc_v2( input_md, link_target_md )
# ```
